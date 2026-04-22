import streamlit as st
import json
import google.generativeai as genai
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Modo AI Playwright", page_icon="🤖")
st.title("🤖 الموظف الذكي (نسخة الـ Scraper المحترف)")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    user_command = st.text_area("اكتب طلبك (مثلاً: ادخل على ويكيبيديا وهات عناوين h1):")

    def plan_with_ai(command):
        prompt = f"Convert this request into JSON steps: {command}. Actions: open, click, type, extract, wait. Output ONLY JSON."
        response = model.generate_content(prompt)
        # تنظيف الرد من أي علامات ماركداون
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        try:
            return json.loads(clean_json)
        except: return []

    def run_steps(steps):
        results = []
        with sync_playwright() as p:
            # تشغيل headless=True ضروري للسيرفر
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for step in steps:
                action = step.get("action")
                try:
                    if action == "open":
                        page.goto(step.get("url"), timeout=60000)
                    elif action == "click":
                        page.click(step.get("selector"), timeout=5000)
                    elif action == "type":
                        page.fill(step.get("selector"), step.get("text"))
                    elif action == "wait":
                        page.wait_for_timeout(step.get("seconds", 2) * 1000)
                    elif action == "extract":
                        # سحب النصوص بناءً على السليكتور
                        data = page.locator(step.get("selector")).all_text_contents()
                        results.extend(data)
                except Exception as e:
                    results.append(f"Error at {action}: {str(e)[:50]}")
            
            browser.close()
        return results

    if st.button("تنفيذ المهمة 🚀"):
        if user_command:
            st.info("🤖 الموظف بيفكر في الخطوات...")
            steps = plan_with_ai(user_command)
            if steps:
                st.json(steps)
                st.info("⚙️ جاري سحب البيانات بالكامل...")
                output = run_steps(steps)
                st.success("✅ البيانات اللي اتسحبت:")
                st.write(output)
            else: st.error("فشل في تحليل الطلب")
else:
    st.info("حط الـ API Key يا مودو")
