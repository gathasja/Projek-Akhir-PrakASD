from datetime import datetime
import streamlit as st
from services.ai_service import rekomendasi_mood_ai
from services.tmdb_service import ambil_katalog_tmdb


def _tambah_ke_watchlist(film: dict):
    """Menambahkan salinan data film beserta bulan ditambahkan ke dalam session_state.watchlist."""
    item_wl = film.copy()
    item_wl.setdefault("bulan_tonton", datetime.now().strftime("%b %Y"))
    st.session_state.watchlist.append(item_wl)


def _cari_film_rekomendasi_tmdb(daftar_rekomendasi: list) -> list:
    """Mengambil data kartu film lengkap dari TMDB berdasarkan judul rekomendasi AI."""
    tmdb_key = str(st.secrets.get("TMDB_API_KEY", "")).strip()
    if not tmdb_key or not daftar_rekomendasi:
        return []

    hasil_kartu = []
    id_tercatat = set()

    for item in daftar_rekomendasi[:3]:
        judul_cari = str(item.get("judul", "")).strip()
        tahun_cari = item.get("tahun")
        if not judul_cari:
            continue

        kandidat = ambil_katalog_tmdb(judul_cari, [], tmdb_key)
        if kandidat:
            pilihan = kandidat[0]
            if tahun_cari:
                for f in kandidat:
                    if str(f.get("tahun")) == str(tahun_cari):
                        pilihan = f
                        break
            if pilihan["id"] not in id_tercatat:
                id_tercatat.add(pilihan["id"])
                hasil_kartu.append(pilihan)

    return hasil_kartu


def _render_grid_film(daftar_film: list, key_prefix: str):
    """Merender daftar film dalam grid kartu 3 kolom lengkap dengan tombol Watchlist, Review, dan Detail."""
    cols = st.columns(3, gap="medium")
    watchlist = st.session_state.get("watchlist", [])

    for idx, film in enumerate(daftar_film):
        with cols[idx % 3]:
            with st.container(border=True):
                gambar_tampil = film.get("backdrop_url") or film.get("poster_url")
                if gambar_tampil:
                    st.image(gambar_tampil, use_container_width=True)

                st.markdown(f"**{film['judul']} ({film['tahun']})**")
                st.caption(f"{film['genre']} | {film['durasi_str']} | {film['rating_persen']}%")

                sudah_ada = any(w["id"] == film["id"] for w in watchlist)
                c_wl, c_rev, c_det = st.columns([1.25, 1, 0.95])

                with c_wl:
                    if st.button(
                        "✔️ Saved" if sudah_ada else "+ Watchlist",
                        key=f"{key_prefix}_wl_{film['id']}",
                        disabled=sudah_ada,
                        use_container_width=True,
                    ):
                        _tambah_ke_watchlist(film)
                        st.toast(f"'{film['judul']}' masuk ke Watchlist!")
                        st.rerun()

                with c_rev:
                    if st.button(
                        "Review",
                        key=f"{key_prefix}_rev_{film['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.selected_movie = film
                        st.toast(f"'{film['judul']}' dipilih! Klik tab Reviews di atas.")

                with c_det:
                    if st.button(
                        "Detail",
                        key=f"{key_prefix}_det_{film['id']}",
                        use_container_width=True,
                    ):
                        st.session_state.homepage_detail_movie = film
                        st.rerun()


def _render_detail_film_modal_view(film: dict):
    """
    Tampilan detail film (sesuai Wireframe Halaman 9 Proposal):
    Poster besar di kiri + Judul, Genre/Durasi/Rating, Synopsis lengkap,
    tombol '+ Watchlist', tombol 'Review', dan tombol kembali ke katalog.
    """
    if st.button("← Kembali ke Film Catalogue", key="btn_back_catalogue"):
        st.session_state.homepage_detail_movie = None
        st.rerun()

    st.write("")
    col_poster, col_detail = st.columns([1.05, 1.8], gap="large")

    with col_poster:
        if film.get("poster_url"):
            st.image(film["poster_url"], use_container_width=True)
        else:
            st.info("belum masang API tmbd yak bos, sabar")

    with col_detail:
        with st.container(border=True):
            st.markdown(f"## {film['judul']} ({film['tahun']})")
            st.caption(f"{film['genre']}  |  {film['durasi_str']}  |  {film['rating_persen']}%")
            st.markdown(f"**Sutradara:** {film.get('sutradara', '-')}")
            st.markdown("### Synopsis")
            st.write(film["sinopsis"])

            st.write("")
            b1, b2 = st.columns(2)
            watchlist = st.session_state.get("watchlist", [])
            sudah_ada = any(w["id"] == film["id"] for w in watchlist)

            with b1:
                if st.button(
                    "✔️ In Watchlist" if sudah_ada else "+ Watchlist",
                    key=f"detail_wl_{film['id']}",
                    disabled=sudah_ada,
                    type="primary",
                    use_container_width=True,
                ):
                    _tambah_ke_watchlist(film)
                    st.toast(f"'{film['judul']}' ditambahkan ke Watchlist!")
                    st.rerun()

            with b2:
                if st.button(
                    "Review",
                    key=f"detail_rev_{film['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_movie = film
                    st.toast(f"'{film['judul']}' dipilih! Silakan buka tab Reviews.")


def render_tab_homepage(katalog_final: list):
    """
    Merender Tab Homepage (Tanggung Jawab Kevin Ariel Solomon - 71251208):
    1. Area AI Mood & Story Matcher (bebas dari filter sidebar + langsung menampilkan kartu film rekomendasi).
    2. Area Film Catalogue (Filtered & Sorted) dalam grid kartu 3 kolom + tampilan detail film.
    """
    if st.session_state.get("homepage_detail_movie"):
        _render_detail_film_modal_view(st.session_state["homepage_detail_movie"])
        return

    # 1. AREA AI MOOD & STORY MATCHER
    with st.container(border=True):
        st.markdown("#### ✨ Cari Film Berdasarkan Moodmu Hari Ini disini")
        col_in, col_go = st.columns([5, 1])
        with col_in:
            mood_input = st.text_input(
                "Ceritakan tema film yang kamu inginkan:",
                placeholder="Contoh: Lagi pengen film bertema kerajaan yang epik dan magical...",
                label_visibility="collapsed",
                key="input_mood_ai",
            )
        with col_go:
            klik_go = st.button("GO", type="primary", use_container_width=True)

        if klik_go:
            st.info("masih tahap 1 ya euy, fiturnya baru dibuat kapan2 kalau inget")

        if st.session_state.get("hasil_ai_mood"):
            st.info(st.session_state["hasil_ai_mood"])

            film_ai = st.session_state.get("hasil_ai_films", [])
            if film_ai:
                st.markdown("##### 🎬 Katalog Film Rekomendasi AI")
                _render_grid_film(film_ai, key_prefix="ai")

            if st.button("Tutup Rekomendasi AI", key="btn_clear_ai"):
                st.session_state["hasil_ai_mood"] = ""
                st.session_state["hasil_ai_films"] = []
                st.rerun()

    st.write("")

    # 2. AREA FILM CATALOGUE (FILTERED & SORTED)
    st.subheader("Katalog Film (Terfilter & Tersortir)")

    if st.session_state.get("tmdb_error"):
        st.error(f"⚠️ {st.session_state['tmdb_error']}")
        return

    if not katalog_final:
        st.warning("ga ada yang cocok ama filter auy. Coba bro, longgarin filter di sidebar.")
        return

    _render_grid_film(katalog_final, key_prefix="home")