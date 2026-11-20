from concurrent.futures import ThreadPoolExecutor
import requests
import streamlit as st

GENRE_MAP = {
    "Action": 28,
    "Adventure": 12,
    "Animation": 16,
    "Comedy": 35,
    "Crime": 80,
    "Documentary": 99,
    "Drama": 18,
    "Family": 10751,
    "Fantasy": 14,
    "History": 36,
    "Horror": 27,
    "Music": 10402,
    "Mystery": 9648,
    "Romance": 10749,
    "Science Fiction": 878,
    "Thriller": 53,
    "War": 10752,
    "Western": 37,
}
ID_TO_GENRE = {v: k for k, v in GENRE_MAP.items()}


def format_durasi(menit: int) -> str:
    """Mengubah durasi menit menjadi format jam & menit seperti di wireframe (contoh: 1h 49m)."""
    if not menit or menit <= 0:
        return "-"
    jam = menit // 60
    sisa_menit = menit % 60
    if jam > 0:
        return f"{jam}h {sisa_menit:02d}m"
    return f"{sisa_menit}m"


def _bangun_auth_tmdb(api_key: str) -> tuple[dict, dict]:
    """
    Mendukung otomatis baik TMDB API Key (v3 auth, ~32 karakter)
    maupun TMDB API Read Access Token (v4 Bearer JWT, diawali 'eyJ...').
    """
    key_bersih = (api_key or "").strip()
    headers = {"accept": "application/json"}
    params = {}

    if key_bersih.startswith("eyJ") or len(key_bersih) > 45:
        headers["Authorization"] = f"Bearer {key_bersih}"
    else:
        params["api_key"] = key_bersih

    return headers, params


def _fetch_detail_api(movie_id: int, api_key: str) -> tuple[int, dict]:
    """Mengambil detail tambahan film (durasi/runtime, backdrop, sutradara, produser)."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    headers, params = _bangun_auth_tmdb(api_key)
    params["append_to_response"] = "credits"

    try:
        res = requests.get(url, headers=headers, params=params, timeout=12).json()
    except Exception:
        res = {}

    runtime = res.get("runtime") or 0
    backdrop = res.get("backdrop_path")
    original_title = res.get("original_title", "")

    crew = res.get("credits", {}).get("crew", [])
    directors = [c["name"] for c in crew if c.get("job") == "Director"]
    producers = [c["name"] for c in crew if c.get("job") == "Producer"]

    detail = {
        "durasi": runtime,
        "original_title": original_title,
        "backdrop_url": f"https://image.tmdb.org/t/p/w1280{backdrop}" if backdrop else None,
        "sutradara": ", ".join(directors[:2]) if directors else "Tidak diketahui",
        "produser": ", ".join(producers[:2]) if producers else "Tidak diketahui",
    }
    return movie_id, detail


def ambil_katalog_tmdb(keyword: str, genres: list, api_key: str) -> list:
    """
    Mengambil daftar film dari TMDB API (/search/movie atau /discover/movie)
    dan menyimpannya dalam struktur data List of Dictionaries dengan Dictionary cache.
    """
    st.session_state["tmdb_error"] = None

    if not api_key or "ISI_TMDB_API_KEY" in api_key:
        st.session_state["tmdb_error"] = (
            "TMDB_API_KEY belum diisi di `.streamlit/secrets.toml`. "
            "Salin `.streamlit/secrets.toml.example` menjadi `.streamlit/secrets.toml` dan isi API Key kamu."
        )
        return []

    cache = st.session_state.setdefault("api_cache", {})
    detail_cache = st.session_state.setdefault("detail_cache", {})
    cache_key = f"{keyword.strip().lower()}|{','.join(sorted(genres))}"

    if cache_key in cache and len(cache[cache_key]) > 0:
        return cache[cache_key]

    genre_ids = [GENRE_MAP[g] for g in genres if g in GENRE_MAP]
    headers, params = _bangun_auth_tmdb(api_key)

    if keyword.strip():
        url = "https://api.themoviedb.org/3/search/movie"
        params.update({
            "query": keyword.strip(),
            "language": "en-US",
            "include_adult": "false",
        })
    else:
        url = "https://api.themoviedb.org/3/discover/movie"
        params.update({
            "language": "en-US",
            "sort_by": "popularity.desc",
            "vote_count.gte": 100,
            "include_adult": "false",
        })
        if genre_ids:
            params["with_genres"] = ",".join(map(str, genre_ids))

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        data_json = resp.json()
    except requests.exceptions.Timeout:
        st.session_state["tmdb_error"] = (
            "Koneksi ke server TMDB API timeout. Periksa koneksi internet atau aktifkan DNS 1.1.1.1 "
            "jika provider internet memblokir akses ke api.themoviedb.org."
        )
        return []
    except Exception as e:
        st.session_state["tmdb_error"] = f"Gagal terhubung ke TMDB API: {e}"
        return []

    if resp.status_code != 200 or data_json.get("success") is False:
        pesan_tmdb = data_json.get("status_message", f"HTTP {resp.status_code}")
        st.session_state["tmdb_error"] = (
            f"TMDB API menolak permintaan ({pesan_tmdb}). "
            "Pastikan TMDB_API_KEY di `.streamlit/secrets.toml` sudah benar."
        )
        return []

    results = data_json.get("results", [])[:15]
    if not results:
        return []

    missing_ids = [item["id"] for item in results if item.get("id") not in detail_cache]
    if missing_ids:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(_fetch_detail_api, mid, api_key) for mid in missing_ids]
            for fut in futures:
                mid, det = fut.result()
                detail_cache[mid] = det

    katalog = []
    for item in results:
        movie_id = item.get("id")
        rilis = item.get("release_date", "")
        tahun = int(rilis[:4]) if len(rilis) >= 4 and rilis[:4].isdigit() else 0
        rating_10 = round(float(item.get("vote_average", 0.0)), 1)
        rating_persen = int(round(rating_10 * 10))
        item_gids = item.get("genre_ids", [])
        nama_genres = [ID_TO_GENRE[g] for g in item_gids if g in ID_TO_GENRE]
        poster = item.get("poster_path")
        detail = detail_cache.get(movie_id, {})
        durasi_mnt = detail.get("durasi", 0)

        katalog.append({
            "id": movie_id,
            "judul": item.get("title", "Tanpa Judul"),
            "original_title": detail.get("original_title") or item.get("original_title", ""),
            "tahun": tahun,
            "rating": rating_10,
            "rating_persen": rating_persen,
            "durasi": durasi_mnt,
            "durasi_str": format_durasi(durasi_mnt),
            "genre": "/".join(nama_genres) if nama_genres else "General",
            "genre_list": nama_genres,
            "sutradara": detail.get("sutradara", "Tidak diketahui"),
            "produser": detail.get("produser", "Tidak diketahui"),
            "sinopsis": item.get("overview") or "Sinopsis belum tersedia.",
            "poster_url": f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
            "backdrop_url": detail.get("backdrop_url"),
        })

    cache[cache_key] = katalog
    return katalog
