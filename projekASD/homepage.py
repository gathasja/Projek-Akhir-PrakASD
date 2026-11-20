import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("loginPage.py")

st.title("My Dashboard")
st.subheader(f"Selamat datang, {st.session_state['username']}!")
st.write("Anda telah berhasil masuk ke aplikasi ini.")
# st.button("Logout")

if st.button("Logout"):
    st.session_state['logged_in'] = False
    st.switch_page("loginPage.py")
    
import streamlit as st

# Konfigurasi halaman (aman dipanggil meski main.py sudah mengatur page_config)
try:
    st.set_page_config(page_title="CineMatch", layout="wide", initial_sidebar_state="expanded")
except st.errors.StreamlitAPIException:
    pass

# Proteksi halaman login (sesuai struktur multipage kamu)
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("loginPage.py")

# --- INISIALISASI SESSION STATE ---
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Homepage"
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = []
if "reviews" not in st.session_state:
    st.session_state["reviews"] = {}
if "review_target" not in st.session_state:
    st.session_state["review_target"] = None

# --- DATA DUMMY FILM (Bisa diganti dengan struktur data / database proyekmu) ---
def make_banner_svg(title: str, bg1: str, bg2: str) -> str:
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="600" height="320" viewBox="0 0 600 320">
      <defs>
        <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{bg1}"/>
          <stop offset="100%" stop-color="{bg2}"/>
        </linearGradient>
      </defs>
      <rect width="600" height="320" rx="20" fill="url(#g)"/>
      <text x="50%" y="52%" dominant-baseline="middle" text-anchor="middle"
            fill="#FFFFFF" font-family="sans-serif" font-size="28" font-weight="bold" opacity="0.9">
        {title}
      </text>
    </svg>
    """.strip()
    import urllib.parse
    return "data:image/svg+xml;utf8," + urllib.parse.quote(svg)

FILMS_DATA = [
    {
        "id": 1,
        "title": "Zootopia",
        "year": 2016,
        "genres": ["Family", "Comedy", "Animation", "Adventure"],
        "duration_min": 109,
        "rating": 78,
        "synopsis": "A rookie bunny cop and a cynical con artist fox must work together to uncover a conspiracy.",
        "poster": make_banner_svg("ZOOTOPIA", "#3B6E8C", "#E09F3E"),
    },
    {
        "id": 2,
        "title": "Coco",
        "year": 2017,
        "genres": ["Family", "Animation", "Music", "Adventure"],
        "duration_min": 105,
        "rating": 82,
        "synopsis": "Aspiring musician Miguel enters the Land of the Dead to find his great-great-grandfather.",
        "poster": make_banner_svg("COCO", "#4A2545", "#F28500"),
    },
    {
        "id": 3,
        "title": "Avatar Aang: The Last Airbender",
        "year": 2026,
        "genres": ["Animation", "Adventure", "Fantasy", "Action"],
        "duration_min": 99,
        "rating": 90,
        "synopsis": "Avatar Aang and his friends embark on a new journey to restore balance across the four nations.",
        "poster": make_banner_svg("AVATAR AANG", "#1D4E89", "#E63946"),
    },
    {
        "id": 4,
        "title": "Inside Out 2",
        "year": 2024,
        "genres": ["Animation", "Family", "Comedy", "Drama"],
        "duration_min": 96,
        "rating": 88,
        "synopsis": "Riley enters puberty and experiences brand new, more complex emotions inside Headquarters.",
        "poster": make_banner_svg("INSIDE OUT 2", "#6A4C93", "#FF924C"),
    },
]

def format_duration(minutes: int) -> str:
    return f"{minutes // 60}h {minutes % 60}m"

# --- CUSTOM CSS AGAR SESUAI MOCKUP ---
st.markdown("""
<style>
    /* Background utama bersih putih */
    .stApp {
        background-color: #FFFFFF;
    }
    .block-container {
        padding-top: 1.8rem !important;
        max-width: 1150px;
    }

    /* Styling Sidebar (Periwinkle / Lavender Blue) */
    [data-testid="stSidebar"] {
        background-color: #CBD4F6;
        border-top-right-radius: 26px;
        border-bottom-right-radius: 26px;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] label p {
        font-weight: 700 !important;
        color: #111111 !important;
        font-size: 0.95rem !important;
    }
    /* Input & Selectbox di dalam Sidebar */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background-color: #9AA6CA !important;
        color: #1A1F36 !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 500;
    }
    /* Tombol Save di Sidebar */
    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        background-color: #6E7A9E !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.45rem 1.8rem !important;
        display: block;
        margin: 0 auto;
    }
    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background-color: #5A668A !important;
    }

    /* Header Brand CineMatch */
    .cinematch-header {
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .cinematch-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #6C789E;
        margin: 0;
        line-height: 1.1;
        letter-spacing: -0.5px;
    }
    .cinematch-subtitle {
        font-size: 1rem;
        font-weight: 600;
        color: #7D8AB2;
        margin-top: 0.25rem;
    }

    /* Styling Border Container (AI Matcher & Kartu Film) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1.5px solid #222222 !important;
        border-radius: 16px !important;
        padding: 14px !important;
        background-color: #FFFFFF !important;
    }

    /* Input AI Matcher */
    .stMainBlockContainer input[type="text"] {
        background-color: #E6E6E6 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 0.65rem 1rem !important;
        color: #222222 !important;
    }

    /* Tombol Primary (+ Watchlist -> Hijau) */
    button[kind="primary"], button[data-testid="stBaseButton-primary"] {
        background-color: #00B865 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover {
        background-color: #009E56 !important;
    }

    /* Tombol Secondary (Review -> Biru Royal) */
    button[kind="secondary"], button[data-testid="stBaseButton-secondary"] {
        background-color: #4E6EF2 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    button[kind="secondary"]:hover, button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #3B5BDB !important;
    }

    /* Poster & Teks di dalam Kartu Film */
    .film-poster {
        width: 100%;
        height: 135px;
        object-fit: cover;
        border-radius: 12px;
        margin-bottom: 10px;
    }
    .film-title {
        font-size: 1rem;
        font-weight: 800;
        color: #111111;
        margin-bottom: 4px;
        line-height: 1.25;
        min-height: 2.5rem;
    }
    .film-title span {
        font-weight: 500;
        color: #333333;
    }
    .film-meta {
        font-size: 0.76rem;
        color: #888888;
        line-height: 1.35;
        margin-bottom: 12px;
        min-height: 2.1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR FILTER ---
with st.sidebar:
    title_query = st.text_input("Title", placeholder="Search title...")
    genre_filter = st.selectbox(
        "Genre",
        ["Animation", "All", "Action", "Adventure", "Comedy", "Drama", "Family", "Fantasy", "Music"],
        index=0,
    )
    duration_range = st.slider("Film Duration", min_value=60, max_value=240, value=(60, 240))
    rating_range = st.slider("Film Rating", min_value=0, max_value=100, value=(0, 100))
    year_range = st.slider("Release Year", min_value=2000, max_value=2026, value=(2000, 2026))
    sort_order = st.selectbox("Sort", ["Ascending", "Descending"], index=0)

    st.write("")
    save_clicked = st.button("Save", key="save_filter_btn")

    st.markdown("---")
    if st.button("Logout", key="logout_btn"):
        st.session_state["logged_in"] = False
        st.switch_page("loginPage.py")

# --- HEADER CINEMATCH ---
st.markdown("""
<div class="cinematch-header">
    <div class="cinematch-title">CineMatch</div>
    <div class="cinematch-subtitle">“Connecting you to the right story.”</div>
</div>
""", unsafe_allow_html=True)

# --- TOP NAVIGATION TABS (Homepage | Watchlist | Reviews) ---
nav_spacer_l, nav_col1, nav_col2, nav_col3, nav_spacer_r = st.columns([1.2, 1.5, 1.5, 1.5, 1.2])

def nav_button(col, label: str):
    is_active = st.session_state["active_tab"] == label
    with col:
        if st.button(
            label,
            key=f"nav_{label}",
            use_container_width=True,
            type="secondary" if is_active else "tertiary",
        ):
            st.session_state["active_tab"] = label
            st.rerun()

# Custom styling khusus tombol tab navigasi tidak aktif (abu-abu seperti gambar)
st.markdown("""
<style>
    button[kind="tertiary"], button[data-testid="stBaseButton-tertiary"] {
        background-color: #BDBDBD !important;
        color: #111111 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    button[kind="tertiary"]:hover, button[data-testid="stBaseButton-tertiary"]:hover {
        background-color: #A8A8A8 !important;
    }
</style>
""", unsafe_allow_html=True)

nav_button(nav_col1, "Homepage")
nav_button(nav_col2, "Watchlist")
nav_button(nav_col3, "Reviews")

st.write("")

# --- KOTAK AI MOOD & STORY MATCHER (GEMINI AI) ---
with st.container(border=True):
    st.markdown("**AI Mood & Story Matcher** (Gemini AI)")
    ai_col1, ai_col2 = st.columns([5.5, 1])
    with ai_col1:
        ai_prompt = st.text_input(
            "AI Prompt",
            label_visibility="collapsed",
            placeholder="Ketik mood atau cerita film yang kamu inginkan...",
        )
    with ai_col2:
        go_clicked = st.button("GO", key="ai_go_btn", use_container_width=True, type="tertiary")

if go_clicked and ai_prompt.strip():
    st.info(f"Mencari rekomendasi film yang cocok dengan mood: **\"{ai_prompt}\"**...")

st.write("")

# --- PROSES FILTER & SORTING ---
filtered_films = []
for film in FILMS_DATA:
    if title_query and title_query.lower() not in film["title"].lower():
        continue
    if genre_filter != "All" and genre_filter not in film["genres"]:
        continue
    if not (duration_range[0] <= film["duration_min"] <= duration_range[1]):
        continue
    if not (rating_range[0] <= film["rating"] <= rating_range[1]):
        continue
    if not (year_range[0] <= film["year"] <= year_range[1]):
        continue
    if ai_prompt.strip():
        kw = ai_prompt.lower()
        if kw not in film["title"].lower() and kw not in film["synopsis"].lower() and not any(kw in g.lower() for g in film["genres"]):
            continue
    filtered_films.append(film)

filtered_films.sort(key=lambda x: x["year"], reverse=(sort_order == "Descending"))

# --- TAMPILAN BERDASARKAN TAB AKTIF ---
active_tab = st.session_state["active_tab"]

if active_tab == "Homepage":
    st.markdown("#### **Film Catalogue** (Filtered & Sorted)")

    if not filtered_films:
        st.warning("Tidak ada film yang sesuai dengan filter saat ini.")
    else:
        # Render grid 3 kolom per baris
        for i in range(0, len(filtered_films), 3):
            cols = st.columns(3, gap="medium")
            for idx, film in enumerate(filtered_films[i : i + 3]):
                with cols[idx]:
                    with st.container(border=True):
                        genre_str = "/".join(film["genres"])
                        dur_str = format_duration(film["duration_min"])

                        st.markdown(f"""
                        <img src="{film['poster']}" class="film-poster" alt="{film['title']}"/>
                        <div class="film-title">{film['title']} <span>({film['year']})</span></div>
                        <div class="film-meta">{genre_str} | {dur_str} | {film['rating']}%</div>
                        """, unsafe_allow_html=True)

                        btn_col1, btn_col2 = st.columns(2, gap="small")
                        in_watchlist = film["id"] in st.session_state["watchlist"]
                        with btn_col1:
                            wl_label = "✓ Saved" if in_watchlist else "+ Watchlist"
                            if st.button(wl_label, key=f"wl_{film['id']}", use_container_width=True, type="primary"):
                                if in_watchlist:
                                    st.session_state["watchlist"].remove(film["id"])
                                else:
                                    st.session_state["watchlist"].append(film["id"])
                                st.rerun()
                        with btn_col2:
                            if st.button("Review", key=f"rev_{film['id']}", use_container_width=True, type="secondary"):
                                st.session_state["review_target"] = film["title"]
                                st.session_state["active_tab"] = "Reviews"
                                st.rerun()

elif active_tab == "Watchlist":
    st.markdown("#### **My Watchlist**")
    wl_films = [f for f in FILMS_DATA if f["id"] in st.session_state["watchlist"]]
    if not wl_films:
        st.info("Watchlist kamu masih kosong. Klik tombol **+ Watchlist** pada kartu film di Homepage.")
    else:
        cols = st.columns(3, gap="medium")
        for idx, film in enumerate(wl_films):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"""
                    <img src="{film['poster']}" class="film-poster"/>
                    <div class="film-title">{film['title']} <span>({film['year']})</span></div>
                    <div class="film-meta">{"/".join(film['genres'])} | {format_duration(film['duration_min'])} | {film['rating']}%</div>
                    """, unsafe_allow_html=True)
                    if st.button("Hapus dari Watchlist", key=f"del_wl_{film['id']}", use_container_width=True, type="tertiary"):
                        st.session_state["watchlist"].remove(film["id"])
                        st.rerun()

elif active_tab == "Reviews":
    st.markdown("#### **Film Reviews**")
    film_titles = [f["title"] for f in FILMS_DATA]
    default_idx = film_titles.index(st.session_state["review_target"]) if st.session_state["review_target"] in film_titles else 0

    with st.container(border=True):
        selected_film = st.selectbox("Pilih Film", film_titles, index=default_idx)
        user_rating = st.slider("Rating Kamu (%)", 0, 100, 85)
        user_comment = st.text_area("Tulis Ulasanmu", placeholder="Bagaimana pendapatmu tentang alur cerita dan visual film ini?")
        if st.button("Kirim Review", type="secondary"):
            if user_comment.strip():
                st.session_state["reviews"].setdefault(selected_film, []).append(
                    {"rating": user_rating, "comment": user_comment.strip()}
                )
                st.success(f"Review untuk **{selected_film}** berhasil ditambahkan!")

    for title, rev_list in st.session_state["reviews"].items():
        for rev in rev_list:
            with st.container(border=True):
                st.markdown(f"**{title}** — Rating: **{rev['rating']}%**")
                st.write(rev["comment"])