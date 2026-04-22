import streamlit as st
import json
import google.generativeai as genai
from playwright.sync_api import sync_playwright
import os

# تثبيت المتصفح داخل بيئة السيرفر أوتوماتيكياً
os.system("playwright install chromium")

st.set_page_config(page_title="Modo AI Playwright", page_icon="🤖")
st.title("🤖 الموظف الذكي (نسخة الـ Scraper المحترف)")

# ضع الـ API Key الخاص بك هنا بين القوسين
api_key = st.sidebar.text_input("Gemini API Key", value="AIzaSyDMleQuDuJFdQOBlCUpzW82_Q_VDrRZn2E", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # اختيار الموديل المستقر لضمان كوتا أكبر
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.sidebar.success("الموظف متصل وجاهز!")

        user_command = st.text_area("اكتب طلبك يا مودو:")

        def plan_with_ai(command):
            prompt = f"""
            You are a web automation planner. Convert this request: '{command}' into JSON steps.
            Actions: open (url), click (selector), type (selector, text), extract (selector), wait (seconds).
            Rules: Return ONLY JSON. Use direct URLs for searching if possible.
            Example: [{{ "action": "open", "url": "https://www.google.com" }}]
            """
            response = model.generate_content(prompt)
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            try:
                return json.loads(clean_json)
            except: return []

        def run_steps(steps):
            results = []
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                for step in steps:
                    action = step.get("action")
                    try:
                        if action == "open":
                            page.goto(step.get("url"), timeout=60000, wait_until="domcontentloaded")
                        elif action == "click":
                            page.click(step.get("selector"), timeout=5000)
                        elif action == "type":
                            page.fill(step.get("selector"), step.get("text"))
                        elif action == "wait":
                            page.wait_for_timeout(step.get("seconds", 2) * 1000)
                        elif action == "extract":
                            data = page.locator(step.get("selector")).all_text_contents()
                            results.extend(data)
                    except Exception as e:
                        results.append(f"Error at {action}: {str(e)[:50]}")
                browser.close()
            return results

        if st.button("تنفيذ المهمة 🚀"):
            if user_command:
                with st.status("🤖 جاري التخطيط والتنفيذ...") as s:
                    steps = plan_with_ai(user_command)
                    if steps:
                        st.write("📋 الخطة:", steps)
                        output = run_steps(steps)
                        st.success("✅ تم سحب البيانات:")
                        st.write(output)
                        
                        # تلخيص البيانات النهائية
                        context_text = " ".join(output)
                        summary_prompt = f"بناءً على البيانات المستخرجة: {context_text[:2500]}، جاوب بدقة على طلب مودو: {user_command}. الرد بالعربي."
                        final_res = model.generate_content(summary_prompt)
                        st.markdown("### 💬 الرد النهائي:")
                        st.info(final_res.text)
                    else:
                        st.error("فشل الموظف في فهم الخطوات، حاول توضيح الطلب.")
    except Exception as e:
        st.error(f"مشكلة تقنية: {e}")
else:
    st.info("أدخل الـ API Key في القائمة الجانبية.")
