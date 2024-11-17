import streamlit as st
import sqlite3
from sqlite3 import Error
from PIL import Image
import os
import PyPDF2

def app(): 
    
    # Save Img
    def save_image_with_shutil(uploaded_image, save_path):
    # Membuat direktori jika belum ada
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Tentukan path lengkap file gambar
        file_path = os.path.join(save_path, uploaded_image.name)
        
        # Menyimpan file gambar ke path yang ditentukan
        with open(file_path, "wb") as f:
            f.write(uploaded_image.getbuffer())
    
        st.success(f"Image saved to {file_path}")
        return file_path
    
    # Fungsi untuk menambahkan kata sandi pada file PDF
    def add_password_to_pdf(input_pdf_path, output_pdf_path, password):
        with open(input_pdf_path, 'rb') as input_pdf_file:
            pdf_reader = PyPDF2.PdfReader(input_pdf_file)
            pdf_writer = PyPDF2.PdfWriter()

            # Menambahkan halaman ke PdfWriter
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                pdf_writer.add_page(page)

            # Menambahkan kata sandi
            pdf_writer.encrypt(password)

            # Menyimpan PDF yang telah diberi kata sandi
            with open(output_pdf_path, 'wb') as output_pdf_file:
                pdf_writer.write(output_pdf_file)
            
    def save_doc_with_shutil(uploaded_file, save_path):
    # Membuat direktori jika belum ada
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Tentukan path lengkap file gambar
        file_path = os.path.join(save_path, uploaded_file.name)
        
        # Menyimpan file gambar ke path yang ditentukan
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
        st.success(f"File saved to {file_path}")
        return file_path
    
    #ENKRIPSI TEXT
    def block_cipher_encrypt(text: str, key: str) -> str:
        result = []
        key_length = len(key)
        for i in range(len(text)):
            encrypted_char = (ord(text[i]) + ord(key[i % key_length])) % 256
            result.append(chr(encrypted_char))
        return ''.join(result)

    def to_hex(input_string: str) -> str:
            return ''.join(f'{ord(c):02x}' for c in input_string)

    def railfence_encrypt(text: str, key: int) -> str:
        rail = [['\n' for _ in range(len(text))] for _ in range(key)]

        dir_down = False
        row, col = 0, 0

        for char in text:
            if row == 0 or row == key - 1:
                dir_down = not dir_down

            rail[row][col] = char
            col += 1

            row = row + 1 if dir_down else row - 1

        result = []
        for i in range(key):
            for j in range(len(text)):
                if rail[i][j] != '\n':
                    result.append(rail[i][j])

        return ''.join(result)
    
    # Fungsi untuk menyembunyikan teks ke dalam gambar
    def encode_text_in_image(image_path, text, output_path):
        # Buka gambar
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        pixels = img.load()

        # Tambahkan terminator ke teks
        text += "<<<END>>>"  # Penanda akhir teks
        binary_text = ''.join([format(ord(char), '08b') for char in text])

        # Periksa teks muat di dalam gambar
        if len(binary_text) > img.width * img.height * 3:
            raise ValueError("Teks terlalu panjang untuk disembunyikan dalam gambar ini.")

        # Encode teks ke dalam gambar
        binary_index = 0
        for y in range(img.height):
            for x in range(img.width):
                if binary_index >= len(binary_text):
                    break
                r, g, b = pixels[x, y]

                # Ubah bit terkecil dari setiap channel RGB
                r = (r & 0xFE) | int(binary_text[binary_index])  # Red
                binary_index += 1

                if binary_index < len(binary_text):
                    g = (g & 0xFE) | int(binary_text[binary_index])  # Green
                    binary_index += 1

                if binary_index < len(binary_text):
                    b = (b & 0xFE) | int(binary_text[binary_index])  # Blue
                    binary_index += 1

                # Simpan kembali nilai piksel
                pixels[x, y] = (r, g, b)

        # Simpan gambar dengan teks tersembunyi
        img.save(output_path)
        print(f"Teks berhasil disembunyikan di {output_path}")

    def connect_db():
        try:
            conn = sqlite3.connect("pt_db.db")  # Gunakan SQLite file-based DB
            return conn
        except Error as e:
            st.error(f"Gagal terhubung ke database: {e}")
            return None
    
    def input(user, name, address, gender, birth, telephone, uploaded_img, uploaded_files):
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute('''create table if not exists data_user (id integer primary key AUTOINCREMENT, username text, name text, address text, gender text,birth text, telephone text, uploaded_img text, uploaded_files text)''')
                    cursor.execute(
                        "INSERT INTO data_user (username, name, address, gender, birth, telephone, uploaded_img, uploaded_files) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (user, name, address, gender, birth, telephone, uploaded_img, uploaded_files)
                    )
                    conn.commit()
                    st.success("Data berhasil disimpan!")
                except sqlite3.IntegrityError:
                    st.error("Nama pengguna sudah terdaftar!")
                except Error as e:
                    st.error(f"Terjadi kesalahan: data tidak dapat disimpan. {e}")
                finally:
                    cursor.close()
                    conn.close()
                
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'input_restricted' not in st.session_state:
        st.session_state.input_restricted = False
    
    def logout():
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        st.title("Anda belum login. Silakan login terlebih dahulu.")
    else:
        user = st.session_state.username
        conn = connect_db() 
        if conn:
            cursor = conn.cursor()
            user = st.session_state.username
            cursor.execute('''create table if not exists data_user (id integer primary key AUTOINCREMENT, username text, name text, address text, gender text,birth text, telephone text, uploaded_img text, uploaded_files text)''')
            cursor.execute("SELECT COUNT(*) FROM data_user WHERE username = ?", (user,))
            if cursor.fetchone()[0] > 0:
                st.session_state.input_restricted = True 
                
        if st.session_state.input_restricted : 
            st.title("Anda sudah mengisi data!")
        else: 
            SAVE_FOLDER = "D:\Semester 5\1. Kriptografi\Projek2\image"
            key = user
            key1 =3
            st.title("Halaman Utama")
            st.write("Selamat datang di halaman utama setelah login!")
            with st.form("login_form", clear_on_submit=True):
                st.markdown("<h3>Input Data</h3>", unsafe_allow_html=True)
           
                #nama pengguna
                name = st.text_input("Nama Pengguna")
                encrypted_text = block_cipher_encrypt(name, key)
                hex_encrypted = to_hex(encrypted_text)
                name = railfence_encrypt(hex_encrypted, key1)
                
                #address
                address = st.text_input("Alamat")
                encrypted_text = block_cipher_encrypt(address, key)
                hex_encrypted = to_hex(encrypted_text)
                address = railfence_encrypt(hex_encrypted, key1)
                
                #gender
                gender = st.radio("Gender Anda:", ["Laki-laki", "Perempuan"])
                encrypted_text = block_cipher_encrypt(gender, key)
                hex_encrypted = to_hex(encrypted_text)
                gender = railfence_encrypt(hex_encrypted, key1)
                
                #birth
                birth = st.date_input("Tanggal lahir", value=None)
                if birth is not None:
                    # Mengonversi objek tanggal menjadi string jika birth ada
                    birth = birth.strftime('%Y-%m-%d')
                    # Proses enkripsi
                    encrypted_text = block_cipher_encrypt(birth, key)
                    hex_encrypted = to_hex(encrypted_text)
                    birth = railfence_encrypt(hex_encrypted, key1)
                    st.write("Hasil enkripsi:", birth)
                else:
                    st.warning("Silakan pilih tanggal lahir terlebih dahulu.")
                    
                #telephone
                telephone = st.text_input("Masukkan nomor telepon Anda")
                encrypted_text = block_cipher_encrypt(telephone, key)
                hex_encrypted = to_hex(encrypted_text)
                telephone = railfence_encrypt(hex_encrypted, key1)

                st.markdown("⚠️ **Hanya file dengan ukuran maksimal 10 MB yang diterima.**")
                
                uploaded_img = st.file_uploader("Unggah foto profil Anda", type=["png"], accept_multiple_files=False)
                if uploaded_img:
                    save_folder = r"D:\Semester 5\1. Kriptografi\Projek2\image" # Tentukan folder penyimpanan
                    input_image = uploaded_img  # Gambar harus berformat PNG
                    output_image = os.path.join(save_folder, f"steg_{uploaded_img.name}")

                    # Teks yang ingin disembunyikan
                    secret_text = ' | '.join([str(name), str(address), str(gender), str(birth), str(telephone)])

                    # Encode teks ke dalam gambar
                    encode_text_in_image(input_image, secret_text, output_image)
                    saved_image_path = save_image_with_shutil(uploaded_img, save_folder)
                        
                uploaded_files = st.file_uploader("Pilih CV Anda", type=["pdf"], accept_multiple_files=False)
                if uploaded_files:
                    save_folder = r"D:\Semester 5\1. Kriptografi\Projek2\doc" # Tentukan folder penyimpanan
                    saved_doc_path = save_doc_with_shutil(uploaded_files, save_folder)
                    password = user
                    output_pdf_path = os.path.join(save_folder, f"protected_{uploaded_files.name}")
                    add_password_to_pdf(saved_doc_path, output_pdf_path, password)

                submitted = st.form_submit_button("Submit")
                if submitted:
                    if not (name and address and telephone and uploaded_img and uploaded_files):
                        st.warning("Semua field dan file wajib diisi!")
                    else:
                        input(user, name, address, gender, birth, telephone, uploaded_img.name, uploaded_files.name)
                       
        col1, col2 = st.columns([7, 1]) 
        with col2:   
            if st.button('Logout'):
                logout()