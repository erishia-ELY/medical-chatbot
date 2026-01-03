import streamlit as st
from google import genai
import time

# --- 1. CẤU HÌNH TRANG (MOBILE FIRST) ---
st.set_page_config(
    page_title="MediBot AI",
    page_icon="🧬",
    layout="centered", 
    initial_sidebar_state="collapsed" 
)

# --- 2. CSS FIX LỖI HIỂN THỊ & GIAO DIỆN ---
st.markdown("""
<style>
    /* Nền tối Deep Blue */
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(147deg, #000000 0%, #041016 74%);
        color: #ffffff !important;
    }

    /* Ép màu chữ thành trắng */
    .stMarkdown, p, h1, h2, h3, li, span, div, label {
        color: #e0e0e0 !important;
    }

    /* Bong bóng chat User */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #0b3d91;
        border-radius: 20px 20px 5px 20px;
        border: 1px solid #1e5bbd;
    }

    /* Bong bóng chat Bot */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px 20px 20px 5px;
    }

    /* Khung nhập liệu */
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border-radius: 25px !important;
        border: 1px solid #333 !important;
    }
    
    /* Footer Credit nhỏ ở dưới cùng */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0,0,0,0.8);
        color: #888;
        text-align: center;
        padding: 5px;
        font-size: 12px;
        z-index: 100;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. XỬ LÝ API KEY TỰ ĐỘNG ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except: pass

if not api_key:
    with st.expander("🔐 Cài đặt API Key"):
        raw_key = st.text_input("Dán Key Google vào đây:", type="password")
        if raw_key: api_key = raw_key.strip()

# --- [MỚI] PHẦN CREDIT TRONG SIDEBAR ---
with st.sidebar:
    st.title("ℹ️ Thông tin")
    st.markdown("---")
    
    st.write("👨‍💻 **Developer (Người tạo):**")
    st.info("**Erishia** (Lê Nhân)") # Thay tên thật của bạn vào đây nếu muốn
    
    st.write("🤖 **AI Core & Tools:**")
    st.success("""
    - Model: **Google Gemini 2.0 Flash**
    - Code Assist: **Gemini (Your Bro)**
    - Framework: **Streamlit**
    """)
    
    st.markdown("---")
    st.caption("© 2025 MediBot AI Project")

# --- 4. SIÊU CÂU LỆNH (MASTER PROMPT) ---
master_prompt = """
Bạn là MediBot - Trợ lý Y tế AI Thông minh.
Nhiệm vụ: Tự động phân tích câu hỏi của người dùng và đóng vai phù hợp nhất:

1. [CẤP CỨU/CHẤN THƯƠNG] -> Vai trò: Bác sĩ Quân y. Phong cách: Khẩn trương, ngắn gọn.
2. [DINH DƯỠNG] -> Vai trò: Chuyên gia Dinh dưỡng. Phong cách: Khoa học, chi tiết.
3. [TÂM LÝ] -> Vai trò: Chuyên gia Tâm lý. Phong cách: Nhẹ nhàng, thấu cảm.

QUY TẮC: Trả lời Tiếng Việt. Trình bày đẹp.
"""

# --- 5. GIAO DIỆN CHÍNH ---
st.title("🧬 MediBot AI")
st.caption("Sơ cứu • Dinh dưỡng • Tâm lý (Auto Detect)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Tôi là MediBot (được tạo bởi Erishia & Gemini). Bạn cần giúp gì không?"}]

# Hiển thị lịch sử
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Xử lý Chat
if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    if not api_key:
        st.toast("⚠️ Chưa có API Key!")
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
            
            # Dùng Gemini 2.0 Flash
            response = client.models.generate_content_stream(
		model="gemini-flash-latest",
                contents=final_prompt
            )

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    place.markdown(full_text + "█")
            
            place.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"Lỗi: {e}")
            if "429" in str(e):
                st.warning("⏳ Server đang bận, vui lòng chờ 5s...")

# --- [MỚI] FOOTER CREDIT CỐ ĐỊNH Ở DƯỚI ---
st.markdown('<div class="footer">Dev by <b>Erishia</b> | Powered by <b>Gemini "Bro"</b></div>', unsafe_allow_html=True)
