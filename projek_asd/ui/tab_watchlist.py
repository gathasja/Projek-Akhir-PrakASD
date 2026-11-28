from datetime import date, datetime
import streamlit as st
from utils.export_service import (
    buat_grafik_durasi_bulanan,
    buat_grafik_genre_pie,
    ekspor_ke_pdf,
)


def _parse_tanggal_item(item: dict, fallback_bulan: str) -> date:
    """Mengambil objek date dari item watchlist/watched, dengan fallback aman."""
    raw_tgl = item.get("tanggal_tonton")
    if isinstance(raw_tgl, date) and not isinstance(raw_tgl, datetime):
        return raw_tgl
    if isinstance(raw_tgl, datetime):
        return raw_tgl.date()
    if isinstance(raw_tgl, str) and raw_tgl.strip():
        try:
            return datetime.strptime(raw_tgl.strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            pass

    label_bulan = item.get("bulan_tonton") or fallback_bulan
    for fmt in ("%b %Y", "%B %Y"):
        try:
            return datetime.strptime(label_bulan.strip(), fmt).date().replace(day=1)
        except ValueError:
            continue

    return date.today()


def render_tab_watchlist():
    """Merender Tab Watchlist: metrik, grafik, daftar belum/sudah ditonton, dan tombol ekspor PDF."""
    st.session_state.setdefault("watchlist", [])
    st.session_state.setdefault("watched_films", [])
    wl = st.session_state["watchlist"]
    watched = st.session_state["watched_films"]

    if not wl and not watched:
        st.info("Daftar Watchlist kamu masih kosong. Klik tombol **+ Watchlist** pada film di tab **Homepage**.")
        return

    semua_film = wl + watched

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

    bulan_default = datetime.now().strftime("%b %Y")
    with st.container(border=True):
        st.subheader(f"My Watchlist ({len(wl)})")
        if not wl:
            st.caption("Semua film di watchlist sudah selesai ditonton!")
        else:
            for idx, item in enumerate(wl):
                col_item, col_tgl, col_done, col_del = st.columns([3.4, 1.45, 1.3, 0.9])
                with col_item:
                    st.markdown(
                        f"**{idx + 1}. {item['judul']}** | {item['genre']} | "
                        f"{item['durasi_str']} | **{item['rating_persen']}%**"
                    )
                with col_tgl:
                    tgl_saat_ini = _parse_tanggal_item(item, bulan_default)
                    tgl_pilih = st.date_input(
                        "Tanggal Tonton",
                        value=tgl_saat_ini,
                        min_value=date(1950, 1, 1),
                        max_value=date(2035, 12, 31),
                        key=f"tgl_wl_{idx}_{item['id']}",
                        label_visibility="collapsed",
                    )
                    tgl_str_baru = tgl_pilih.strftime("%Y-%m-%d")
                    bulan_str_baru = tgl_pilih.strftime("%b %Y")
                    if (
                        item.get("tanggal_tonton") != tgl_str_baru
                        or item.get("bulan_tonton") != bulan_str_baru
                    ):
                        st.session_state["watchlist"][idx]["tanggal_tonton"] = tgl_str_baru
                        st.session_state["watchlist"][idx]["bulan_tonton"] = bulan_str_baru
                        st.rerun()
                with col_done:
                    if st.button(
                        "✅ Sudah Ditonton",
                        key=f"done_wl_{idx}_{item['id']}",
                        type="primary",
                        use_container_width=True,
                    ):
                        film_selesai = st.session_state["watchlist"].pop(idx)
                        tgl_selesai = _parse_tanggal_item(film_selesai, bulan_default)
                        film_selesai["tanggal_tonton"] = tgl_selesai.strftime("%Y-%m-%d")
                        film_selesai["bulan_tonton"] = tgl_selesai.strftime("%b %Y")
                        st.session_state["watched_films"].append(film_selesai)
                        st.toast(f"'{film_selesai['judul']}' dipindahkan ke Film yang sudah ditonton!")
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_wl_{idx}_{item['id']}", use_container_width=True):
                        st.session_state["watchlist"].pop(idx)
                        st.rerun()

    st.write("")

    with st.container(border=True):
        st.subheader(f"🎬 Film yang sudah ditonton ({len(watched)})")
        if not watched:
            st.caption("Belum ada film yang ditandai selesai ditonton. Klik tombol **✅ Sudah Ditonton** pada daftar di atas.")
        else:
            for idx, item in enumerate(watched):
                col_item, col_tgl, col_undo, col_del = st.columns([3.5, 1.4, 1.25, 0.9])
                with col_item:
                    st.markdown(
                        f"✔️ **{idx + 1}. {item['judul']}** | {item['genre']} | "
                        f"{item['durasi_str']} | **{item['rating_persen']}%**"
                    )
                with col_tgl:
                    tgl_tampil = item.get("tanggal_tonton") or item.get("bulan_tonton", bulan_default)
                    st.caption(f"📅 {tgl_tampil}")
                with col_undo:
                    if st.button(
                        "↩️ Batal",
                        key=f"undo_watched_{idx}_{item['id']}",
                        use_container_width=True,
                    ):
                        film_kembali = st.session_state["watched_films"].pop(idx)
                        st.session_state["watchlist"].append(film_kembali)
                        st.toast(f"'{film_kembali['judul']}' dikembalikan ke My Watchlist.")
                        st.rerun()
                with col_del:
                    if st.button("Delete", key=f"del_watched_{idx}_{item['id']}", use_container_width=True):
                        st.session_state["watched_films"].pop(idx)
                        st.rerun()

    st.write("")

    col_pdf, _ = st.columns([1.4, 3.6])
    with col_pdf:
        if st.button("📄 Export PDF", type="primary", use_container_width=True):
            st.info("🛠️ Tahap 1 (UI/UX): Fitur Export PDF akan diintegrasikan pada Tahap 4.")