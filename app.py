import streamlit as st
import requests

# --- 1. CONFIG & STYLE (แก้ไขจุดที่ Error) ---
st.set_page_config(page_title="Artist Insights", layout="wide")

# แก้ไขจาก unsafe_allow_status_code เป็น unsafe_allow_html
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border-radius: 10px; padding: 15px; border: 1px solid #e6e9ef; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. API CONNECT (ใช้ Secrets เพื่อความปลอดภัย) ---
API_KEY = st.secrets.get("RAPIDAPI_KEY", "")
API_HOST = "instagram-scraper-stable-api.p.rapidapi.com"

@st.cache_data(ttl=86400) # จำข้อมูลไว้ 24 ชม. เพื่อประหยัดโควตา 10 ครั้ง/วัน
def fetch_artist_data(username):
    url = f"https://{API_HOST}/ig_basic_user_posts.php"
    headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
    params = {"username_or_url": username} 
    
    try:
        # ดึงข้อมูลแบบ GET ตามคู่มือ API
        response = requests.get(url, headers=headers, params=params, timeout=15)
        return response
    except Exception as e:
        return None

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎨 Artist Settings")
    target_user = st.text_input("IG Username", value="aespa_official")
    update_btn = st.button("🔄 ดึงข้อมูลใหม่")
    st.divider()
    st.caption("📊 ขีดจำกัด: 10 ครั้ง/วัน")

if update_btn:
    st.cache_data.clear()
    st.rerun()

# --- 4. MAIN UI ---
if not API_KEY:
    st.error("⚠️ ไม่พบ API Key ใน Secrets โปรดตั้งค่า RAPIDAPI_KEY ก่อน")
else:
    with st.spinner("🚀 กำลังโหลดข้อมูล..."):
        response = fetch_artist_data(target_user)
        
        if response and response.status_code == 200:
            data = response.json()
            # แงะข้อมูลจากโครงสร้าง Basic User + Posts
            user = data.get('data', {}).get('user', {})
            posts = data.get('data', {}).get('items', [])

            # --- Header Section ---
            col_img, col_info = st.columns([1, 3])
            
            with col_img:
                profile_pic = user.get('profile_pic_url', 'https://via.placeholder.com/150')
                st.image(profile_pic, width=150)

            with col_info:
                st.title(user.get('full_name', target_user))
                st.write(f"**Bio:** {user.get('biography', 'No bio available.')}")
                st.write(f"🔗 [Link]({user.get('external_url', '#')})")

            st.divider()

            # --- Metrics Section ---
            m1, m2, m3 = st.columns(3)
            m1.metric("Followers", f"{user.get('follower_count', 0):,}")
            m2.metric("Following", f"{user.get('following_count', 0):,}")
            m3.metric("Posts", f"{user.get('media_count', 0):,}")

            st.divider()

            # --- Posts Grid ---
            st.subheader("📸 Latest Posts")
            if posts:
                # แสดงผล 3 คอลัมน์แบบ IG Grid
                grid_cols = st.columns(3)
                for i, post in enumerate(posts[:6]): # โชว์ 6 รูปล่าสุด
                    with grid_cols[i % 3]:
                        # เข้าถึง URL รูปภาพในโครงสร้าง JSON ของ API
                        img_list = post.get('image_versions', {}).get('items', [])
                        if img_list:
                            st.image(img_list[0].get('url'), use_container_width=True)
                            st.caption(f"❤️ {post.get('like_count', 0):,} likes")
            else:
                st.info("ไม่พบข้อมูลโพสต์ล่าสุด")

        elif response and response.status_code == 429:
            st.error("⏱️ Rate Limit: คุณกดเร็วเกินไป (เกิน 3 ครั้ง/นาที) โปรดรอสักครู่")
        elif response:
            st.error(f"Error {response.status_code}: {response.text}")
