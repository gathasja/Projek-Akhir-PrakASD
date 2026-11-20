from datetime import datetime
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from utils.dsa_helpers import hitung_frekuensi_genre

DAFTAR_BULAN = [
    "Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026",
    "May 2026", "Jun 2026", "Jul 2026", "Aug 2026",
    "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026",
]


def _urutan_bulan(label_bulan: str) -> int:
    if label_bulan in DAFTAR_BULAN:
        return DAFTAR_BULAN.index(label_bulan)
    try:
        return int(datetime.strptime(label_bulan, "%b %Y").timestamp())
    except Exception:
        return 999


def buat_grafik_durasi_bulanan(watchlist: list):
    """
    Visualisasi 1 (Sesuai Wireframe 3.2 Proposal):
    Grafik Garis (Line Chart) menampilkan rata-rata durasi film (menit) tiap bulan.
    """
    bulan_default = datetime.now().strftime("%b %Y")
    rows = []
    for f in watchlist:
        rows.append({
            "Bulan": f.get("bulan_tonton") or bulan_default,
            "Durasi": f.get("durasi", 0),
        })

    df = pd.DataFrame(rows)
    df_bulanan = (
        df.groupby("Bulan", as_index=False)["Durasi"]
        .mean()
        .rename(columns={"Durasi": "Rata-rata Durasi (menit)"})
    )
    df_bulanan["Rata-rata Durasi (menit)"] = df_bulanan["Rata-rata Durasi (menit)"].round(1)
    df_bulanan["_sort_key"] = df_bulanan["Bulan"].apply(_urutan_bulan)
    df_bulanan = df_bulanan.sort_values("_sort_key")

    fig = px.line(
        df_bulanan,
        x="Bulan",
        y="Rata-rata Durasi (menit)",
        markers=True,
        title="Average Film Duration per Month (Line Chart)",
    )
    fig.update_traces(line=dict(color="#4F6BED", width=3), marker=dict(size=9))
    fig.update_layout(
        yaxis=dict(rangemode="tozero"),
        margin=dict(l=20, r=20, t=45, b=20),
    )
    return fig


def buat_grafik_genre_pie(watchlist: list):
    """
    Visualisasi 2 (Sesuai Wireframe 3.2 Proposal):
    Grafik Lingkaran (Pie Chart) menampilkan persentase genre film yang sudah ditonton / di Watchlist.
    """
    freq = hitung_frekuensi_genre(watchlist)
    if not freq:
        return None

    df_genre = pd.DataFrame({
        "Genre": list(freq.keys()),
        "Jumlah Film": list(freq.values()),
    }).sort_values("Jumlah Film", ascending=False)

    fig = px.pie(
        df_genre,
        names="Genre",
        values="Jumlah Film",
        title="Watched Genre Distribution (Pie Chart)",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=20, r=20, t=45, b=20))
    return fig


def ekspor_ke_pdf(watchlist: list) -> bytes:
    """Mengekspor ringkasan metrik dan daftar Watchlist ke format PDF menggunakan FPDF."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "CineMatch - My Watchlist Report", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, '"Connecting you to the right story."', ln=True, align="C")
    pdf.ln(6)

    total_film = len(watchlist)
    avg_rating = sum(f["rating_persen"] for f in watchlist) / total_film
    avg_durasi = int(sum(f["durasi"] for f in watchlist) / total_film)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(
        0,
        8,
        f"Total Films: {total_film} | Average Rating: {avg_rating:.1f}% | Average Duration: {avg_durasi} mins",
        ln=True,
    )
    pdf.ln(4)

    bulan_default = datetime.now().strftime("%b %Y")
    pdf.set_font("Helvetica", "", 10)
    for idx, f in enumerate(watchlist, start=1):
        bulan_str = f.get("bulan_tonton") or bulan_default
        baris = (
            f"{idx}. {f['judul']} ({f['tahun']}) | {f['genre']} | "
            f"{f['durasi_str']} | {f['rating_persen']}% | Bulan: {bulan_str}"
        )
        baris_aman = baris.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, baris_aman)
        pdf.ln(1)

    return bytes(pdf.output())
