import streamlit as st
import instaloader
import pandas as pd
import plotly.express as px

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="IG Basic Dashboard", layout="wide")

st.title("📊 Instagram Basic Data")
st.write("ดึงข้อมูลพื้นฐานจาก Instagram (Public Data)")

# 2. ตั้งค่าการดึงข้อมูลใน Sidebar
target_user = st.sidebar.text_input("ใส่ชื่อ IG Artist", value="aespa_official")
num_posts = st.sidebar.slider("จำนวนโพสต์ที่ต้องการดู", 5, 20, 10)

# 3. ฟังก์ชันดึงข้อมูล (มีระบบกันโดนแบนชั่วคราว)
@st.cache_data(ttl=600)
def get_basic_data(username, count):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        posts_data = []
        for i, post in enumerate(profile.get_posts()):
            if i >= count:
                break
            posts_data.append({
                "Date": post.date_local,
                "Likes": post.likes,
                "Comments": post.comments,
                "Total": post.likes + post.comments,
                "URL": f"https://www.instagram.com/p/{post.shortcode}/"
            })
            
        return {
            "full_name": profile.full_name,
            "followers": profile.followers,
            "following": profile.followees,
            "df": pd.DataFrame(posts_data)
        }
    except Exception as e:
        return e

# 4. ส่วนแสดงผล
if st.sidebar.button('อัปเดตข้อมูล'):
    st.cache_data.clear()

with st.spinner('กำลังโหลด...'):
    result = get_basic_data(target_user, num_posts)

    if isinstance(result, Exception):
        st.error(f"พบข้อผิดพลาด: {result}")
        st.info("คำแนะนำ: หากขึ้น 429 หรือ 401 แสดงว่า IG บล็อก IP ของเซิร์ฟเวอร์ชั่วคราว ให้รอประมาณ 15 นาทีแล้วค่อยกดอัปเดตใหม่ครับ")
    else:
        # แสดงตัวเลขสรุป (Metrics)
        st.subheader(f"บัญชี: {result['full_name']} (@{target_user})")
        col1, col2, col3 = st.columns(3)
        col1.metric("ผู้ติดตาม (Followers)", f"{result['followers']:,}")
        col2.metric("กำลังติดตาม (Following)", f"{result['following']:,}")
        col3.metric("วิเคราะห์ล่าสุด (Posts)", len(result['df']))

        st.divider()

        # แสดงกราฟแท่งยอด Like ของแต่ละโพสต์
        st.subheader("📈 ยอด Like ของโพสต์ล่าสุด")
        fig = px.bar(result['df'], x="Date", y="Likes", 
                     hover_data=["Comments", "URL"],
                     title=f"Likes per Post for {target_user}")
        st.plotly_chart(fig, use_container_width=True)

        # แสดงตารางข้อมูลดิบ
        st.subheader("📋 ตารางข้อมูลโพสต์")
        st.dataframe(result['df'], use_container_width=True)
