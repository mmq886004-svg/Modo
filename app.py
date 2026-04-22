import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Modo AI Agent", page_icon="🤖")
st.title("🤖 موظف مودو الذكي")

api_key = st.sidebar.text_input("أدخل Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model_name = next((m for m in available_models if "flash" in m), available_models[0])
        model = genai.GenerativeModel(model_name)
        st.sidebar.success(f"متصل بـ: {model_name}")

        user_query = st.chat_input("بماذا تأمر الموظف اليوم يا مودو؟")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                status = st.empty()
                status.write("⏳ الموظف بيتحرك بحذر لتجنب الحظر...")
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                # --- التمويه هنا ---
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                    
                    # طلب الرابط من جيمناي
                    prompt_url = f"Give me ONLY a direct Wikipedia or News URL to answer: {user_query}. No Google search links."
                    res_url = model.generate_content(prompt_url)
                    url = res_url.text.strip().split('\n')[0]
                    
                    if "http" not in url:
                        url = f"https://ar.wikipedia.org/wiki/{url.replace(' ', '_')}"
                    
                    status.write(f"🌐 بدخل موقع: {url}...")
                    driver.get(url)
                    time.sleep(2) # انتظار بسيط عشان الموقع يحمل
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # سحب النصوص المهمة فقط (البرجرافات)
                    paragraphs = soup.find_all('p')
                    page_text = " ".join([p.get_text() for p in paragraphs[:5]]) # أول 5 برجرافات
                    
                    if len(page_text) < 50: # لو الموقع فاضي أو حظرنا
                        st.warning("⚠️ الموقع ده محمي أو طلب CAPTCHA، هحاول بطريقة تانية...")
                        driver.quit()
                    else:
                        summary_prompt = f"لخص المعلومات دي بالعربي عشان تجاوب مودو: {page_text}"
                        final_res = model.generate_content(summary_prompt)
                        st.markdown(f"### 📄 الرد:\n{final_res.text}")
                        driver.quit()
                except Exception as e:
                    st.error(f"مشكلة تقنية: {e}")
    except Exception as e:
        st.error(f"مشكلة في الـ API: {e}")
else:
    st.info("حط الـ API Key يا مودو.")
