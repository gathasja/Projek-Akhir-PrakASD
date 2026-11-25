import streamlit as st
from ui.tab_homepage import render_tab_homepage
from ui.tab_watchlist import render_tab_watchlist
from ui.tab_review import render_tab_review

st.set_page_config(
    page_title="CineMatch — Connecting you to the right story",
    page_icon="🎬",
    layout="wide",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { background-color: #DCE1FA; }
    .main-title { text-align: center; font-size: 2.5rem; font-weight: 800; color: #4A558F; margin-bottom: 0; }
    .main-tagline { text-align: center; font-size: 1rem; color: #64748B; margin-top: 0; margin-bottom: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Data contoh (Dummy) khusus untuk demonstrasi tampilan Tahap 1
DUMMY_FILMS = [
    {
        "id": 1,
        "judul": "Zootopia",
        "tahun": "2016",
        "genre": "Animation / Comedy / Adventure",
        "durasi": 108,
        "durasi_str": "1h 48m",
        "rating_persen": 78,
        "sutradara": "Byron Howard",
        "sinopsis": "Officer Judy Hopps bekerja sama dengan rubah cerdik Nick Wilde untuk memecahkan kasus hilangnya warga di kota Zootopia.",
        "poster": "https://image.tmdb.org/t/p/w500/hlK0e0wAQ3VLuJcsfIYPvb4JVud.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w780/9tOkjBE8ckgzModgV41n4lZ6072.jpg",
    },
    {
        "id": 2,
        "judul": "Coco",
        "tahun": "2017",
        "genre": "Animation / Family / Music",
        "durasi": 105,
        "durasi_str": "1h 45m",
        "rating_persen": 82,
        "sutradara": "Lee Unkrich",
        "sinopsis": "Miguel bermimpi menjadi musisi hebat dan tanpa sengaja memasuki Negeri Arwah untuk mengungkap kisah keluarganya.",
        "poster": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w780/askg3SMvhqEl4OL52YuvdtY40Yb.jpg",
    },
    {
        "id": 3,
        "judul": "Interstellar",
        "tahun": "2014",
        "genre": "Science Fiction / Drama / Adventure",
        "durasi": 169,
        "durasi_str": "2h 49m",
        "rating_persen": 84,
        "sutradara": "Christopher Nolan",
        "sinopsis": "Sekelompok penjelajah luar angkasa melewati lubang cacing demi mencari planet baru bagi kelangsungan hidup umat manusia.",
        "poster": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop": "https://image.tmdb.org/t/p/w780/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
    },
]

st.session_state.setdefault("watchlist", [DUMMY_FILMS[0]])
st.session_state.setdefault("watched_films", [])
st.session_state.setdefault("selected_movie", None)
st.session_state.setdefault("homepage_detail_movie", None)
st.session_state.setdefault("user_reviews", {})

# Sidebar UI Lengkap (Tahap 1)
with st.sidebar:
    st.markdown("### 🎬 Filter & Pencarian")
    st.text_input("Judul", placeholder="Cari judul film...")
    st.multiselect("Genre", options=["Animation", "Action", "Comedy", "Drama", "Science Fiction"], placeholder="Pilih genre...")
    st.slider("Durasi Film (menit)", 30, 240, (30, 240), step=5)
    st.slider("Rating Rating (%)", 0, 100, 50, step=5)
    st.slider("Tahun Rilis", 1980, 2026, (1995, 2026))
    st.selectbox("Urutan", options=["Rating (Descending)", "Rating (Ascending)", "Release Year (Terbaru)"])

    st.caption(f"Menampilkan {len(DUMMY_FILMS)} dari {len(DUMMY_FILMS)} film.")

    # Tombol Save & Undo (Tampilan UI Tahap 1)
    col_save, col_undo = st.columns(2)
    with col_save:
        if st.button("Simpan", use_container_width=True):
            st.toast("Tampilan UI: Filter disimpan (Logika Stack diaktifkan pada Tahap 2).")
    with col_undo:
        if st.button("Batalkan", use_container_width=True):
            st.toast("Tampilan UI: Undo filter (Logika Stack diaktifkan pada Tahap 2).")

    if st.button("🔄 Muat Ulang Data API", use_container_width=True):
        st.toast("Tampilan UI: Koneksi API TMDB diaktifkan pada Tahap 2.")

st.markdown('<div class="main-title">CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="main-tagline">"Connecting you to the right story."</div>', unsafe_allow_html=True)

tab_homepage, tab_watchlist, tab_reviews = st.tabs(["Homepage", "Watchlist", "Reviews"])

with tab_homepage:
    render_tab_homepage(DUMMY_FILMS)

with tab_watchlist:
    render_tab_watchlist()

with tab_reviews:
    render_tab_review(DUMMY_FILMS)