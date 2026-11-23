import streamlit as st
from services.tmdb_service import GENRE_MAP, ambil_katalog_tmdb
from utils.dsa_helpers import (
    FilterHistoryStack,
    filter_katalog_searching,
    urutkan_katalog_selection_sort,
)
from ui.tab_homepage import render_tab_homepage
from ui.tab_watchlist import render_tab_watchlist
from ui.tab_review import render_tab_review

# ==========================================
# 1. KONFIGURASI HALAMAN & GAYA VISUAL
# ==========================================
st.set_page_config(
    page_title="CineMatch — Connecting you to the right story",
    page_icon="🎬",
    layout="wide",
)

# Custom CSS ringan agar nuansa warna selaras dengan wireframe di proposal
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-color: #DCE1FA;
    }
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #4A558F;
        margin-bottom: 0;
    }
    .main-tagline {
        text-align: center;
        font-size: 1rem;
        color: #64748B;
        margin-top: 0;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

TMDB_KEY = st.secrets.get("TMDB_API_KEY", "")

# ==========================================
# 2. INISIALISASI STRUKTUR DATA (SESSION STATE)
# ==========================================
if "api_cache" not in st.session_state:
    st.session_state.api_cache = {}
if "detail_cache" not in st.session_state:
    st.session_state.detail_cache = {}
if "filter_stack_data" not in st.session_state:
    st.session_state.filter_stack_data = []
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "watched_films" not in st.session_state:
    st.session_state.watched_films = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "homepage_detail_movie" not in st.session_state:
    st.session_state.homepage_detail_movie = None
if "user_reviews" not in st.session_state:
    st.session_state.user_reviews = {}

# Default nilai filter di session_state agar tombol Undo Stack dapat memulihkan nilai filter
st.session_state.setdefault("f_title", "")
st.session_state.setdefault("f_genre", [])
st.session_state.setdefault("f_duration", (30, 240))
st.session_state.setdefault("f_rating", 50)
st.session_state.setdefault("f_year", (1995, 2026))
st.session_state.setdefault("f_sort", "Rating (Descending)")

history_stack = FilterHistoryStack(st.session_state.filter_stack_data)

# ==========================================
# 3. SIDEBAR: FILTER & SORTING (Sesuai Wireframe Proposal)
# ==========================================
with st.sidebar:
    st.markdown("### 🎬 Filter & Pencarian")

    title_input = st.text_input(
        "Title",
        key="f_title",
        placeholder="Cari judul film...",
    )

    genre_input = st.multiselect(
        "Genre",
        options=list(GENRE_MAP.keys()),
        key="f_genre",
        placeholder="Pilih genre...",
    )

    duration_input = st.slider(
        "Film Duration (menit)",
        min_value=30,
        max_value=240,
        key="f_duration",
        step=5,
    )

    rating_input = st.slider(
        "Film Rating (%)",
        min_value=0,
        max_value=100,
        key="f_rating",
        step=5,
    )

    year_input = st.slider(
        "Release Year",
        min_value=1980,
        max_value=2026,
        key="f_year",
    )

    sort_input = st.selectbox(
        "Sort",
        options=[
            "Rating (Descending)",
            "Rating (Ascending)",
            "Release Year (Newest)",
            "Release Year (Oldest)",
            "Duration (Shortest)",
            "Duration (Longest)",
            "Title (A-Z)",
        ],
        key="f_sort",
    )

    # Pengambilan data TMDB -> Algoritma Searching -> Algoritma Selection Sort
    katalog_mentah = ambil_katalog_tmdb(title_input, genre_input, TMDB_KEY)
    katalog_terfilter = filter_katalog_searching(
        katalog_mentah,
        genres=genre_input,
        durasi_range=duration_input,
        rating_min_persen=rating_input,
        tahun_range=year_input,
    )
    katalog_final = urutkan_katalog_selection_sort(katalog_terfilter, sort_input)

    st.caption(f"Menampilkan {len(katalog_final)} dari {len(katalog_mentah)} film.")

    # Tombol Save (Push ke Stack) & Undo (Pop dari Stack)
    col_save, col_undo = st.columns(2)
    with col_save:
        if st.button("Save", use_container_width=True):
            history_stack.push({
                "title": title_input,
                "genre": list(genre_input),
                "duration": duration_input,
                "rating": rating_input,
                "year": year_input,
                "sort": sort_input,
            })
            st.toast(f"Filter disimpan ke Stack! (Total riwayat: {history_stack.size()})")

    with col_undo:
        if st.button("Undo", use_container_width=True, disabled=history_stack.is_empty()):
            prev = history_stack.pop()
            if prev:
                st.session_state["f_title"] = prev["title"]
                st.session_state["f_genre"] = prev["genre"]
                st.session_state["f_duration"] = prev["duration"]
                st.session_state["f_rating"] = prev["rating"]
                st.session_state["f_year"] = prev["year"]
                st.session_state["f_sort"] = prev["sort"]
                st.toast("Parameter filter dikembalikan dari riwayat Stack!")
                st.rerun()

    if st.button("🔄 Refresh Data API", use_container_width=True):
        st.session_state.api_cache.clear()
        st.session_state.detail_cache.clear()
        st.rerun()

# ==========================================
# 4. HEADER & 3 TAB UTAMA (Homepage, Watchlist, Reviews)
# ==========================================
st.markdown('<div class="main-title">CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="main-tagline">"Connecting you to the right story."</div>', unsafe_allow_html=True)

tab_homepage, tab_watchlist, tab_reviews = st.tabs([
    "Homepage",
    "Watchlist",
    "Reviews",
])

with tab_homepage:
    render_tab_homepage(katalog_final)

with tab_watchlist:
    render_tab_watchlist()

with tab_reviews:
    render_tab_review(katalog_final)