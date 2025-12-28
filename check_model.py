import google.generativeai as genai
import os

# --- NHẬP KEY CỦA BẠN VÀO ĐÂY ĐỂ TEST ---
api_key = "AIzaSyDE9Z0usdQDdQueJhrH-Ns1dVKkI_rlbTw" 

try:
    genai.configure(api_key=api_key)
    print("Trying to connect to Google API...")
    print("-" * 30)
    
    # Liệt kê tất cả model
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ MODEL NAME: {m.name}")
            
except Exception as e:
    print(f"❌ ERROR: {e}")
