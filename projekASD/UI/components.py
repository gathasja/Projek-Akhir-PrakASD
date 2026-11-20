import streamlit as st


def _kategori_rating(rating: float) -> str:
    """Mengubah skor rating TMDB (0-10) menjadi label status singkat seperti referensi UI."""
    if rating >= 8.0:
        return "Sangat Direkomendasikan"
    elif rating >= 6.8:
        return "Layak Tonton"
    elif rating >= 5.5:
        return "Biasa saja"
    return "Kurang Direkomendasikan"


def render_kartu_detail_film(film: dict, key_prefix: str = "card", show_actions: bool = True):
    """
    Merender tampilan film dengan tata letak bersih persis seperti referensi UI:
    - Strip banner backdrop tipis di bagian paling atas
    - Layout 2 kolom lega tanpa kotak border kaku: Poster besar di kiri + caption judul,
      detail lengkap di kanan (Judul besar, judul asli & genre, badge status rating,
      3 kolom metrik Tahun | Durasi | Rating, Sutradara, Produser, dan Sinopsis).
    """
    # Strip backdrop tipis di bagian atas (menyerupai potongan gambar atas di referensi UI)
    if film.get("backdrop_url"):
        st.markdown(
            f"""
            <div style="width:100%; height:34px; overflow:hidden; border-radius:4px; margin-bottom:14px;">
                <img src="{film['backdrop_url']}" style="width:100%; height:180px; object-fit:cover; object-position:center;">
            </div>
            """,
            unsafe_allow_html=True,
        )

    col_poster, col_info = st.columns([1.05, 2.2], gap="large")

    with col_poster:
        if film.get("poster_url"):
            st.image(film["poster_url"], use_container_width=True, caption=film["judul"])
        else:
            st.info("Poster tidak tersedia")

    with col_info:
        # Judul Utama
        st.markdown(f"# {film['judul']}")

        # Judul Asli & Genre (abu-abu halus di bawah judul)
        sub_info = []
        if film.get("original_title") and film["original_title"] != film["judul"]:
            sub_info.append(film["original_title"])
        if film.get("genre"):
            sub_info.append(film["genre"])
        if sub_info:
            st.caption(" • ".join(sub_info))

        # Label Status Rating (seperti "🏷️ Biasa saja" pada referensi UI)
        label_status = _kategori_rating(film["rating"])
        st.markdown(f"🏷️ **{label_status}**")

        # 3 Kolom Metrik: Tahun | Durasi | Rating (persis sejajar 3 kolom)
        m1, m2, m3 = st.columns(3)
        m1.metric("Tahun", str(film["tahun"]) if film["tahun"] else "-")
        m2.metric("Durasi", f"{film['durasi']} menit" if film["durasi"] else "-")
        skor_persen = int(round(film["rating"] * 10))
        m3.metric("Rating TMDB", f"{skor_persen}% ({film['rating']}/10)")

        # Sutradara & Produser
        st.write(f"**Sutradara:** {film.get('sutradara', '-')}")
        st.write(f"**Produser:** {film.get('produser', '-')}")

        # Bagian Sinopsis
        st.subheader("📖 Sinopsis")
        st.write(film["sinopsis"])

        # Tombol Aksi Watchlist & Review
        if show_actions:
            st.write("")
            btn_col1, btn_col2, _ = st.columns([1.2, 1.2, 1])
            watchlist = st.session_state.get("watchlist", [])
            sudah_tersimpan = any(w["id"] == film["id"] for w in watchlist)

            with btn_col1:
                label_wl = "✔️ Di Watchlist" if sudah_tersimpan else "🔖 + Watchlist"
                if st.button(
                    label_wl,
                    key=f"{key_prefix}_wl_{film['id']}",
                    disabled=sudah_tersimpan,
                    use_container_width=True,
                ):
                    st.session_state.watchlist.append(film)
                    st.toast(f"'{film['judul']}' ditambahkan ke Watchlist!")
                    st.rerun()

            with btn_col2:
                if st.button(
                    "📝 Buka Review",
                    key=f"{key_prefix}_rev_{film['id']}",
                    use_container_width=True,
                ):
                    st.session_state.selected_movie = film
                    st.toast(f"'{film['judul']}' dipilih! Buka tab 'Halaman Review Film'.")

    st.divider()