# Implementasi Struktur Data & Algoritma (Tabel 2.4 Proposal CineMatch)


def filter_katalog_searching(
    katalog: list,
    genres: list,
    durasi_range: tuple,
    rating_min_persen: int,
    tahun_range: tuple,
) -> list:
    """
    Algoritma Linear Searching & Multi-Criteria Filtering pada List of Dictionaries.
    Menyaring daftar film berdasarkan Genre, Film Duration, Film Rating (%), dan Release Year.
    """
    hasil = []
    for film in katalog:
        # 1. Cek Genre
        if genres:
            if not any(g in film["genre_list"] for g in genres):
                continue

        # 2. Cek Film Duration (menit)
        if film["durasi"] > 0:
            if not (durasi_range[0] <= film["durasi"] <= durasi_range[1]):
                continue

        # 3. Cek Film Rating Minimal (skala 0-100%)
        if film["rating_persen"] < rating_min_persen:
            continue

        # 4. Cek Release Year
        if film["tahun"] > 0:
            if not (tahun_range[0] <= film["tahun"] <= tahun_range[1]):
                continue

        hasil.append(film)
    return hasil


def urutkan_katalog_selection_sort(daftar_film: list, kriteria: str) -> list:
    """
    Algoritma Selection Sort untuk mengurutkan katalog film berdasarkan kriteria pilihan pengguna.
    """
    data = daftar_film.copy()
    n = len(data)

    for i in range(n):
        idx_terpilih = i
        for j in range(i + 1, n):
            if kriteria == "Rating (Descending)":
                if data[j]["rating_persen"] > data[idx_terpilih]["rating_persen"]:
                    idx_terpilih = j
            elif kriteria == "Rating (Ascending)":
                if data[j]["rating_persen"] < data[idx_terpilih]["rating_persen"]:
                    idx_terpilih = j
            elif kriteria == "Release Year (Newest)":
                if data[j]["tahun"] > data[idx_terpilih]["tahun"]:
                    idx_terpilih = j
            elif kriteria == "Release Year (Oldest)":
                if data[j]["tahun"] < data[idx_terpilih]["tahun"]:
                    idx_terpilih = j
            elif kriteria == "Duration (Shortest)":
                if data[j]["durasi"] < data[idx_terpilih]["durasi"]:
                    idx_terpilih = j
            elif kriteria == "Duration (Longest)":
                if data[j]["durasi"] > data[idx_terpilih]["durasi"]:
                    idx_terpilih = j
            elif kriteria == "Title (A-Z)":
                if data[j]["judul"].lower() < data[idx_terpilih]["judul"].lower():
                    idx_terpilih = j

        data[i], data[idx_terpilih] = data[idx_terpilih], data[i]

    return data


def hitung_frekuensi_genre(watchlist: list) -> dict:
    """
    Struktur Data Dictionary / Counter untuk menghitung frekuensi kemunculan tiap genre
    pada Watchlist pengguna sebagai sumber data visualisasi grafik batang.
    """
    frekuensi = {}
    for film in watchlist:
        for genre in film.get("genre_list", []):
            frekuensi[genre] = frekuensi.get(genre, 0) + 1
    return frekuensi


class FilterHistoryStack:
    """
    Struktur Data Stack (LIFO - Last In First Out) untuk menyimpan riwayat parameter filter
    yang diterapkan pengguna di sidebar (tombol Save & Undo Filter).
    """

    def __init__(self, state_list: list):
        self._stack = state_list

    def push(self, filter_snapshot: dict):
        self._stack.append(filter_snapshot)

    def pop(self):
        if not self.is_empty():
            return self._stack.pop()
        return None

    def peek(self):
        if not self.is_empty():
            return self._stack[-1]
        return None

    def is_empty(self) -> bool:
        return len(self._stack) == 0

    def size(self) -> int:
        return len(self._stack)
