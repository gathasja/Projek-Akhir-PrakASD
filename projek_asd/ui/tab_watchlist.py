from datetime import datetime
import streamlit as st
from utils.export_service import (
    DAFTAR_BULAN,
    buat_grafik_durasi_bulanan,
    buat_grafik_genre_pie,
    ekspor_ke_pdf,
)


def render_tab_watchlist():
    """
    Merender Tab Watchlist:
    1. 3 Kartu Metrik: Total Films, Average Score Rating, Average Film Duration.
    2. 2 Visualisasi Data Interaktif (Line Chart Durasi Bulanan & Pie Chart Genre).
    3. Container 'My Watchlist' dengan tombol 'Sudah Ditonton' & 'Delete'.
    4. Container 'Film yang sudah ditonton' dengan tombol 'Batal' & 'Delete'.
    5. Tombol 'Export PDF' yang memuat kedua daftar film dalam tabel bertema CineMatch.
    """
    st.session_state.setdefault("watched_films", [])
    wl = st.session_state.get("watchlist", [])
    watched = st.session_state.get("watched_films", [])

    if not wl and not watched:
        st.info("Daftar Watchlist kamu masih kosong. Klik tombol **+ Watchlist** pada film di tab **Homepage**.")
        return

    semua_film = wl + watched

    # 1. 3 KOLOM METRIK RINGKASAN
    total_films = len(semua_film)
    avg_rating = sum(f["rating_persen"] for f in semua_film) / total_films
    avg_duration = int(sum(f["durasi"] for f in semua_film) / total_films)

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        with st.container(border=True):
            st.metric(
                "Total Saved & Watched",
                f"{total_films} Films",
                delta=f"{len(watched)} Sudah Ditonton",
            )
    with m2:
        with st.container(border=True):
            st.metric("Average Score Rating", f"{avg_rating:.1f}%")
    with m3:
        with st.container(border=True):
            st.metric("Average Film Duration", f"{avg_duration} mins")

    st.write("")

    # 2. 2 KOLOM VISUALISASI DATA (Line Chart Durasi Bulanan & Pie Chart Genre)
    v1, v2 = st.columns(2, gap="medium")
    with v1:
        with st.container(border=True):
            st.plotly_chart(buat_grafik_durasi_bulanan(semua_film), use_container_width=True)
    with v2:
        with st.container(border=True):
            fig_genre = buat_grafik_genre_pie(semua_film)
            if fig_genre:
                st.plotly_chart(fig_genre, use_container_width=True)
            else:
                st.caption("Data genre belum tersedia.")

    st.write("")

    # 3. CONTAINER MY WATCHLIST (BELUM DITONTON)
    bulan_default = datetime.now().strftime("%b %Y")
    with st.container(border=True):
        st.subheader(f"My Watchlist ({len(wl)})")
        if not wl:
            st.caption("Semua film di watchlist sudah selesai ditonton!")
        else:
            for idx, item in enumerate(wl):
                col_item, col_bulan, col_done, col_del = st.columns([3.6, 1.2, 1.35, 0.9])
                with col_item:
                    st.markdown(
                        f"**{idx + 1}. {item['judul']}** | {item['genre']} | "
                        f"{item['durasi_str']} | **{item['rating_persen']}%**"
                    )
                with col_bulan:
                    bulan_sekarang = item.get("bulan_tonton") or bulan_default
                    opsi_bulan = list(DAFTAR_BULAN)
                    if bulan_sekarang not in opsi_bulan:
                        opsi_bulan.append(bulan_sekarang)
                    bulan_pilih = st.selectbox(
                        "Bulan Tonton",
                        options=opsi_bulan,
                        index=opsi_bulan.index(bulan_sekarang),
                        key=f"bulan_wl_{item['id']}",
                        label_visibility="collapsed",
                    )
                    if bulan_pilih != item.get("bulan_tonton"):
                        st.session_state.watchlist[idx]["bulan_tonton"] = bulan_pilih
                        st.rerun()
                with col_done:
                    if st.button(
                        "✅ Sudah Ditonton",
                        key=f"done_wl_{item['id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        film_selesai = st.session_state.watchlist.pop(idx)
                        st.session_state.watched_films.append(film_selesai)
                        st.toast(f"'{film_selesai['judul']}' dipindahkan ke Film yang sudah ditonton!")
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_wl_{item['id']}", use_container_width=True):
                        st.session_state.watchlist.pop(idx)
                        st.rerun()

    st.write("")

    # 4. CONTAINER BARU: FILM YANG SUDAH DITONTON
    with st.container(border=True):
        st.subheader(f"🎬 Film yang sudah ditonton ({len(watched)})")
        if not watched:
            st.caption("Belum ada film yang ditandai selesai ditonton. Klik tombol **✅ Sudah Ditonton** pada daftar di atas.")
        else:
            for idx, item in enumerate(watched):
                col_item, col_bulan, col_undo, col_del = st.columns([3.8, 1.1, 1.25, 0.9])
                with col_item:
                    st.markdown(
                        f"✔️ **{idx + 1}. {item['judul']}** | {item['genre']} | "
                        f"{item['durasi_str']} | **{item['rating_persen']}%**"
                    )
                with col_bulan:
                    st.caption(f"📅 {item.get('bulan_tonton', bulan_default)}")
                with col_undo:
                    if st.button(
                        "↩️ Batal",
                        key=f"undo_watched_{item['id']}",
                        use_container_width=True,
                    ):
                        film_kembali = st.session_state.watched_films.pop(idx)
                        st.session_state.watchlist.append(film_kembali)
                        st.toast(f"'{film_kembali['judul']}' dikembalikan ke My Watchlist.")
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_watched_{item['id']}", use_container_width=True):
                        st.session_state.watched_films.pop(idx)
                        st.rerun()

    st.write("")

    # 5. TOMBOL EKSPOR: EXPORT PDF (MEMUAT WATCHLIST & FILM SUDAH DITONTON)
    col_pdf, _ = st.columns([1.4, 3.6])
    with col_pdf:
        if st.button("📄 Export PDF", type="primary", use_container_width=True):
            st.info("🛠️ Tahap 1 (UI/UX): Fitur Export PDF akan diintegrasikan pada Tahap 4.")