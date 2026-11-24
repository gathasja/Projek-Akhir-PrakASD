import json
import re
import requests
import streamlit as st

DAFTAR_PROVIDER = [
    {
        "nama": "Groq",
        "secret_key": "GROQ_API_KEY",
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
    },
    {
        "nama": "OpenRouter",
        "secret_key": "OPENROUTER_API_KEY",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "models": ["openrouter/free", "google/gemma-3-27b-it:free"],
    },
]


def _ambil_secret(nama_key: str) -> str:
    """Membaca API Key dari st.secrets secara aman."""
    try:
        return str(st.secrets.get(nama_key, "")).strip()
    except Exception:
        return ""


def _panggil_multi_ai(prompt: str) -> tuple[bool, str, str]:
    """
    Mencoba Groq terlebih dahulu, lalu otomatis pindah ke OpenRouter jika gagal/sibuk.
    Mengembalikan tuple: (berhasil: bool, teks_jawaban: str, label_provider: str)
    """
    error_per_provider = []
    ada_key_valid = False

    for provider in DAFTAR_PROVIDER:
        api_key = _ambil_secret(provider["secret_key"])
        if not api_key or "tempel_api_key" in api_key or "ISI_" in api_key:
            continue

        ada_key_valid = True
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if provider["nama"] == "OpenRouter":
            headers["HTTP-Referer"] = "http://localhost:8501"
            headers["X-Title"] = "CineMatch App"

        error_provider_ini = ""

        for model in provider["models"]:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Kamu adalah asisten kurator film di aplikasi CineMatch. "
                            "Selalu balas HANYA dengan JSON valid sesuai format yang diminta, "
                            "tanpa teks pembuka atau penutup di luar JSON."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 1100,
            }

            try:
                res = requests.post(provider["url"], headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices") or []
                    pesan = choices[0].get("message", {}) if choices else {}
                    teks = (pesan.get("content") or "").strip()
                    if teks:
                        label = f"*(⚡ Dijawab oleh **{provider['nama']}** — `{model}`)*"
                        return True, teks, label
                    error_provider_ini = f"{provider['nama']} ({model}): Respons kosong dari model"
                else:
                    detail_err = res.text[:120].replace("\n", " ")
                    error_provider_ini = f"{provider['nama']} ({model}): HTTP {res.status_code} ({detail_err})"
            except Exception as e:
                error_provider_ini = f"{provider['nama']} ({model}): {e}"

        if error_provider_ini:
            error_per_provider.append(error_provider_ini)

    if not ada_key_valid:
        return (
            False,
            "⚠️ `GROQ_API_KEY` maupun `OPENROUTER_API_KEY` belum diisi di file `.streamlit/secrets.toml`.",
            "",
        )

    ringkasan_err = " | ".join(error_per_provider)
    return (
        False,
        f"⏳ Semua layanan AI (Groq & OpenRouter) sedang sibuk sementara ({ringkasan_err}). Coba klik tombol lagi.",
        "",
    )


def _parse_respons_rekomendasi(teks_mentah: str, label_provider: str) -> dict:
    """Memisahkan teks penjelasan dan daftar judul film dari respons JSON AI."""
    bersih = re.sub(r"^```(?:json)?\s*|\s*```$", "", teks_mentah.strip(), flags=re.IGNORECASE)
    awal = bersih.find("{")
    akhir = bersih.rfind("}")

    if awal != -1 and akhir != -1 and akhir > awal:
        try:
            obj = json.loads(bersih[awal : akhir + 1])
            penjelasan = str(obj.get("penjelasan", "")).strip()
            daftar_film = obj.get("daftar_film") or []
            if penjelasan:
                return {
                    "sukses": True,
                    "penjelasan": f"{penjelasan}\n\n{label_provider}",
                    "daftar_film": daftar_film if isinstance(daftar_film, list) else [],
                }
        except Exception:
            pass

    # Fallback jika model tidak mengembalikan JSON murni
    kandidat_judul = []
    for judul, tahun in re.findall(r"\*\*([^*(\n]+?)\s*\((\d{4})\)\*\*", teks_mentah):
        kandidat_judul.append({"judul": judul.strip(), "tahun": int(tahun)})

    return {
        "sukses": True,
        "penjelasan": f"{teks_mentah}\n\n{label_provider}",
        "daftar_film": kandidat_judul[:3],
    }


def rekomendasi_mood_ai(mood_teks: str) -> dict:
    """
    Merekomendasikan 3 film terbaik berdasarkan prompt pengguna (tanpa melihat filter sidebar)
    serta mengembalikan daftar judul resminya agar bisa langsung ditampilkan sebagai kartu katalog TMDB.
    """
    prompt = (
        f'Suasana hati (mood), tema cerita, atau kriteria film yang dicari pengguna: "{mood_teks}"\n\n'
        "Tugasmu:\n"
        "1. Pilih 3 film terbaik yang paling cocok dengan permintaan pengguna (bebas dari seluruh katalog film dunia, tidak terikat filter tertentu).\n"
        "2. Balas HANYA dengan struktur JSON valid persis seperti contoh berikut:\n"
        "{\n"
        '  "penjelasan": "Tulis penjelasan rekomendasi 3 film tersebut dalam Bahasa Indonesia yang menarik, rapi dengan poin bernomor (judul, genre, sinopsis singkat tanpa spoiler berat, dan alasan kecocokannya).",\n'
        '  "daftar_film": [\n'
        '    {"judul": "Official English/International Movie Title 1", "tahun": 2005},\n'
        '    {"judul": "Official English/International Movie Title 2", "tahun": 2019},\n'
        '    {"judul": "Official English/International Movie Title 3", "tahun": 1995}\n'
        "  ]\n"
        "}\n"
        "Pastikan nilai 'judul' pada 'daftar_film' menggunakan judul resmi internasional/bahasa Inggris film tersebut agar akurat saat dicari di database TMDB."
    )

    sukses, teks_mentah, label_provider = _panggil_multi_ai(prompt)
    if not sukses:
        return {"sukses": False, "penjelasan": teks_mentah, "daftar_film": []}

    return _parse_respons_rekomendasi(teks_mentah, label_provider)