# 🎬 CineMatch — "Connecting you to the right story."

Proyek Besar Praktikum Algoritma dan Struktur Data — **Kelompok 6** (Fakultas Teknologi Informasi, Universitas Kristen Duta Wacana).

## Pembagian Tugas & Struktur Multi-File
```text
CineMatch_Project/
├── app.py                      # Entry point utama Streamlit (Sidebar Filter & 3 Tab Navigasi)
├── requirements.txt            # Daftar library Python
├── .gitignore                  # Melindungi .streamlit/secrets.toml agar tidak ter-upload ke GitHub
├── .streamlit/
│   ├── config.toml             # Konfigurasi tema warna terang sesuai wireframe proposal
│   └── secrets.toml.example    # Template API Key (TMDB & Gemini)
├── services/
│   ├── tmdb_service.py         # Integrasi TMDB API (/search, /discover, /credits) & Dictionary Cache
│   └── ai_service.py           # Integrasi Google Gemini API (gemini-2.5-flash)
├── utils/
│   ├── dsa_helpers.py          # Struktur Data (Stack LIFO, Dict Counter) & Algoritma (Searching, Selection Sort)
│   └── export_service.py       # Visualisasi Plotly (Line Chart Durasi Bulanan & Pie Chart Genre) + Ekspor PDF
└── ui/
    ├── tab_homepage.py         # [Kevin Ariel Solomon - 71251208] Tab Homepage (AI Mood Matcher & Katalog)
    ├── tab_watchlist.py        # [Agatha Sabda Alethea Prabawa - 71251218] Tab Watchlist (Metrik, Grafik & Export PDF)
    └── tab_review.py           # [Jannet Theodora - 71251173] Tab Review Film (Form Review, Other Reviews & AI)
```

## Cara Menjalankan di Lokal
1. Instal seluruh modul:
   ```bash
   pip install -r requirements.txt
   ```
2. Salin `.streamlit/secrets.toml.example` menjadi `.streamlit/secrets.toml` dan masukkan `TMDB_API_KEY` serta `GEMINI_API_KEY`.
3. Jalankan aplikasi:
   ```bash
   python -m streamlit run app.py
   ```
