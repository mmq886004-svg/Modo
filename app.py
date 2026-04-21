import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Modo AI Agent", page_icon="🤖")
st.title("🤖 موظف مودو الذكي")

# القائمة الجانبية
api_key = st.sidebar.text_input("أدخل Gemini API Key:", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # التعديل الجوهري هنا: نستخدم الموديل المستقر 
        model = genai.GenerativeModel('gemini-1.5-flash')

        user_query = st.chat_input("بماذا تأمر الموظف اليوم يا مودو؟")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                st.write("⏳ الموظف بيفكر وهيفتح المتصفح حالاً...")
                
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.binary_location = "/usr/bin/chromium"
                
                try:
                    driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=options)
                    
                    # طلب الرابط بوضوح تام
                    prompt = f"Target: {user_query}. Tasks: Find the most relevant URL. Rules: Return ONLY the URL, no text."
                    res = model.generate_content(prompt)
                    url = res.text.strip()
                    
                    # التأكد إن الرد رابط حقيقي
                    if not url.startswith("http"):
                        url = "https://www.google.com/search?q=" + url.replace(" ", "+")
                    
                    driver.get(url)
                    st.write(f"✅ دخلت الموقع بنجاح: {url}")
                    st.write(f"📄 عنوان الصفحة الحالية: {driver.title}")
                    
                    driver.quit()
                    st.success("المهمة تمت بنجاح!")
                except Exception as e:
                    st.error(f"مشكلة في تشغيل المتصفح: {e}")
    except Exception as e:
        st.error(f"مشكلة في الاتصال بـ Google AI: {e}")
else:
    st.info("يا مودو، حط الـ API Key في الجنب عشان الموظف يصحى من النوم!")
