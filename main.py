import streamlit as st
import sqlite3
import hashlib

def app():
    
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

   # Fungsi untuk mendaftar pengguna baru
    def register_user(username, password):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''create table if not exists user (id integer primary key AUTOINCREMENT, username text, password text)''')
                cursor.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                st.success("Pendaftaran berhasil!")
            except sqlite3.IntegrityError:
                st.error("Nama pengguna sudah terdaftar!")
            except sqlite3.Error as e:
                st.error(f"Error saat mendaftarkan pengguna: {e}")
            finally:
                cursor.close()
                conn.close()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Fungsi untuk login
    def login():
        st.session_state.logged_in = True

    # Fungsi untuk logout
    def logout():
        st.session_state.logged_in = False
    
    def connect_db():
        try:
            # Menggunakan SQLite sebagai database
            conn = sqlite3.connect('pt_db.db')
            return conn
        except sqlite3.Error as e:
            st.error(f"Gagal terhubung ke database: {e}")
            return None

     # Fungsi untuk memverifikasi login pengguna
    def verify_login(username, password):
        conn = connect_db()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT * FROM user WHERE username = ? AND password = ?", (username, password))
                user = cursor.fetchone()
                return user
            except sqlite3.Error as e:
                st.error(f"Error saat memverifikasi login: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        return None

    if st.session_state.logged_in:
        st.title("Anda telah login pada : ")
        user = st.session_state.username
        password = st.session_state.password
        st.text_input("Username", user, disabled=True)
        st.text_input("Password", password, type="password", disabled=True)
        if st.button('Logout'):
            st.session_state.logged_in = False
            st.write("Anda telah logout.")
    else :
    
        # Title
        st.title("Input Data PT Indah Citra")
        st.text("Gunakan username dan password dengan benar")

        col1, col2 = st.columns([1, 8])

        with col1:
            if st.button("Login"):
                st.session_state["show_login"] = True  
                st.session_state["show_register"] = False 

        with col2:
            if st.button("Register"):
                st.session_state["show_register"] = True 
                st.session_state["show_login"] = False

        # Login Popup
        if st.session_state.get("show_login", False):
            with st.form("login_form", clear_on_submit=True):
                st.markdown("<h3>Login</h3>", unsafe_allow_html=True)
                username = st.text_input("username")
                password = st.text_input("Kata Sandi", type="password")
                if st.form_submit_button("Masuk"):
                    password = hash_password(password)
                    user = verify_login(username, password)
                    if user:
                        st.success("Berhasil Login!")
                        st.session_state.show_login = False  # Tutup popup
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.password = password
                    else:
                        st.error("Nama Pengguna atau Kata Sandi salah!")

        # Register Popup
        if st.session_state.get("show_register", False):
            with st.form("register_form", clear_on_submit=True):
                st.markdown("<h3>Register</h3>", unsafe_allow_html=True)
                username = st.text_input("Nama Pengguna")
                password = st.text_input("Kata Sandi", type="password")
                confirm_password = st.text_input("Konfirmasi Kata Sandi", type="password")
                if st.form_submit_button("Daftar"):
                    if password == confirm_password:
                        password = hash_password(password)
                        register_user(username, password)
                        st.session_state.show_register = False  # Tutup popup
                    else:
                        st.error("Kata Sandi dan Konfirmasi Kata Sandi tidak cocok!")
