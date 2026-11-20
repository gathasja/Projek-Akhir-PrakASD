import streamlit as st

# username = "admin"
# password = "password"
if 'username' not in st.session_state:
    st. session_state['username'] = "admin"
if 'password' not in st.session_state:
    st.session_state[ 'password' ] = "password"
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

st.title("Welcome to CineMatch!")
st.write("We connect you to the right stories.")
st.divider()
st.write("Enter your credentials to login.")

col1, col2 = st.columns(2)
with col1:
    st.image(
        "cat.jpg"
    )
with col2:
    username_input = st.text_input("Username")
    password_input = st.text_input("Password", type="password")

    if st.button( "Login"):
        if username_input == st.session_state['username'] and password_input == st.session_state[ 'password' ]:
            st.session_state['logged_in' ] = True
            st.switch_page("homepage.py")
        else:
            st.error("Login gagal. Silakan coba lagi.")

    if st.session_state['logged_in' ]:
        st.switch_page("homepage.py")
