import streamlit as st
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="IG Artist Dashboard", layout="centered")
st.title("📱 IG Profile Insights")

# ดึง Key จาก Secrets เพื่อความปลอดภัย (ไม่ต้องกรอกเองในหน้าเว็บ)
API_KEY = st.secrets.get("RAPIDAPI_KEY", "")
API_HOST = "instagram-scraper-stable-api.p.rapidapi.com"
ENDPOINT_URL = "https://instagram-scraper-stable-api.p.rapidapi.com/ig_get_fb_profile_hover.php"

# --- SIDEBAR ---
st.sidebar.header("Settings")
target_user = st.sidebar.text_input("IG Username (เช่น aespa_official)", value="aespa_official")
st.sidebar.divider()
st.sidebar.info(f"💡 Daily Quota: 10 requests\n⏱️ Rate Limit: 3/min")

# --- DATA FETCHING ---
@st.cache_data(ttl=86400) # จำข้อมูลไว้ 24 ชม. เพื่อประหยัดโควตา 10 ครั้ง/วัน
def fetch_ig_data(username):
    if not API_KEY:
        return None, "กรุณาตั้งค่า RAPIDAPI_KEY ใน Secrets"
    
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    # ต้องใช้ parameter 'username_or_url' เท่านั้นสำหรับเมนู User About
    params = {"username_or_url": username} 
    
    try:
        # ใช้เมธอด GET ตามที่ระบุในเมนู User About
        response = requests.get(ENDPOINT_URL, headers=headers, params=params, timeout=10)
        return response, None
    except Exception as e:
        return None, str(e)

# --- MAIN DISPLAY ---
if st.sidebar.button("🚀 ดึงข้อมูลล่าสุด"):
    st.cache_data.clear()
    st.rerun()

if API_KEY:
    with st.spinner("กำลังเชื่อมต่อกับ Instagram..."):
        response, error = fetch_ig_data(target_user)
        
        if error:
            st.error(f"เกิดข้อผิดพลาด: {error}")
        elif response.status_code == 200:
            data = response.json()
            st.success("🎉 อัปเดตข้อมูลสำเร็จ")
            
            # เจาะหาข้อมูลใน JSON (โครงสร้างอาจเปลี่ยนตาม API)
            # ส่วนใหญ่อยู่ใน data -> user หรือแสดงที่ระดับบนสุด
            user_info = data.get('data', {})
            
            if user_info:
                # แสดงผลด้วย Metric Card ให้สวยงาม
                col1, col2 = st.columns(2)
                col1.metric("Followers", f"{user_info.get('follower_count', 0):,}")
                col2.metric("Total Posts", f"{user_info.get('media_count', 0):,}")
                
                with st.expander("ดูข้อมูลดิบ (JSON)"):
                    st.json(data)
            else:
                st.warning("ดึงข้อมูลได้สำเร็จ แต่ไม่พบข้อมูลผู้ใช้")
                st.json(data)
        elif response.status_code == 429:
            st.error("Too Many Requests: คุณเรียกข้อมูลเกิน 3 ครั้งต่อนาที โปรดรอสักครู่")
        else:
            st.error(f"Error {response.status_code}: {response.text}")
else:
    st.warning("⚠️ ตรวจไม่พบ API Key ในระบบ Secrets กรุณาตั้งค่าก่อนใช้งาน")
