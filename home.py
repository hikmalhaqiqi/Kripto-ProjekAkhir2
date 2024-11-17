import streamlit as st
from streamlit_option_menu import option_menu  # Import untuk sidebar menu
import main, akun, input  # Pastikan file main.py, akun.py, dan input.py ada di folder yang sama

st.set_page_config(page_title="Multi Page App")  # Menyeting judul halaman

class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title="Home",  # Judul menu di sidebar
                options=["Login/Register", "Input Data", "Akun"],  # Opsi menu yang ditampilkan di sidebar
                default_index=0,  # Indeks default saat aplikasi pertama kali dimuat
            )
        
        # Jalankan fungsi sesuai dengan menu yang dipilih
        if app == "Login/Register":
            main.app()  # Pastikan Anda memiliki fungsi app() di main.py
        elif app == "Input Data":
            input.app()  # Pastikan Anda memiliki fungsi app() di input.py
        elif app == "Akun":
            akun.app()  # Pastikan Anda memiliki fungsi app() di akun.py


# Menambahkan dan menjalankan aplikasi
app = MultiApp()
app.add_app("main", main.app)
app.add_app("input", input.app)
app.add_app("akun", akun.app)
app.run()
