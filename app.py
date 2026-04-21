import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Modo AI Agent", page_icon="🤖")
st.title("🤖 موظف مودو الذكي")

api_key = st.sidebar.text_input("أدخل Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    user_query = st.chat_input("بماذا تأمر الموظف اليوم؟")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
        with st.chat_message("assistant"):
            st.write("⏳ جاري تشغيل المتصفح المحترف...")
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            # تحديد مسار الكروم في السيرفر
            options.binary_location = "/usr/bin/chromium"
            
            try:
                # تشغيل المتصفح مباشرة من نظام السيرفر
                driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                
                res = model.generate_content(f"User wants: {user_query}. Return ONLY the URL.")
                url = res.text.strip()
                
                driver.get(url)
                st.write(f"✅ نجحت! دخلت موقع: {url}")
                st.write(f"📄 العنوان: {driver.title}")
                driver.quit()
            except Exception as e:
                st.error(f"لسه فيه مشكلة: {e}")
else:
    st.info("حط الـ API Key عشان نبدأ.")
