import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("loginPage.py")

st.title("My Dashboard")
st.subheader(f"Selamat datang, {st.session_state['username']}!")
st.write("Anda telah berhasil masuk ke aplikasi ini.")
# st.button("Logout")

if st.button("Logout"):
    st.session_state['logged_in'] = False
    st.switch_page("loginPage.py")