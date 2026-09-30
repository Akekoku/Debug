import streamlit as st
import requests
import base64
import json
import io
from PIL import Image

st.set_page_config(page_title="API Debugger", page_icon="🛠️")
st.title("🛠️ API Debugger: Groq & GitHub")
st.markdown("ใช้ทดสอบยิง API ด้วยข้อความและรูปภาพ เพื่อดูโครงสร้างข้อมูล (Payload) และผลลัพธ์ดิบ (Raw Response)")

# 1. ใส่กุญแจตรงนี้ได้เลย (เพื่อความง่ายในการทดสอบ)
st.subheader("🔑 1. API Keys")
groq_key = st.text_input("GROQ_API_KEY", type="password", placeholder="gsk_...")
github_key = st.text_input("GITHUB_TOKEN", type="password", placeholder="ghp_...")

# 2. ใส่ข้อมูลทดสอบ
st.subheader("📝 2. ข้อมูลทดสอบ")
prompt_text = st.text_area("ข้อความ (Prompt)", value="อธิบายรูปภาพนี้ให้หน่อย")
uploaded_file = st.file_uploader("อัปโหลดรูปภาพ (1 รูป)", type=["png", "jpg", "jpeg"])

def get_base64_image(file):
    img = Image.open(file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((512, 512)) # บีบอัดให้เล็กเพื่อทดสอบ
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 3. เลือกค่ายและทดสอบ
st.subheader("🚀 3. ทดสอบยิง API")
col1, col2 = st.columns(2)

# ฟังก์ชันแสดงผลลัพธ์
def display_results(payload, response):
    st.markdown("### 📤 ข้อมูลที่ส่งไป (Request Payload)")
    st.json(payload)
    
    st.markdown("### 📥 ผลลัพธ์ที่ตอบกลับ (Response)")
    if response.status_code == 200:
        st.success(f"Status Code: {response.status_code} (สำเร็จ)")
        st.json(response.json())
    else:
        st.error(f"Status Code: {response.status_code} (ขัดข้อง)")
        try:
            st.json(response.json())
        except:
            st.text(response.text)

# --- ปุ่มทดสอบ Groq ---
with col1:
    if st.button("ทดสอบ Groq (Llama 3.2 Vision)", use_container_width=True):
        if not groq_key:
            st.warning("กรุณาใส่ GROQ_API_KEY")
        else:
            with st.spinner("กำลังยิง API ไปที่ Groq..."):
                headers = {
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                }
                
                # สร้าง Payload มาตรฐาน OpenAI
                content_list = [{"type": "text", "text": prompt_text}]
                if uploaded_file:
                    b64 = get_base64_image(uploaded_file)
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                
                payload = {
                    "model": "llama-3.2-90b-vision-preview",
                    "messages": [{"role": "user", "content": content_list}],
                    "max_tokens": 500
                }
                
                try:
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                    display_results(payload, res)
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --- ปุ่มทดสอบ GitHub ---
with col2:
    if st.button("ทดสอบ GitHub (GPT-4o-mini)", use_container_width=True):
        if not github_key:
            st.warning("กรุณาใส่ GITHUB_TOKEN")
        else:
            with st.spinner("กำลังยิง API ไปที่ GitHub..."):
                headers = {
                    "Authorization": f"Bearer {github_key}",
                    "Content-Type": "application/json"
                }
                
                content_list = [{"type": "text", "text": prompt_text}]
                if uploaded_file:
                    b64 = get_base64_image(uploaded_file)
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": content_list}],
                    "max_tokens": 500
                }
                
                try:
                    res = requests.post("https://models.inference.ai.azure.com/chat/completions", headers=headers, json=payload, timeout=20)
                    display_results(payload, res)
                except Exception as e:
                    st.error(f"Connection Error: {e}")
