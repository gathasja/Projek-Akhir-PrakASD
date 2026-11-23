import streamlit as st
from services.ai_service import analisis_review_ai


def render_tab_review(katalog_final: list, gemini_api_key: str):
    """
    Merender Tab Reviews / Halaman Review Film (Tanggung Jawab Jannet Theodora - 71251173):
    1. Pemilih film dari katalog/watchlist (otomatis terisi jika user klik tombol Review di Homepage).
    2. Tampilan Poster + Detail Film + Analisis & Tanya Jawab Gemini AI.
    3. Form tulis review (Nama, Rating 0-100, Review, tombol Send).
    4. Container Other Reviews (disimpan dalam Dictionary berdasarkan movie_id).
    """
    semua_film = {f["judul"]: f for f in (katalog_final + st.session_state.get("watchlist", []))}
    if st.session_state.get("selected_movie"):
        sel = st.session_state["selected_movie"]
        semua_film[sel["judul"]] = sel

    if not semua_film:
        st.info("Belum ada film yang dimuat. Cari atau atur filter film di sidebar terlebih dahulu.")
        return

    daftar_judul = list(semua_film.keys())
    default_idx = 0
    if st.session_state.get("selected_movie") and st.session_state["selected_movie"]["judul"] in daftar_judul:
        default_idx = daftar_judul.index(st.session_state["selected_movie"]["judul"])

    judul_aktif = st.selectbox("Pilih Film untuk Diulas:", daftar_judul, index=default_idx)
    film_aktif = semua_film[judul_aktif]

    st.write("")

    # LAYOUT 2 KOLOM SESUAI WIREFRAME 3.3 PROPOSAL
    col_kiri, col_kanan = st.columns([1.05, 1.85], gap="large")

    with col_kiri:
        if film_aktif.get("poster_url"):
            st.image(film_aktif["poster_url"], use_container_width=True)
        else:
            st.info("Poster tidak tersedia")

        st.markdown(f"### {film_aktif['judul']} ({film_aktif['tahun']})")
        st.caption(f"{film_aktif['genre']} | {film_aktif['durasi_str']} | {film_aktif['rating_persen']}%")
        st.write(film_aktif["sinopsis"])

    with col_kanan:
        # FORM INPUT REVIEW PENGGUNA (Nama, Rating 0-100, Review, Send)
        with st.container(border=True):
            st.markdown("#### ✍️ Tulis Review Film")
            with st.form(key=f"form_review_{film_aktif['id']}"):
                nama_reviewer = st.text_input("Nama", placeholder="Masukkan nama kamu...")
                rating_reviewer = st.slider("Rating (0-100)", min_value=0, max_value=100, value=80)
                teks_review = st.text_area("Review", placeholder="Tulis ulasan singkat atau detail mengenai film ini...")
                kirim_review = st.form_submit_button("Send", type="primary")

                if kirim_review:
                    if not teks_review.strip():
                        st.warning("Kolom Review tidak boleh kosong.")
                    else:
                        mid = film_aktif["id"]
                        st.session_state.user_reviews.setdefault(mid, []).append({
                            "nama": nama_reviewer.strip() or "Anonymous",
                            "rating": rating_reviewer,
                            "review": teks_review.strip(),
                        })
                        st.success("Review berhasil dikirim!")

        st.write("")

        # CONTAINER OTHER REVIEWS
        with st.container(border=True):
            st.markdown("#### 💬 Other Reviews")
            mid = film_aktif["id"]
            daftar_review = st.session_state.user_reviews.get(mid, [])

            if not daftar_review:
                st.caption("Belum ada review untuk film ini. Jadilah yang pertama menulis ulasan di atas!")
            else:
                for rev in reversed(daftar_review):
                    st.markdown(f"**{rev['nama']} - {rev['rating']}%**")
                    st.write(rev["review"])
                    st.divider()

        st.write("")

        # ANALISIS & TANYA JAWAB GEMINI AI PADA HALAMAN REVIEW FILM (Tabel 2.3 Proposal)
        with st.expander("🤖 Analisis & Tanya Jawab Gemini AI seputar Film Ini", expanded=True):
            tanya_film = st.text_input(
                "Ajukan pertanyaan spesifik tentang film ini (opsional):",
                placeholder="Contoh: Apa kelebihan alur cerita film ini? Apakah cocok ditonton akhir pekan?",
                key=f"tanya_ai_{film_aktif['id']}",
            )
            if st.button("Minta Analisis Gemini AI", key=f"btn_ai_rev_{film_aktif['id']}"):
                with st.spinner("Gemini AI sedang menganalisis film..."):
                    hasil = analisis_review_ai(film_aktif, tanya_film, gemini_api_key)
                    st.info(hasil)
