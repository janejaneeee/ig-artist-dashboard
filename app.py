import streamlit as st
import requests

st.title("📱 IG Profile Stats (Endpoint Fix)")

# 1. รับค่าจาก Sidebar
api_key = st.sidebar.text_input("ใส่ RapidAPI Key", type="password")
# ให้คุณก๊อปปี้ URL จากหน้า RapidAPI มาแปะตรงนี้เลยครับ
api_url = st.sidebar.text_input("ใส่ Endpoint URL (เช่น https://.../ig_user_info.php)")
target_user = st.sidebar.text_input("IG Username", value="aespa_official")

# 2. ฟังก์ชันดึงข้อมูลแบบจำค่าไว้ 24 ชม.
@st.cache_data(ttl=86400)
def fetch_data(url, key, username):
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "instagram-scraper-stable-api.p.rapidapi.com"
    }
    querystring = {"username": username}
    # ใช้ requests ตามคำแนะนำของ API
    return requests.get(url, headers=headers, params=querystring)

# 3. แสดงผล
if st.sidebar.button("ดึงข้อมูล"):
    if api_key and api_url:
        with st.spinner("กำลังดึงข้อมูล..."):
            response = fetch_data(api_url, api_key, target_user)
            
            if response.status_code == 200:
                data = response.json()
                st.success("🎉 เชื่อมต่อสำเร็จ!")
                # โชว์ข้อมูลดิบทั้งหมดเพื่อหาชื่อตัวแปร Followers
                st.json(data) 
            else:
                st.error(f"Error {response.status_code}: {response.text}")
    else:
        st.warning("กรุณาใส่ทั้ง Key และ URL ให้ครบถ้วนครับ")
