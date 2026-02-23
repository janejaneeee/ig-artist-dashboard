import streamlit as st
import requests

# 1. ตั้งค่าหน้าเว็บให้ดูสะอาดตา
st.set_page_config(page_title="Artist Basic Stats", layout="centered")
st.title("📱 Artist Profile Stats")

# 2. ส่วนตั้งค่าที่ Sidebar
api_key = st.sidebar.text_input("ใส่ RapidAPI Key", type="password")
target_user = st.sidebar.text_input("IG Username", value="aespa_official")

# 3. ฟังก์ชันดึงข้อมูล (จำค่าไว้ 24 ชม. เพื่อประหยัดโควตา 50 ครั้ง/เดือน)
@st.cache_data(ttl=86400)
def get_profile_data(username, key):
    # ใช้ Endpoint ตัวหลักสำหรับข้อมูลโปรไฟล์
    url = "https://instagram-scraper-stable-api.p.rapidapi.com/ig_get_fb_profile.php"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "instagram-scraper-stable-api.p.rapidapi.com"
    }
    querystring = {"username": username}
    
    # ใช้ไลบรารี requests ตามมาตรฐานของ API เจ้านี้
    response = requests.get(url, headers=headers, params=querystring)
    return response

# 4. ส่วนการแสดงผลบนหน้าจอ
if st.sidebar.button("อัปเดตข้อมูล"):
    st.cache_data.clear()
    st.rerun()

if api_key:
    with st.spinner("กำลังดึงข้อมูลจาก Instagram..."):
        response = get_profile_data(target_user, api_key)
        
        if response.status_code == 200:
            res_data = response.json()
            
            # ตรวจสอบโครงสร้างข้อมูล (JSON) ที่ได้มา
            # หมายเหตุ: โครงสร้างข้อมูลอาจเปลี่ยนไปตามเวอร์ชันของ API
            if "data" in res_data and "user" in res_data["data"]:
                user = res_data["data"]["user"]
                
                st.header(f"✨ {user.get('full_name', target_user)}")
                st.caption(f"ID: {user.get('id', '-')}")
                
                # แสดงผลด้วย Metric Card (ดูง่ายและสวย)
                col1, col2, col3 = st.columns(3)
                col1.metric("Followers", f"{user.get('follower_count', 0):,}")
                col2.metric("Following", f"{user.get('following_count', 0):,}")
                col3.metric("Posts", f"{user.get('media_count', 0):,}")
                
                st.divider()
                st.subheader("💡 คำอธิบายโปรไฟล์ (Bio)")
                st.write(user.get("biography", "ไม่มีข้อมูลคำอธิบาย"))
                
            else:
                st.warning("ดึงข้อมูลสำเร็จ แต่โครงสร้างข้อมูลไม่ตรงกับที่คาดไว้")
                st.write("ลองดูข้อมูลดิบที่ได้:")
                st.json(res_data) # โชว์ JSON ทั้งหมดเพื่อเช็กชื่อตัวแปร
        else:
            st.error(f"เกิดข้อผิดพลาด (Code: {response.status_code})")
            st.write(response.text)
else:
    st.info("กรุณาใส่ RapidAPI Key ในแถบด้านข้างเพื่อเริ่มต้นครับ")
