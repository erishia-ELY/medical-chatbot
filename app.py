import streamlit as st
from google import genai

# --- 1. CẤU HÌNH TRANG (MOBILE FIRST) ---
st.set_page_config(
    page_title="MediBot AI",
    page_icon="🧬",
    layout="centered", # Dùng centered để gom gọn trên điện thoại
    initial_sidebar_state="collapsed" # Ẩn sidebar cho rộng chỗ
)

# --- 2. CSS FIX LỖI HIỂN THỊ (QUAN TRỌNG) ---
st.markdown("""
<style>
    /* 1. Nền tối Deep Blue dễ chịu cho mắt */
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(147deg, #000000 0%, #041016 74%);
        color: #ffffff !important; /* Bắt buộc chữ màu trắng */
    }

    /* 2. Fix lỗi chữ bị đen trên điện thoại */
    p, h1, h2, h3, li, span, div {
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

# Nếu không có key trong secrets, hiện ô nhập nhỏ gọn
if not api_key:
    with st.expander("🔐 Nhập API Key (Nếu chưa cài đặt)"):
        raw_key = st.text_input("Dán Key Google vào đây:", type="password")
        if raw_key: api_key = raw_key.strip()

# --- 4. SIÊU CÂU LỆNH (MASTER PROMPT) ---
# Đây là "bộ não" giúp bot tự biến hình
master_prompt = """
Bạn là MediBot - Trợ lý Y tế AI Thông minh 3 trong 1.
Nhiệm vụ: Tự động phân tích câu hỏi của người dùng và đóng vai phù hợp nhất:

1. [TRƯỜNG HỢP KHẨN CẤP/CHẤN THƯƠNG]:
   - Vai trò: Bác sĩ Quân y Cấp cứu.
   - Phong cách: Khẩn trương, ngắn gọn, súc tích.
   - Hành động: Hướng dẫn sơ cứu từng bước. Cảnh báo gọi 115 ngay nếu nguy hiểm.

2. [DINH DƯỠNG/THỰC PHẨM/TẬP LUYỆN]:
   - Vai trò: Chuyên gia Dinh dưỡng & PT.
   - Phong cách: Khoa học, khuyến khích, chi tiết.
   - Hành động: Tính calo, phân tích macro, gợi ý thực đơn.

3. [TÂM LÝ/CẢM XÚC/STRESS]:
   - Vai trò: Chuyên gia Tâm lý trị liệu.
   - Phong cách: Nhẹ nhàng, thấu cảm, sâu sắc.
   - Hành động: Lắng nghe, không phán xét, đưa lời khuyên xoa dịu.

4. [CÂU HỎI KHÁC]:
   - Trả lời thân thiện như một trợ lý y tế đa năng.

QUY TẮC: Luôn trả lời bằng Tiếng Việt. Trình bày đẹp mắt (dùng gạch đầu dòng, in đậm).
"""

# --- 5. GIAO DIỆN CHÍNH ---
st.title("🧬 MediBot AI")
st.caption("Sơ cứu • Dinh dưỡng • Tâm lý (Tự động nhận diện)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì cho sức khỏe của bạn hôm nay?"}]

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Xử lý Chat
if prompt := st.chat_input("Bạn đang cảm thấy thế nào?"):
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
            # Lưu ý: Ta ghép prompt hệ thống vào mỗi lần gọi để bot không quên vai
            final_prompt = f"SYSTEM INSTRUCTION: {master_prompt}\nUSER QUERY: {prompt}"
            
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash", 
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
