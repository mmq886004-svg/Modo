import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

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
                status.write("⏳ جاري البحث وفتح المتصفح...")
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                    
                    # خطوة 1: تحديد الرابط
                    prompt_url = f"Give me ONLY the best URL to answer this: {user_query}. Return only the URL."
                    res_url = model.generate_content(prompt_url)
                    url = res_url.text.strip().split('\n')[0]
                    
                    if "http" not in url:
                        url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
                    
                    # خطوة 2: دخول الموقع وسحب النص
                    driver.get(url)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    page_text = soup.get_text()[:2000] # هناخد أول 2000 حرف بس عشان السرعة
                    
                    # خطوة 3: تلخيص المحتوى
                    status.write(f"✅ دخلت موقع: {driver.title}.. جاري قراءة البيانات...")
                    summary_prompt = f"Based on this text from the website: {page_text}, answer the user query: {user_query}. Answer in Arabic."
                    final_res = model.generate_content(summary_prompt)
                    
                    st.markdown(f"### 📄 الرد المباشر:\n{final_res.text}")
                    st.caption(f"المصدر: {url}")
                    
                    driver.quit()
                except Exception as e:
                    st.error(f"مشكلة في القراءة: {e}")
    except Exception as e:
        st.error(f"مشكلة في الاتصال: {e}")
else:
    st.info("حط الـ API Key في الجنب عشان الموظف يبدأ الشغل!")
