# def main():
#     print("Hello from projekasd!")


# if __name__ == "__main__":
#     main()

import streamlit as st

# Inisialisasi default session state agar tidak error saat pertama kali dibuka
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Daftarkan semua file halaman yang sejajar dengan main.py
login_page = st.Page("loginPage.py", title="Login")
home_page = st.Page("homepage.py", title="Dashboard")
profil_page = st.Page("profilPage.py", title="Profil")

# Taruh login_page di urutan pertama agar menjadi halaman awal
pg = st.navigation([login_page, home_page, profil_page])
pg.run()
