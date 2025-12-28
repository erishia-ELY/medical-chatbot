import streamlit as st
from google import genai
import time

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="MediBot AI 2.5",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. SIÊU GIAO DIỆN CYBERPUNK ---
st.markdown("""
<style>
    /* Tổng thể: Nền tối hiện đại */
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: #ffffff;
    }
    
    /* Sidebar: Hiệu ứng kính mờ (Glassmorphism) */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Tiêu đề */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #00f260; /* Màu xanh y tế neon */
        text-shadow: 0 0 10px rgba(0, 242, 96, 0.5);
    }

    /* Input Chat: Trông như thanh command */
    .stTextInput input {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: #00f260 !important;
        border: 1px solid #00f260 !important;
        border-radius: 20px;
        padding: 10px;
    }

    /* Tin nhắn User */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px 20px 5px 20px;
        border: none;
    }

    /* Tin nhắn Bot */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(0, 242, 96, 0.3);
        border-radius: 20px 20px 20px 5px;
        color: #e0e0e0;
    }
    
    /* Nút bấm */
    .stButton button {
        background: linear-gradient(to right, #11998e, #38ef7d);
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR XỊN ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4128/4128362.png", width=100)
    st.title("🧬 MEDIBOT CONTROL")
    st.caption("System: Gemini 2.5 Flash | Status: Online")
    
    st.markdown("---")
    
    # Xử lý Key thông minh
    api_key = None
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Server Key Active")
    except: pass

    if not api_key:
        raw_key = st.text_input("🔑 Enter Access Key:", type="password")
        if raw_key: api_key = raw_key.strip()

    st.markdown("---")
    
    # Chọn chế độ với Icon đẹp
    mode = st.radio(
        "CHỌN CHUYÊN GIA:",
        ("🚑 Bác sĩ Cấp cứu", "🥦 Chuyên gia Dinh dưỡng", "🧠 Bác sĩ Tâm lý"),
        index=0
    )
    
    st.markdown("---")
    if st.button("🔄 Reset Memory"):
        st.session_state.messages = []
        st.rerun()

# --- 4. LOGIC HỆ THỐNG ---
sys_prompts = {
    "🚑 Bác sĩ Cấp cứu": "Bạn là bác sĩ quân y cấp cứu. Trả lời cực ngắn gọn, súc tích, tập trung vào hành động sơ cứu ngay lập tức. Luôn cảnh báo nếu cần gọi 115.",
    "🥦 Chuyên gia Dinh dưỡng": "Bạn là chuyên gia dinh dưỡng. Tính toán calo, macro, đưa ra thực đơn khoa học và dễ hiểu.",
    "🧠 Bác sĩ Tâm lý": "Bạn là chuyên gia tâm lý trị liệu. Lắng nghe thấu cảm, nói chuyện nhẹ nhàng, xoa dịu tinh thần người dùng."
}

# Avatar cho đẹp
avatars = {
    "user": "👤",
    "assistant": "🤖"
}
if mode == "🚑 Bác sĩ Cấp cứu": avatars["assistant"] = "🚑"
elif mode == "🥦 Chuyên gia Dinh dưỡng": avatars["assistant"] = "🥦"
elif mode == "🧠 Bác sĩ Tâm lý": avatars["assistant"] = "🧠"

st.subheader(f"{mode} đang trực tuyến...")

# Quản lý lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị tin nhắn
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatars.get(msg["role"])):
        st.markdown(msg["content"])

# Xử lý Chat
if prompt := st.chat_input("Nhập câu hỏi sức khỏe tại đây..."):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập API Key để kích hoạt hệ thống.")
        st.stop()
        
    with st.chat_message("user", avatar=avatars["user"]):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        place = st.empty()
        full_text = ""
        
        try:
            client = genai.Client(api_key=api_key)
            final_prompt = f"SYSTEM INSTRUCTION: {sys_prompts[mode]}\nUSER QUERY: {prompt}"
            
            # Gọi Gemini 2.5 Flash
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=final_prompt
            )

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    place.markdown(full_text + "▌") # Hiệu ứng con trỏ
            
            place.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"Lỗi kết nối vệ tinh: {e}")
