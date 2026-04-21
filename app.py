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
        # استخدمنا نسخة برو المستقرة لضمان التشغيل
        model = genai.GenerativeModel('gemini-1.5-pro')

        user_query = st.chat_input("بماذا تأمر الموظف اليوم؟")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                st.write("⏳ جاري استدعاء المتصفح وتحليل الطلب...")
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                    
                    # طلب الرابط من الموديل بطريقة أكيدة
                    prompt = f"Give me ONLY the URL for this: {user_query}. No extra text."
                    res = model.generate_content(prompt)
                    url = res.text.strip()
                    
                    if "http" not in url:
                        url = f"https://www.google.com/search?q={url.replace(' ', '+')}"
                    
                    driver.get(url)
                    st.write(f"✅ تم الدخول بنجاح: {url}")
                    st.write(f"📄 عنوان الصفحة: {driver.title}")
                    driver.quit()
                except Exception as e:
                    st.error(f"عطل في المحرك: {e}")
    except Exception as e:
        st.error(f"عطل في الـ API: {e}")
else:
    st.info("حط الـ API Key في الجنب يا مودو.")
