import streamlit as st
from google import genai
import time

# --- 1. CẤU HÌNH TRANG (MOBILE FIRST) ---
st.set_page_config(
    page_title="MediBot AI",
    page_icon="🧬",
    layout="centered", # Dùng centered để gom gọn trên điện thoại
    initial_sidebar_state="collapsed" # Ẩn sidebar cho rộng chỗ
)

# --- 2. CSS FIX LỖI HIỂN THỊ TRÊN ĐIỆN THOẠI ---
st.markdown("""
<style>
    /* 1. Nền tối Deep Blue dễ chịu cho mắt */
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(147deg, #000000 0%, #041016 74%);
        color: #ffffff !important; /* Bắt buộc toàn bộ chữ phải màu trắng */
    }

    /* 2. Ép màu chữ trong khung chat thành trắng (Fix lỗi trên điện thoại) */
    .stMarkdown, p, h1, h2, h3, li, span, div {
        color: #e0e0e0 !important;
    }

    /* 3. Bong bóng chat User (Màu xanh nổi bật) */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background-color: #0b3d91;
        border-radius: 20px 20px 5px 20px;
        border: 1px solid #1e5bbd;
    }

    /* 4. Bong bóng chat Bot (Màu tối trong suốt, chữ sáng) */
    .stChatMessage[data-testid="stChatMessageAssistant"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px 20px 20px 5px;
    }

    /* 5. Khung nhập liệu (Nổi bật để dễ bấm) */
    .stTextInput input {
        background-color: #1a1a1a !important;
        color: #00ff41 !important;
        border-radius: 25px !important;
        border: 1px solid #333 !important;
    }
    
    /* 6. Ẩn bớt padding thừa trên mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. XỬ LÝ API KEY TỰ ĐỘNG ---
api_key = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except: pass

# Nếu không có key trong secrets, hiện ô nhập nhỏ gọn (ẩn trong Expander cho đỡ rối)
if not api_key:
    with st.expander("🔐 Cài đặt API Key"):
        raw_key = st.text_input("Dán Key Google vào đây:", type="password")
        if raw_key: api_key = raw_key.strip()

# --- 4. SIÊU CÂU LỆNH (MASTER PROMPT) - GỘP 3 TRONG 1 ---
# Đây là "bộ não" giúp bot tự biến hình
master_prompt = """
Bạn là MediBot - Trợ lý Y tế AI Thông minh.
Nhiệm vụ: Tự động phân tích câu hỏi của người dùng và đóng vai phù hợp nhất:

1. [NẾU LÀ CẤP CỨU/CHẤN THƯƠNG]:
   - Vai trò: Bác sĩ Quân y Cấp cứu.
   - Phong cách: Khẩn trương, ngắn gọn, súc tích.
   - Hành động: Hướng dẫn sơ cứu từng bước. Cảnh báo gọi 115 ngay.

2. [NẾU LÀ DINH DƯỠNG/THỰC PHẨM]:
   - Vai trò: Chuyên gia Dinh dưỡng.
   - Phong cách: Khoa học, chi tiết.
   - Hành động: Tính calo, phân tích macro, gợi ý thực đơn.

3. [NẾU LÀ TÂM LÝ/CẢM XÚC/TÌNH CẢM]:
   - Vai trò: Chuyên gia Tâm lý trị liệu.
   - Phong cách: Nhẹ nhàng, thấu cảm, "chữa lành".
   - Hành động: Lắng nghe, chia sẻ, không phán xét.

QUY TẮC: Luôn trả lời bằng Tiếng Việt. Trình bày đẹp mắt (dùng gạch đầu dòng, in đậm).
"""

# --- 5. GIAO DIỆN CHÍNH ---
st.title("🧬 MediBot AI")
st.caption("Sơ cứu • Dinh dưỡng • Tâm lý (Tự động nhận diện)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Tôi là trợ lý sức khỏe toàn năng. Bạn đang gặp vấn đề gì (đau ốm, ăn uống hay tâm lý)?"}]

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Xử lý Chat
if prompt := st.chat_input("Nhập câu hỏi tại đây..."):
    if not api_key:
        st.toast("⚠️ Chưa có API Key! Vui lòng nhập Key.")
        st.stop()
        
    # Hiện tin nhắn user
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Xử lý Bot
    with st.chat_message("assistant"):
        place = st.empty()
        full_text = ""
        
        try:
            client = genai.Client(api_key=api_key)
            
            # Gửi kèm Master Prompt để định hướng Bot
            final_prompt = f"SYSTEM INSTRUCTION: {master_prompt}\nUSER QUERY: {prompt}"
            
            # Sử dụng gemini-2.0-flash (bản ổn định hơn 2.5 một chút về limit)
            # Nếu vẫn lỗi 429, hãy đổi dòng dưới thành "gemini-1.5-flash"
            response = client.models.generate_content_stream(
                model="gemini-2.0-flash", 
                contents=final_prompt
            )

            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    place.markdown(full_text + "█")
            
            place.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"Lỗi kết nối: {e}")
            if "429" in str(e):
                st.warning("⏳ Hệ thống đang quá tải (Free Tier). Vui lòng chờ 5-10 giây rồi thử lại.")
