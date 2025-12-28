import streamlit as st
from google import genai
import time

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="MediBot AI",
    page_icon="🧬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS GIAO DIỆN (MOBILE + DARK MODE) ---
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(147deg, #000000 0%, #041016 74%);
        color: #ffffff !important;
    }
    .stMarkdown, p, h1, h2, h3, li, span, div {
        color: #e0e0e0 !important;
    }
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #0b3d91;
        border-radius: 20px 20px 5px 20px;
        border: 1px solid #1e5bbd;
    }
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px 20px 20px 5px;
    }
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border-radius: 25px !important;
        border: 1px solid #333 !important;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. XỬ LÝ API KEY ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except: pass

if not api_key:
    with st.expander("🔐 Cài đặt API Key"):
        raw_key = st.text_input("Dán Key Google vào đây:", type="password")
        if raw_key: api_key = raw_key.strip()

# --- 4. MASTER PROMPT (3 IN 1) ---
master_prompt = """
Bạn là MediBot - Trợ lý Y tế AI.
Nhiệm vụ: Tự động phân tích câu hỏi và đóng vai:
1. [CẤP CỨU]: Bác sĩ Quân y. Khẩn trương, ngắn gọn. Cảnh báo gọi 115.
2. [DINH DƯỠNG]: Chuyên gia Dinh dưỡng. Tính calo, khoa học.
3. [TÂM LÝ]: Chuyên gia Tâm lý. Lắng nghe, nhẹ nhàng, chia sẻ.
QUY TẮC: Luôn trả lời Tiếng Việt. Trình bày đẹp.
"""

# --- 5. LOGIC CHAT ---
st.title("🧬 MediBot AI")
st.caption("Sơ cứu • Dinh dưỡng • Tâm lý")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì cho sức khỏe của bạn?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    if not api_key:
        st.toast("⚠️ Thiếu API Key!")
        st.stop()
        
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        place = st.empty()
        full_text = ""
        
        try:
            client = genai.Client(api_key=api_key)
            final_prompt = f"SYSTEM: {master_prompt}\nUSER: {prompt}"
            
            # [FIX QUAN TRỌNG]: Dùng model 1.5-flash để không bị giới hạn
            response = client.models.generate_content_stream(
                model="gemini-1.5-flash", 
                contents=final_prompt
            )

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    place.markdown(full_text + "█")
            
            place.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            # Tự động xử lý nếu vẫn bị lỗi rate limit
            if "429" in str(e):
                st.error("⏳ Đang quá tải. Vui lòng đợi 5 giây...")
                time.sleep(5) # Tự động chờ
                st.rerun()    # Tự động thử lại
            else:
                st.error(f"Lỗi: {e}")
