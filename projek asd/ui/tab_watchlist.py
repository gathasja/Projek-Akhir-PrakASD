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
    Merender Tab Watchlist (Tanggung Jawab Agatha Sabda Alethea Prabawa - 71251218):
    1. 3 Kartu Metrik: Total Watchlist Films, Average Score Rating, Average Film Duration.
    2. 2 Visualisasi Data Interaktif:
       - Line Chart: Rata-rata durasi film tiap bulan.
       - Pie Chart: Distribusi persentase genre yang sudah ditonton.
    3. Container My Watchlist dengan pilihan bulan tonton & tombol Delete.
    4. Satu tombol ekspor: Export PDF.
    """
    wl = st.session_state.get("watchlist", [])

    if not wl:
        st.info("Daftar Watchlist kamu masih kosong. Klik tombol **+ Watchlist** pada film di tab **Homepage**.")
        return

    # 1. 3 KOLOM METRIK RINGKASAN
    total_films = len(wl)
    avg_rating = sum(f["rating_persen"] for f in wl) / total_films
    avg_duration = int(sum(f["durasi"] for f in wl) / total_films)

    m1, m2, m3 = st.columns(3, gap="medium")
    with m1:
        with st.container(border=True):
            st.metric("Total Watchlist Films", f"{total_films} Films")
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
            st.plotly_chart(buat_grafik_durasi_bulanan(wl), use_container_width=True)
    with v2:
        with st.container(border=True):
            fig_genre = buat_grafik_genre_pie(wl)
            if fig_genre:
                st.plotly_chart(fig_genre, use_container_width=True)
            else:
                st.caption("Data genre belum tersedia.")

    st.write("")

    # 3. CONTAINER MY WATCHLIST
    bulan_default = datetime.now().strftime("%b %Y")
    with st.container(border=True):
        st.subheader("My Watchlist")
        for idx, item in enumerate(wl):
            col_item, col_bulan, col_del = st.columns([4.2, 1.3, 1.0])
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
            with col_del:
                if st.button("Delete", key=f"del_wl_{item['id']}", use_container_width=True):
                    st.session_state.watchlist.pop(idx)
                    st.rerun()

    st.write("")

    # 4. SATU TOMBOL EKSPOR: EXPORT PDF
    col_pdf, _ = st.columns([1.4, 3.6])
    with col_pdf:
        st.download_button(
            "📄 Export PDF",
            data=ekspor_ke_pdf(wl),
            file_name="CineMatch_Watchlist.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
