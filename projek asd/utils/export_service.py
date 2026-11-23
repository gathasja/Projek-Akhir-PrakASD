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


def _teks_aman(teks: str, batas: int = 0) -> str:
    """Membersihkan karakter non-latin1 dan memotong teks panjang agar rapi di dalam sel tabel."""
    bersih = str(teks).encode("latin-1", "replace").decode("latin-1")
    if batas > 0 and len(bersih) > batas:
        return bersih[: batas - 3].rstrip() + "..."
    return bersih


class _CineMatchReportPDF(FPDF):
    """Template PDF bertema CineMatch dengan latar belakang berwarna dan header/footer konsisten."""

    def header(self):
        # Latar belakang halaman lembut bernuansa Lavender/Periwinkle (#EEF1FD)
        self.set_fill_color(238, 241, 253)
        self.rect(0, 0, self.w, self.h, style="F")

        # Garis aksen Indigo di sisi paling atas halaman (#4A558F)
        self.set_fill_color(74, 85, 143)
        self.rect(0, 0, self.w, 4, style="F")

        if self.page_no() == 1:
            # Banner Header Utama pada Halaman 1
            self.set_fill_color(74, 85, 143)
            self.rect(10, 10, 190, 26, style="F")

            self.set_xy(10, 13)
            self.set_font("Helvetica", "B", 18)
            self.set_text_color(255, 255, 255)
            self.cell(190, 9, "CineMatch - Watchlist & Watched Report", align="C", ln=True)

            self.set_x(10)
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(220, 225, 250)
            self.cell(190, 6, '"Connecting you to the right story."', align="C", ln=True)

            self.set_y(41)
        else:
            self.set_y(12)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        tanggal_cetak = datetime.now().strftime("%d %b %Y, %H:%M")
        self.cell(
            0,
            6,
            f"Dicetak dari CineMatch pada {tanggal_cetak}   |   Halaman {self.page_no()}",
            align="C",
        )


