import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Artist Mockup Dashboard", layout="wide")
st.title("🎨 Artist Engagement Mockup (Stable API)")

# 1. ตั้งค่า API (แนะนำให้ใส่ใน Streamlit Secrets ภายหลัง)
API_KEY = st.sidebar.text_input("ใส่ RapidAPI Key", type="password")
API_HOST = "instagram-scraper-stable-api.p.rapidapi.com"
target_user = st.sidebar.text_input("IG Username", value="aespa_official")

# 2. ฟังก์ชันดึงข้อมูลแบบประหยัดโควตา (จำค่าไว้ 24 ชม.)
@st.cache_data(ttl=86400) 
def get_ig_data(username, key):
    url = "https://instagram-scraper-stable-api.p.rapidapi.com/user_info"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": API_HOST
    }
    querystring = {"username": username}
    
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

# 3. ส่วนแสดงผล
if API_KEY:
    if st.sidebar.button("ดึงข้อมูลใหม่ (ใช้โควตา)"):
        st.cache_data.clear()
        st.rerun()

    with st.spinner("กำลังติดต่อ API..."):
        res = get_ig_data(target_user, API_KEY)
        
        # ตรวจสอบว่า API ส่งข้อมูลมาถูกต้องไหม (ชื่อตัวแปรอาจปรับตาม JSON จริง)
        if "data" in res:
            user = res["data"]
            # แสดง Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Followers", f"{user.get('follower_count', 0):,}")
            c2.metric("Total Posts", f"{user.get('media_count', 0):,}")
            c3.metric("Quota Status", "Active")
            
            st.success(f"แสดงข้อมูลของ {user.get('full_name')} เรียบร้อย!")
            # ตรงนี้คุณสามารถเพิ่มโค้ดทำกราฟจากข้อมูลใน user['edge_owner_to_timeline_media'] ได้
        else:
            st.error("ไม่สามารถดึงข้อมูลได้ โปรดเช็ก API Key หรือ Username")
            st.json(res) # แสดง Error เพื่อใช้ Debug
else:
    st.info("กรุณาใส่ API Key ใน Sidebar เพื่อเริ่มต้นครับ")
