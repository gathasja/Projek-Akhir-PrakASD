import streamlit as st


def render_tab_profile():
    """Merender halaman Profile untuk melihat dan memperbarui username serta password."""
    st.title("Halaman Profile")
    st.info(f"Username aktif saat ini: {st.session_state.get('username', '')}")

    st.subheader("Form Ubah Username & Password")
    new_username = st.text_input("Username Baru", value=st.session_state.get("username", ""))
    new_password = st.text_input(
        "Password Baru",
        value="",
        type="password",
        placeholder="Kosongkan jika tidak ingin mengubah password",
    )

    if st.button("Ubah", key="btn_ubah_profile", type="primary"):
        if not new_username.strip():
            st.error("Username tidak boleh kosong!")
        else:
            st.session_state["username"] = new_username.strip()
            if new_password.strip():
                st.session_state["password"] = new_password.strip()
            st.success("Profile berhasil diperbarui!")
            st.rerun()