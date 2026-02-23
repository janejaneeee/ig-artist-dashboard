import streamlit as st
import instaloader
import pandas as pd
import plotly.express as px
from datetime import datetime

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="IG Artist Engagement Dashboard", layout="wide")

st.title("🎨 Artist Instagram Engagement Dashboard")
st.markdown("แสดงข้อมูล Engagement แบบ Real-time (On-demand)")

# --- Sidebar สำหรับตั้งค่า ---
st.sidebar.header("Settings")
target_user = st.sidebar.text_input("Instagram Username", value="aespa_official")
num_posts = st.sidebar.slider("Number of posts to analyze", 5, 20, 10)

# --- ฟังก์ชันดึงข้อมูล (พร้อมระบบ Cache 10 นาที เพื่อกันโดนแบน) ---
@st.cache_data(ttl=600) 
def fetch_ig_data(username, count):
    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        
        posts_list = []
        for i, post in enumerate(profile.get_posts()):
            if i >= count:
                break
            posts_list.append({
                "Date": post.date_local,
                "Likes": post.likes,
                "Comments": post.comments,
                "Engagement": post.likes + post.comments,
                "Shortcode": post.shortcode
            })
        
        return {
            "full_name": profile.full_name,
            "followers": profile.followers,
            "following": profile.followees,
            "posts_count": profile.mediacount,
            "data": pd.DataFrame(posts_list)
        }
    except Exception as e:
        return e

# --- ส่วนแสดงผลบน Dashboard ---
if st.button('🔄 Update Data'):
    st.cache_data.clear() # ล้าง Cache เพื่อดึงข้อมูลใหม่ทันที

with st.spinner('กำลังดึงข้อมูลจาก Instagram...'):
    result = fetch_ig_data(target_user, num_posts)

    if isinstance(result, Exception):
        st.error(f"เกิดข้อผิดพลาด: {result}")
        st.info("คำแนะนำ: อาจเกิดจาก Rate Limit ของ IG ให้รอสักครู่แล้วค่อยลองใหม่ครับ")
    else:
        # 1. แสดงตัวเลขหลัก (Metrics)
        col1, col2, col3, col4 = st.columns(4)
        avg_eng = result['data']['Engagement'].mean()
        er_rate = (avg_eng / result['followers']) * 100

        col1.metric("Followers", f"{result['followers']:,}")
        col2.metric("Following", f"{result['following']:,}")
        col3.metric("Avg. Engagement", f"{avg_eng:,.0f}")
        col4.metric("Engagement Rate", f"{er_rate:.2f}%")

        st.divider()

        # 2. กราฟแสดงแนวโน้ม
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("📈 Engagement Trend (Recent Posts)")
            fig = px.line(result['data'], x="Date", y="Engagement", 
                         hover_data=["Likes", "Comments"],
                         markers=True, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("📊 Data Table")
            st.dataframe(result['data'][["Date", "Engagement"]], use_container_width=True)

        # 3. สูตรการคำนวณ (LaTeX)
        st.info(f"สูตรการคำนวณ: $$Engagement Rate = \\frac{avg\_engagement}{total\_followers} \\times 100$$")
