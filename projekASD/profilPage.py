import streamlit as st

import streamlit as st

if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.switch_page("loginPage.py")

st.title("My Profile")
# Menampilkan username yang sedang aktif
st.info(f"Username aktif saat ini: {st.session_state['username']}")

st.subheader("Form Ubah Username & Password")
new_username = st.text_input("Username Baru", value=st.session_state['username'])
new_password = st.text_input("Password Baru", st.session_state['password'])

if st.button("Ubah"):
    if new_username.strip() == "":
        st.error("Username tidak boleh kosong!")
    else:
        st.session_state['username'] = new_username
        if new_password.strip() != "":
            st.session_state['password'] = new_password
        
        st.success("Profile berhasil diperbarui!")
        st.switch_page("homepage.py")
