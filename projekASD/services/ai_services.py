from google import genai


def get_ai_client(api_key: str):
    return genai.Client(api_key=api_key)


def rekomendasi_mood_ai(daftar_film: list, mood_teks: str, api_key: str) -> str:
    """
    Mengirim daftar kandidat film hasil filter TMDB dan input mood pengguna ke Gemini AI
    untuk menghasilkan rekomendasi personal beserta alasan kecocokan cerita.
    """
    client = get_ai_client(api_key)
    kandidat = "\n".join([
        f"- {f['judul']} ({f['tahun']}) | Genre: {f['genre']} | Durasi: {f['durasi']} mnt | "
        f"Rating: {f['rating']}/10 | Sutradara: {f['sutradara']}\n  Sinopsis: {f['sinopsis']}"
        for f in daftar_film[:10]
    ])

    prompt = f"""
    Kamu adalah asisten kurator film di aplikasi CineMatch ("Connecting you to the right story").
    Suasana hati / tema cerita yang diinginkan pengguna saat ini:
    "{mood_teks}"

    Berikut adalah kandidat film dari katalog yang sudah difilter pengguna:
    {kandidat}

    Tugasmu:
    1. Pilih maksimal 3 film TERBAIK dari daftar kandidat di atas yang paling cocok dengan keinginan pengguna.
    2. Jelaskan secara personal dan menarik mengapa alur cerita serta suasana film tersebut cocok untuk pengguna (dalam Bahasa Indonesia).
    3. Jangan merekomendasikan judul film di luar daftar kandidat di atas.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gagal menghubungi Gemini AI: {e}"


def analisis_review_ai(film: dict, pertanyaan_user: str, api_key: str) -> str:
    """
    Menganalisis daya tarik film pada Halaman Review Film dan menjawab pertanyaan spesifik pengguna.
    """
    client = get_ai_client(api_key)
    tambahan_tanya = (
        f'3. Jawab pertanyaan spesifik pengguna berikut secara jelas: "{pertanyaan_user}"'
        if pertanyaan_user.strip()
        else ""
    )

    prompt = f"""
    Kamu adalah kritikus dan kurator film di aplikasi CineMatch. Analisis film berikut dalam Bahasa Indonesia:
    - Judul: {film['judul']} ({film['tahun']})
    - Genre: {film['genre']}
    - Durasi: {film['durasi']} menit
    - Rating TMDB: {film['rating']}/10
    - Sutradara: {film['sutradara']} | Produser: {film['produser']}
    - Sinopsis: {film['sinopsis']}

    Berikan ulasan ringkas dan terstruktur meliputi:
    1. Daya tarik utama dan nuansa cerita (tanpa spoiler berat).
    2. Rekomendasi tipe penonton yang akan menikmati film ini.
    {tambahan_tanya}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gagal memuat analisis AI: {e}"