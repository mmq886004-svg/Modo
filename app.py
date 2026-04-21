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
        # التغيير هنا: استخدمنا نسخة مستقرة ومؤكدة
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        user_query = st.chat_input("بماذا تأمر الموظف اليوم يا مودو؟")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                st.write("⏳ الموظف بيفكر وهيفتح المتصفح حالاً...")
                
                # إعدادات المتصفح للسيرفر
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                    
                    # طلب الرابط من جيمناي بوضوح
                    prompt = f"Extract only the main URL to find this: {user_query}. Return only the URL starting with http."
                    res = model.generate_content(prompt)
                    url = res.text.strip()
                    
                    driver.get(url)
                    st.write(f"✅ دخلت الموقع بنجاح: {url}")
                    st.write(f"📄 عنوان الصفحة: {driver.title}")
                    
                    driver.quit()
                    st.success("المهمة خلصت يا وحش!")
                except Exception as e:
                    st.error(f"مشكلة في المتصفح: {e}")
    except Exception as e:
        st.error(f"مشكلة في الـ API Key أو الموديل: {e}")
else:
    st.info("مستني الـ API Key بتاعك عشان أنزل الشغل!")
