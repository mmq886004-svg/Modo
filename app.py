import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Modo Super AI", page_icon="⚡")
st.title("🤖 موظف مودو السريع")

# الـ API Key بتاعك مدمج
api_key = st.sidebar.text_input("Gemini API Key", value="AIzaSyDMleQuDuJFdQOBlCUpzW82_Q_VDrRZn2E", type="password")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # تفعيل ميزة البحث من جوجل داخل الموديل مباشرة
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            tools=[{'google_search': {}}] 
        )

        user_query = st.chat_input("عايز تعرف أسعار إيه يا مودو؟")

        if user_query:
            with st.chat_message("user"):
                st.write(user_query)
            
            with st.chat_message("assistant"):
                with st.spinner("⏳ جاري البحث في الأسواق المصرية..."):
                    # الموديل هنا بيدخل يبحث في جوجل ويرد عليك بالأسعار الحقيقية
                    response = model.generate_content(user_query)
                    st.markdown(response.text)
                    
                    # إظهار المصادر اللي جاب منها الأسعار
                    if response.candidates[0].grounding_metadata.search_entry_point:
                        st.divider()
                        st.caption("المصادر المباشرة:")
                        st.html(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)

    except Exception as e:
        st.error(f"حصلت مشكلة بسيطة: {e}")
else:
    st.info("حط الـ API Key في الجنب.")
