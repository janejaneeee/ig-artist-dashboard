import streamlit as st
from apify_client import ApifyClient

# --- 1. CONFIG ---
st.set_page_config(page_title="Artist Insights", layout="wide")
st.title("📈 Artist Overview Dashboard")

APIFY_TOKEN = st.secrets.get("APIFY_TOKEN", "")

@st.cache_data(ttl=86400)
def fetch_data(username):
    if not APIFY_TOKEN: return None
    client = ApifyClient(APIFY_TOKEN)
    try:
        # ใช้ Actor ตัวที่เสถียรที่สุด
        run_input = { "usernames": [username] }
        run = client.actor("apify/instagram-profile-scraper").call(run_input=run_input)
        items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        return items[0] if items else None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# --- 2. SIDEBAR ---
target_user = st.sidebar.text_input("IG Username", value="aespa_official")
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- 3. MAIN DISPLAY ---
if not APIFY_TOKEN:
    st.warning("⚠️ Please set APIFY_TOKEN in Secrets")
else:
    with st.spinner("Loading Stats..."):
        user = fetch_data(target_user)
        
        if user:
            # --- Profile Header ---
            c1, c2 = st.columns([1, 4])
            with c1:
                st.image(user.get('profilePicUrl', ''), width=150)
            with c2:
                st.header(user.get('fullName', target_user))
                st.write(f"@{user.get('username', '')}")

            st.divider()

            # --- Metrics (จุดที่ปรับแก้ให้มองเห็นชัด) ---
            # ใช้การดึงค่าแบบรองรับหลายชื่อ Key (Fallback Keys)
            f_count = user.get('followersCount') or user.get('followers') or 0
            p_count = user.get('postsCount') or user.get('mediaCount') or 0
            
            # คำนวณ Engagement จากโพสต์ล่าสุด
            posts = user.get('latestPosts', [])
            avg_likes = sum(p.get('likesCount', 0) for p in posts) / len(posts) if posts else 0
            er = (avg_likes / f_count * 100) if f_count > 0 else 0

            # แสดงผลแบบ Standard เพื่อเลี่ยงปัญหา CSS สีจาง
            st.subheader("📊 Key Performance Indicators")
            m1, m2, m3, m4 = st.columns(4)
            
            # ใส่ Label ให้ชัดเจนและใช้ตัวเลขสีเข้ม
            m1.metric("Followers", f"{f_count:,}")
            m2.metric("Total Posts", f"{p_count:,}")
            m3.metric("Avg. Likes", f"{int(avg_likes):,}")
            m4.metric("Engagement Rate", f"{er:.2f}%")

            st.divider()

            # --- Grid Content ---
            if posts:
                st.subheader("📸 Recent Content")
                grid = st.columns(3)
                for i, post in enumerate(posts[:6]):
                    with grid[i % 3]:
                        st.image(post.get('displayUrl'), use_container_width=True)
                        st.caption(f"❤️ {post.get('likesCount', 0):,} | 💬 {post.get('commentsCount', 0):,}")
        else:
            st.error("❌ No data found. Please check the username.")
