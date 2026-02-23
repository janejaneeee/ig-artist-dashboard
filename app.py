import streamlit as st
from apify_client import ApifyClient
from datetime import datetime

# --- 1. SETTINGS & UI STYLE ---
st.set_page_config(page_title="Artist Engagement Dashboard", layout="wide")

# ปรับแต่ง CSS ให้ Metric ดูพรีเมียมขึ้น
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; border: 1px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    </style>
    """, unsafe_allow_html=True)

# ดึง Token จาก Secrets
APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "")

# --- 2. DATA FETCHING FUNCTION ---
@st.cache_data(ttl=86400) # จำข้อมูลไว้ 24 ชม. เพื่อประหยัด Credits ($5/เดือน)
def fetch_instagram_data(username):
    if not APIFY_TOKEN:
        return None
    
    client = ApifyClient(APIFY_TOKEN)
    
    # ใช้ Actor: instagram-profile-scraper (ตัวนี้ให้ข้อมูล Like รายโพสต์มาด้วย)
    run_input = { "usernames": [username] }
    
    try:
        # สั่งรันและรอผล (Asynchronous Process)
        run = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
        
        # ดึงข้อมูลจากผลลัพธ์ (Dataset)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        return items[0] if items else None
    except Exception as e:
        st.error(f"Apify Error: {e}")
        return None

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1384/1384063.png", width=50)
    st.title("Settings")
    target_user = st.text_input("IG Username", value="aespa_official")
    
    if st.button("🔄 อัปเดตข้อมูลใหม่", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    st.info("💡 ข้อมูลจะถูกจำไว้ 24 ชม. เพื่อช่วยคุณประหยัด Credits ฟรีจาก Apify")

# --- 4. MAIN DASHBOARD DISPLAY ---
if not APIFY_TOKEN:
    st.warning("⚠️ โปรดตั้งค่า APIFY_TOKEN ใน Streamlit Secrets ก่อนเริ่มใช้งาน")
else:
    with st.spinner(f"Apify กำลังรวบรวมข้อมูล @{target_user} (ใช้เวลาประมาณ 15-30 วินาที)..."):
        user_data = fetch_instagram_data(target_user)
        
        if user_data:
            # --- ส่วนหัว: Profile Overview ---
            col_img, col_info = st.columns([1, 4])
            with col_img:
                st.image(user_data.get('profilePicUrl', ''), width=150)
            with col_info:
                st.title(user_data.get('fullName', target_user))
                st.write(f"@{user_data.get('username', '')}")
                st.write(f"📝 **Bio:** {user_data.get('biography', 'No bio available.')}")
            
            st.divider()

            # --- ส่วนสถิติ: Metrics Overview ---
            st.subheader("📊 Performance Summary")
            
            # การคำนวณสถิติยอด Like และ Engagement
            latest_posts = user_data.get('latestPosts', [])
            followers = user_data.get('followersCount', 1) # กันหารด้วย 0
            
            if latest_posts:
                total_likes = sum(p.get('likesCount', 0) for p in latest_posts)
                avg_likes = total_likes / len(latest_posts)
                # Engagement Rate = (Likes เฉลี่ย / Followers) * 100
                er = (avg_likes / followers) * 100
            else:
                avg_likes, er = 0, 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Followers 👥", f"{followers:,}")
            m2.metric("Total Posts 📮", f"{user_data.get('postsCount', 0):,}")
            m3.metric("Avg. Likes ❤️", f"{int(avg_likes):,}")
            m4.metric("Engagement 🚀", f"{er:.2f}%")

            st.divider()

            # --- ส่วน Grid: Latest Content ---
            st.subheader("🖼️ Latest Content Analysis")
            if latest_posts:
                grid = st.columns(3)
                for i, post in enumerate(latest_posts[:6]): # แสดง 6 โพสต์ล่าสุด
                    with grid[i % 3]:
                        st.image(post.get('displayUrl'), use_container_width=True)
                        st.caption(f"❤️ {post.get('likesCount', 0):,} Likes | 💬 {post.get('commentsCount', 0):,} Comments")
            else:
                st.info("ไม่พบข้อมูลโพสต์ล่าสุดในขณะนี้")
                
        else:
            st.error("ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบว่า Token ถูกต้องหรือชื่อ IG มีอยู่จริงหรือไม่")