def _gambar_kartu_ringkasan(pdf: _CineMatchReportPDF, wl: list, watched: list):
    """Menggambar 4 kartu metrik ringkasan di bagian atas laporan."""
    semua = wl + watched
    total = len(semua)
    avg_rating = (sum(f["rating_persen"] for f in semua) / total) if total else 0.0
    avg_durasi = int(sum(f["durasi"] for f in semua) / total) if total else 0

    kartu = [
        ("TOTAL FILM", f"{total} Film"),
        ("SUDAH DITONTON", f"{len(watched)} dari {total}"),
        ("RATA-RATA RATING", f"{avg_rating:.1f}%"),
        ("RATA-RATA DURASI", f"{avg_durasi} mnt"),
    ]

    x_awal = 10
    y_awal = pdf.get_y()
    lebar_kartu = 44.5
    tinggi_kartu = 18
    jarak = 4

    for idx, (label, nilai) in enumerate(kartu):
        x = x_awal + idx * (lebar_kartu + jarak)

        # Isi kartu (#DCE1FA) dengan border Indigo (#4A558F)
        pdf.set_fill_color(220, 225, 250)
        pdf.set_draw_color(74, 85, 143)
        pdf.set_line_width(0.35)
        pdf.rect(x, y_awal, lebar_kartu, tinggi_kartu, style="DF")

        # Strip aksen atas pada masing-masing kartu (#4F6BED)
        pdf.set_fill_color(79, 107, 237)
        pdf.rect(x, y_awal, lebar_kartu, 2.2, style="F")

        pdf.set_xy(x, y_awal + 3.8)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(74, 85, 143)
        pdf.cell(lebar_kartu, 4.5, label, align="C")

        pdf.set_xy(x, y_awal + 9.2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(lebar_kartu, 6, nilai, align="C")

    pdf.set_y(y_awal + tinggi_kartu + 7)


def _gambar_tabel_film(
    pdf: _CineMatchReportPDF,
    judul_bagian: str,
    daftar_film: list,
    warna_header: tuple[int, int, int],
    pesan_kosong: str,
):
    """Menggambar satu bagian tabel film lengkap dengan header berwarna dan baris zebra."""
    lebar_kolom = [10, 72, 44, 22, 18, 24]  # Total = 190 mm
    header_kolom = ["No", "Judul Film (Tahun)", "Genre", "Durasi", "Rating", "Bulan"]
    align_kolom = ["C", "L", "L", "C", "C", "C"]

    def _cetak_header_tabel():
        pdf.set_x(10)
        pdf.set_fill_color(*warna_header)
        pdf.set_draw_color(*warna_header)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        for lebar, teks_hdr, al in zip(lebar_kolom, header_kolom, align_kolom):
            pdf.cell(lebar, 8.5, teks_hdr, border=1, align=al, fill=True)
        pdf.ln()

    # Pastikan judul bagian + header tabel + minimal 1 baris muat di halaman aktif
    if pdf.get_y() + 26 > pdf.page_break_trigger:
        pdf.add_page()

    # Judul Bagian Tabel
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*warna_header)
    pdf.cell(190, 8, _teks_aman(f"{judul_bagian} ({len(daftar_film)} Film)"), ln=True)

    _cetak_header_tabel()

    if not daftar_film:
        pdf.set_x(10)
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(195, 203, 242)
        pdf.set_text_color(100, 116, 139)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(190, 9, _teks_aman(pesan_kosong), border=1, align="C", fill=True)
        pdf.ln(11)
        return

    bulan_default = datetime.now().strftime("%b %Y")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_draw_color(195, 203, 242)

    for idx, f in enumerate(daftar_film, start=1):
        if pdf.get_y() + 8.5 > pdf.page_break_trigger:
            pdf.add_page()
            _cetak_header_tabel()
            pdf.set_font("Helvetica", "", 9)
            pdf.set_draw_color(195, 203, 242)

        # Zebra striping: Putih bersih & Periwinkle lembut (#DCE1FA)
        if idx % 2 == 1:
            pdf.set_fill_color(255, 255, 255)
        else:
            pdf.set_fill_color(220, 225, 250)

        pdf.set_text_color(30, 41, 59)
        judul_lengkap = f"{f['judul']} ({f['tahun']})"
        nilai_baris = [
            str(idx),
            _teks_aman(judul_lengkap, batas=38),
            _teks_aman(f.get("genre", "-"), batas=23),
            _teks_aman(f.get("durasi_str", "-")),
            f"{f.get('rating_persen', 0)}%",
            _teks_aman(f.get("bulan_tonton") or bulan_default),
        ]

        pdf.set_x(10)
        for lebar, isi, al in zip(lebar_kolom, nilai_baris, align_kolom):
            pdf.cell(lebar, 8, isi, border=1, align=al, fill=True)
        pdf.ln()

    pdf.ln(6)


def ekspor_ke_pdf(watchlist: list, watched_films: list | None = None) -> bytes:
    """Mengekspor ringkasan metrik, daftar My Watchlist, dan Film yang Sudah Ditonton ke PDF."""
    watched = watched_films or []

    pdf = _CineMatchReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=10, top=12, right=10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # 1. Kartu Ringkasan Statistik
    _gambar_kartu_ringkasan(pdf, watchlist, watched)

    # 2. Tabel 1: Film yang Sudah Ditonton (Warna header Emerald Slate #2B6CB0 / #335C67)
    _gambar_tabel_film(
        pdf,
        judul_bagian="Film yang Sudah Ditonton",
        daftar_film=watched,
        warna_header=(45, 106, 94),
        pesan_kosong="Belum ada film yang ditandai sudah ditonton.",
    )

    # 3. Tabel 2: My Watchlist / Belum Ditonton (Warna header Indigo #4A558F)
    _gambar_tabel_film(
        pdf,
        judul_bagian="My Watchlist (Belum Ditonton)",
        daftar_film=watchlist,
        warna_header=(74, 85, 143),
        pesan_kosong="Semua film di watchlist sudah selesai ditonton.",
    )

    return bytes(pdf.output())