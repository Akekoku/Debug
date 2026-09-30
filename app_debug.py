import streamlit as st
import requests
import base64
import json
import io
import socket
from PIL import Image

st.set_page_config(page_title="API Debugger", page_icon="🛠️", layout="wide")
st.title("🛠️ API Debugger: Groq & GitHub Deep Test")
st.markdown("ใช้ทดสอบยิง API และวินิจฉัยเครือข่ายลึก (DNS / Routing)")

# 1. API Keys
st.subheader("🔑 1. API Keys")
c_k1, c_k2 = st.columns(2)
with c_k1:
    groq_key = st.text_input("GROQ_API_KEY", type="password", placeholder="gsk_...")
with c_k2:
    github_key = st.text_input("GITHUB_TOKEN", type="password", placeholder="ghp_... หรือ github_pat_...")

# ฟังก์ชันดึง Groq Models
@st.cache_data(ttl=3600)
def get_groq_models(api_key):
    if not api_key:
        return ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json().get("data", [])
            blocked_words = ["guard", "whisper", "orpheus", "allam", "safeguard", "embedding"]
            valid_models = []
            for model in data:
                model_id = model["id"].lower()
                if not any(bad in model_id for bad in blocked_words):
                    valid_models.append(model["id"])
            return sorted(valid_models)
    except:
        pass
    return ["qwen/qwen3.8-27b", "llama-3.3-70b-versatile"]

# 2. ข้อมูลทดสอบ
st.subheader("📝 2. ข้อมูลทดสอบ")
available_groq_models = get_groq_models(groq_key)
default_idx = available_groq_models.index("qwen/qwen3.8-27b") if "qwen/qwen3.8-27b" in available_groq_models else 0
selected_groq_model = st.selectbox("🧠 เลือกรุ่น Groq", available_groq_models, index=default_idx)

prompt_text = st.text_area("ข้อความ (Prompt)", value="สวัสดี อธิบายสั้นๆ หน่อยว่าคุณคือใคร")
uploaded_file = st.file_uploader("อัปโหลดรูปภาพ (ไม่บังคับ)", type=["png", "jpg", "jpeg"])

def get_base64_image(file):
    img = Image.open(file)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((512, 512))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=80)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

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

# 3. โซนทดสอบ
st.subheader("🚀 3. ทดสอบยิง API")
col1, col2 = st.columns(2)

with col1:
    if st.button("ทดสอบ Groq", use_container_width=True):
        if not groq_key:
            st.warning("กรุณาใส่ GROQ_API_KEY")
        else:
            with st.spinner(f"กำลังยิง Groq ({selected_groq_model})..."):
                headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
                content_list = [{"type": "text", "text": prompt_text}]
                if uploaded_file:
                    b64 = get_base64_image(uploaded_file)
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    })
                payload = {
                    "model": selected_groq_model,
                    "messages": [{"role": "user", "content": content_list}],
                    "max_tokens": 500
                }
                try:
                    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=20)
                    display_results(payload, res)
                except Exception as e:
                    st.error(f"Connection Error: {e}")

with col2:
    github_endpoint = st.selectbox(
        "🌐 เลือก Endpoint สำหรับ GitHub Model",
        [
            "https://models.inference.ai.azure.com/chat/completions",
            "https://models.github.ai/inference/chat/completions"
        ]
    )
    
    col_gh_btn, col_gh_net = st.columns([1, 1])
    
    with col_gh_net:
        if st.button("🔍 ทดสอบเน็ต/DNS (Ping Domain)", use_container_width=True):
            domain = github_endpoint.split("/")[2]
            st.write(f"กำลังทดสอบ Resolve domain: `{domain}`")
            try:
                ip = socket.gethostbyname(domain)
                st.success(f"✅ DNS Resolve สำเร็จ! IP: `{ip}`")
            except Exception as net_err:
                st.error(f"❌ DNS Lookup ล้มเหลว: {net_err}")

    with col_gh_btn:
        if st.button("ทดสอบ GitHub Model", use_container_width=True, type="primary"):
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
                        res = requests.post(github_endpoint, headers=headers, json=payload, timeout=20)
                        display_results(payload, res)
                    except Exception as e:
                        st.error(f"Connection Error: {e}")
