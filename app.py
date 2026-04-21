import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# إعداد واجهة البرنامج
st.set_page_config(page_title="Modo AI Agent", page_icon="🤖")
st.title("🤖 موظف مودو الذكي")

# مكان الـ API Key في القائمة الجانبية
api_key = st.sidebar.text_input("أدخل Gemini API Key:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    user_query = st.chat_input("بماذا تأمر الموظف اليوم يا مودو؟")

    if user_query:
        with st.chat_message("user"):
            st.write(user_query)

        with st.chat_message("assistant"):
            st.write("⏳ جاري تشغيل المحرك وتنفيذ المهمة...")
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                # تشغيل المتصفح على السيرفر
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                
                # جيمناي بيفكر في أفضل رابط
                prompt = f"User wants: {user_query}. Return ONLY the most relevant URL to find this information."
                res = model.generate_content(prompt)
                url = res.text.strip()
                
                driver.get(url)
                st.write(f"🌐 دخلت موقع: {url}")
                st.write(f"📄 عنوان الصفحة: {driver.title}")
                
                driver.quit()
                st.success("تمت المهمة بنجاح!")
            except Exception as e:
                st.error(f"حصلت مشكلة: {e}")
else:
    st.info("يا مودو، من فضلك حط الـ API Key في الجنب عشان الموظف يبدأ يشتغل.")
