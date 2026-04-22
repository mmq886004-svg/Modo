import streamlit as st
import json
import google.generativeai as genai
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Modo AI Playwright", page_icon="🤖")
st.title("🤖 الموظف الذكي (نسخة الـ Scraper المحترف)")

api_key = st.sidebar.text_input("Gemini API Key", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # --- خطوة البحث التلقائي عن الموديل المتاح عشان نتفادى الـ 404 ---
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models:
            st.error("الـ API Key ده مش لاقي موديلات شغالة.")
        else:
            model_name = next((m for m in available_models if "flash" in m), available_models[0])
            model = genai.GenerativeModel(model_name)
            st.sidebar.success(f"متصل بـ: {model_name}")

            user_command = st.text_area("اكتب طلبك (مثلاً: ادخل على Google وهات مواعيد ماتشات برشلونة):")

            def plan_with_ai(command):
                prompt = f"""
                You are a web automation planner. Convert this request: '{command}' into JSON steps.
                Actions: open (url), click (selector), type (selector, text), extract (selector), wait (seconds).
                Output ONLY JSON.
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
                                page.goto(step.get("url"), timeout=60000)
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
                    with st.status("🤖 الموظف بيخطط وينفذ...") as s:
                        steps = plan_with_ai(user_command)
                        if steps:
                            st.write("الخطة المتبعة:", steps)
                            output = run_steps(steps)
                            st.success("✅ النتائج اللي اتسحبت:")
                            st.write(output)
                        else:
                            st.error("فشل في تحليل الطلب")
    except Exception as e:
        st.error(f"مشكلة في الـ API: {e}")
else:
    st.info("حط الـ API Key يا مودو")
