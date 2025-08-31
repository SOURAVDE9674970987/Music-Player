import streamlit as st
import requests

# ---------- Spotify API ----------
CLIENT_ID = "ef88de20f02d4990ab7ca7726e5fdd5e"
CLIENT_SECRET = "55c22cd4bca54c3f93b02fdff5e45126"
AUTH_URL = "https://accounts.spotify.com/api/token"
SEARCH_URL = "https://api.spotify.com/v1/search"

def get_access_token():
    resp = requests.post(
        AUTH_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return resp.json()["access_token"]

def search_spotify(query, token, limit=10, offset=0):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": limit, "offset": offset}
    resp = requests.get(SEARCH_URL, headers=headers, params=params)
    return resp.json().get("tracks", {}).get("items", [])

def embed_player(track_id):
    url = f"https://open.spotify.com/embed/track/{track_id}"
    st.markdown(
        f"""
        <div class="embed-wrap fade-in">
            <iframe src="{url}" width="100%" height="80" frameborder="0" 
            allowtransparency="true" allow="encrypted-media"></iframe>
        </div>
        """, unsafe_allow_html=True
    )

# ---------- Streamlit Config ----------
st.set_page_config(page_title="🎶 Mobile Spotify Player", layout="centered")

# ---------- Mobile-Friendly Dark UI + Animations ----------
st.markdown("""
<style>
body, .stApp {
    background-color: #121212;
    color: #fff;
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    padding: 0;
}

/* Fade-in Animation */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in {
  animation: fadeIn 0.6s ease-in-out;
}

/* Title */
h1 {
    text-align: center;
    color: #1DB954;
    font-weight: 900;
    margin: 10px 0 25px;
    font-size: 30px;
    letter-spacing: 1px;
}

/* Control Bar */
.control-bar {
    background: linear-gradient(145deg, #181818, #202020);
    padding: 14px 16px;
    border-radius: 18px;
    margin-bottom: 20px;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Search Input */
input[type="text"] {
    border-radius: 25px;
    padding: 12px 16px;
    font-size: 16px;
    border: none;
    outline: none;
    width: 100%;
    background: #2a2a2a;
    color: #fff;
    transition: 0.3s ease;
}
input[type="text"]:focus {
    background: #333;
    border: 1px solid #1DB954;
}

/* Buttons General */
.stButton button {
    border-radius: 25px !important;
    font-weight: bold !important;
    font-size: 15px !important;
    padding: 10px 16px !important;
    transition: 0.25s ease-in-out;
    border: none !important;
}

/* Search Button */
.stButton button#search_btn {
    background: #1DB954 !important;
    color: white !important;
}
.stButton button#search_btn:hover {
    background: #1ed760 !important;
    transform: scale(1.08);
    box-shadow: 0 0 10px #1db954aa;
}

/* Clear Button */
.stButton button#clear_btn {
    background: #e63946 !important;
    color: white !important;
}
.stButton button#clear_btn:hover {
    background: #ff4d6d !important;
    transform: scale(1.08);
    box-shadow: 0 0 10px #ff4d6daa;
}

/* Song Card */
.song-card {
    background: linear-gradient(145deg, #181818, #1e1e1e);
    border-radius: 16px;
    padding: 14px;
    margin: 16px 0;
    box-shadow: 0px 4px 14px rgba(0,0,0,0.55);
    text-align: center;
    transition: 0.3s ease-in-out;
}
.song-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0px 8px 20px rgba(0,0,0,0.75);
}

/* Song Title */
.song-title {
    color: #fff;
    font-size: 18px;
    font-weight: bold;
    margin: 10px 0 4px;
    letter-spacing: 0.5px;
}

/* Artist */
.song-artist {
    color: #aaa;
    font-size: 14px;
    margin-bottom: 10px;
    font-style: italic;
}

/* Spotify Embed */
.embed-wrap iframe {
    border-radius: 10px;
    margin-top: 8px;
}

/* Load More Button */
.load-btn button {
    background: #1DB954 !important;
    color: white !important;
    border-radius: 25px !important;
    font-weight: bold !important;
    padding: 10px 20px !important;
    transition: 0.3s ease-in-out;
}
.load-btn button:hover {
    background: #1ed760 !important;
    transform: scale(1.07);
    box-shadow: 0 0 12px #1db95488;
}
</style>
""", unsafe_allow_html=True)

st.title("🎧 Mobile Music Player")

# ---------- Session State ----------
if "results" not in st.session_state: st.session_state.results = []
if "offset" not in st.session_state: st.session_state.offset = 0
if "search_active" not in st.session_state: st.session_state.search_active = False
if "search_query" not in st.session_state: st.session_state.search_query = ""

# ---------- Search Bar ----------
with st.container():
    st.markdown('<div class="control-bar">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([3,1,1])
    with col1: search_query = st.text_input("Search song name...")
    with col2: search_button = st.button("🔍", key="search_btn")
    with col3: clear_button = st.button("❌", key="clear_btn")

    if search_button and search_query:
        st.session_state.search_query = search_query
        st.session_state.search_active = True
        st.session_state.offset = 0
        st.session_state.results = []
        st.rerun()
    if clear_button:
        st.session_state.search_active = False
        st.session_state.search_query = ""
        st.session_state.offset = 0
        st.session_state.results = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Build Query ----------
final_query = None
if st.session_state.get("search_active", False):
    final_query = st.session_state.search_query
else:
    # Default trending feed
    final_query = "Top Trending Global Songs"

# ---------- Fetch and Display Songs ----------
if final_query:
    token = get_access_token()
    new_tracks = search_spotify(final_query, token, offset=st.session_state.offset, limit=6)
    if new_tracks:
        st.session_state.results.extend(new_tracks)
        st.session_state.offset += 6

    for track in st.session_state.results:
        st.markdown('<div class="song-card fade-in">', unsafe_allow_html=True)
        st.image(track["album"]["images"][0]["url"], width=220)
        st.markdown(f'<div class="song-title">{track["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="song-artist">{", ".join([a["name"] for a in track["artists"]])}</div>', unsafe_allow_html=True)
        embed_player(track["id"])
        st.markdown('</div>', unsafe_allow_html=True)

    # Load More Button
    st.markdown('<div class="load-btn">', unsafe_allow_html=True)
    if st.button("⬇️ Load More Songs"):
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
