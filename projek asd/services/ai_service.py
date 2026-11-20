from google import genai


def get_ai_client(api_key: str):
    return genai.Client(api_key=api_key)


def rekomendasi_mood_ai(daftar_film: list, mood_teks: str, api_key: str) -> str:
    """
    Tugas AI 1 & 2 (Tabel 2.3 Proposal):
    - Merekomendasikan film terbaik berdasarkan suasana hati (mood) atau tema cerita pengguna.
    - Menjelaskan alasan personal kecocokan alur cerita film dengan kebutuhan pengguna.
    """
    if not api_key or "ISI_GEMINI_API_KEY" in api_key:
        return "⚠️ GEMINI_API_KEY belum diisi di file `.streamlit/secrets.toml`."

    client = get_ai_client(api_key)
    kandidat = "\n".join([
        f"- {f['judul']} ({f['tahun']}) | Genre: {f['genre']} | Durasi: {f['durasi_str']} | "
        f"Rating: {f['rating_persen']}% ({f['rating']}/10)\n  Sinopsis: {f['sinopsis']}"
        for f in daftar_film[:12]
    ])

    prompt = f"""
    Kamu adalah asisten kurator film di aplikasi CineMatch ("Connecting you to the right story").
    Suasana hati (mood) atau tema cerita yang diinginkan pengguna:
    "{mood_teks}"

    Berikut adalah kandidat film dari katalog yang sudah difilter dari TMDB:
    {kandidat}

    Tugasmu:
    1. Pilih maksimal 3 film TERBAIK dari daftar kandidat di atas yang paling sesuai dengan keinginan pengguna.
    2. Jelaskan secara personal dan menarik mengapa alur cerita film tersebut cocok dengan kebutuhan pengguna (dalam Bahasa Indonesia).
    3. Jangan merekomendasikan film di luar daftar kandidat di atas.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gagal menghubungi Gemini AI: {e}"


def analisis_review_ai(film: dict, pertanyaan_user: str, api_key: str) -> str:
    """
    Tugas AI 3 (Tabel 2.3 Proposal):
    - Menganalisis daya tarik film dan menjawab pertanyaan spesifik pengguna pada Halaman Review Film.
    """
    if not api_key or "ISI_GEMINI_API_KEY" in api_key:
        return "⚠️ GEMINI_API_KEY belum diisi di file `.streamlit/secrets.toml`."

    client = get_ai_client(api_key)
    tambahan_tanya = (
        f'3. Jawab pertanyaan spesifik pengguna berikut dengan jelas: "{pertanyaan_user}"'
        if pertanyaan_user.strip()
        else ""
    )

    prompt = f"""
    Kamu adalah asisten kurator dan pengulas film di aplikasi CineMatch. Analisis film berikut dalam Bahasa Indonesia:
    - Judul: {film['judul']} ({film['tahun']})
    - Genre: {film['genre']}
    - Durasi: {film['durasi_str']} ({film['durasi']} menit)
    - Rating TMDB: {film['rating_persen']}% ({film['rating']}/10)
    - Sutradara: {film['sutradara']} | Produser: {film['produser']}
    - Sinopsis: {film['sinopsis']}

    Berikan ulasan terstruktur namun ringkas meliputi:
    1. Daya tarik utama dan nuansa cerita film ini (tanpa spoiler berat).
    2. Tipe penonton yang paling cocok menikmati film ini.
    {tambahan_tanya}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gagal memuat analisis AI: {e}"