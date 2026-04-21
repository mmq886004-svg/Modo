import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Modo AI Agent", page_icon="🤖")
st.title("🤖 موظف مودو الذكي")

api_key = st.sidebar.text_input("أدخل Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- خطوة البحث التلقائي عن الموديل المتاح ---
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models:
            st.error("للأسف مفيش موديلات متاحة للـ API Key ده.")
        else:
            # هنختار أول موديل flash متاح، ولو مفيش نختار أول واحد في القائمة
            model_name = next((m for m in available_models if "flash" in m), available_models[0])
            model = genai.GenerativeModel(model_name)
            st.sidebar.success(f"متصل بـ: {model_name}")

            user_query = st.chat_input("بماذا تأمر الموظف اليوم يا مودو؟")

            if user_query:
                with st.chat_message("user"):
                    st.write(user_query)
                
                with st.chat_message("assistant"):
                    st.write("⏳ الموظف بيجهز المتصفح...")
                    
                    options = Options()
                    options.add_argument("--headless")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    options.binary_location = "/usr/bin/chromium"
                    
                    try:
                        driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                        
                        # طلب الرابط
                        prompt = f"Return ONLY the URL for: {user_query}. If not a URL, return a Google search link for it."
                        res = model.generate_content(prompt)
                        url = res.text.strip().split('\n')[0] # هناخد أول سطر بس
                        
                        if "http" not in url:
                            url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
                        
                        driver.get(url)
                        st.write(f"✅ دخلت الموقع: {url}")
                        st.write(f"📄 العنوان: {driver.title}")
                        driver.quit()
                    except Exception as e:
                        st.error(f"مشكلة في المحرك: {e}")
    except Exception as e:
        st.error(f"مشكلة في الاتصال: {e}")
else:
    st.info("مستني الـ API Key في القائمة الجانبية.")
