import streamlit as st
import requests

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="Artist Insights", layout="wide")

# ปรับ CSS เล็กน้อยให้รูปโปรไฟล์เป็นวงกลมและตัวเลขเด่นชัด
st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; }
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_status_code=True)

# --- 2. API CONNECT (คงเดิมเพื่อความเสถียร) ---
API_KEY = st.secrets.get("RAPIDAPI_KEY", "")
API_HOST = "instagram-scraper-stable-api.p.rapidapi.com"

@st.cache_data(ttl=86400)
def fetch_artist_data(username):
    url = f"https://{API_HOST}/ig_basic_user_posts.php"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    params = {"username_or_url": username} # ต้องใช้ชื่อนี้เท่านั้นสำหรับ Endpoint นี้
    return requests.get(url, headers=headers, params=params)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/174/174855.png", width=50)
    st.title("Settings")
    target_user = st.text_input("IG Username", value="aespa_official")
    update_btn = st.button("🔄 อัปเดตข้อมูล")
    st.divider()
    st.caption("📊 Quota: 10/day | ⏱️ 3/min")

if update_btn:
    st.cache_data.clear()
    st.rerun()

# --- 4. MAIN UI ---
if not API_KEY:
    st.error("กรุณาตั้งค่า RAPIDAPI_KEY ใน Secrets")
else:
    with st.spinner("กำลังจัดเตรียมข้อมูล..."):
        response = fetch_artist_data(target_user)
        
        if response and response.status_code == 200:
            data = response.json()
            user = data.get('data', {}).get('user', {})
            posts = data.get('data', {}).get('items', []) # ดึงรายการโพสต์

            # --- Header Section ---
            col_img, col_info = st.columns([1, 3])
            
            with col_img:
                # แสดงรูปโปรไฟล์ (ถ้ามี)
                profile_pic = user.get('profile_pic_url', 'https://via.placeholder.com/150')
                st.image(profile_pic, width=180)

            with col_info:
                st.title(f"✨ {user.get('full_name', target_user)}")
                st.write(f"@{user.get('username', target_user)}")
                st.write(f"**Bio:** {user.get('biography', 'No bio available.')}")
                if user.get('external_url'):
                    st.link_button("🔗 ลิงก์ที่เกี่ยวข้อง", user['external_url'])

            st.divider()

            # --- Metrics Section ---
            m1, m2, m3 = st.columns(3)
            # แสดงยอด Followers, Following และจำนวนโพสต์
            m1.metric("Followers 👥", f"{user.get('follower_count', 0):,}")
            m2.metric("Following 🤝", f"{user.get('following_count', 0):,}")
            m3.metric("Total Posts 📮", f"{user.get('media_count', 0):,}")

            st.divider()

            # --- Posts Grid Section (โชว์ความเป็น Mockup IG) ---
            st.subheader("🖼️ Latest Posts")
            if posts:
                # จัดเรียงเป็นแถวละ 3 รูป เหมือนใน Instagram
                post_cols = st.columns(3)
                for index, post in enumerate(posts[:9]): # โชว์ 9 โพสต์ล่าสุด
                    with post_cols[index % 3]:
                        # ดึงรูปจากโพสต์ล่าสุด
                        img_url = post.get('image_versions', {}).get('items', [{}])[0].get('url')
                        if img_url:
                            st.image(img_url, use_container_width=True)
                            # แสดงยอด Like ของแต่ละโพสต์ (ถ้ามีข้อมูล)
                            likes = post.get('like_count', 0)
                            st.caption(f"❤️ {likes:,} likes")
            else:
                st.info("ไม่พบข้อมูลโพสต์ล่าสุด หรือบัญชีนี้อาจเป็น Private")

        elif response and response.status_code == 429:
            st.error("Rate Limit: โปรดรอ 20 วินาทีก่อนกดอัปเดตใหม่")
        else:
            st.error("ไม่สามารถดึงข้อมูลได้ โปรดเช็กชื่อ IG หรือสถานะบัญชี")
