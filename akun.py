import streamlit as st
import sqlite3
from sqlite3 import Error
from PIL import Image
import os

def app(): 
    SAVE_FOLDER = r"D:\Semester 5\1. Kriptografi\Projek2\image"
    SAVE_FOLDER2 = r"D:\Semester 5\1. Kriptografi\Projek2\doc"
    
    def connect_db():
        try:
            conn = sqlite3.connect("pt_db.db")
            return conn
        except Error as e:
            st.error(f"Gagal terhubung ke database: {e}")
            return None
   
    # Mengambil data dari db
    def get_user_info(conn, user):
        try:
            cursor = conn.cursor()
            query = "SELECT name, address, gender, birth, telephone, uploaded_img, uploaded_files FROM data_user WHERE username = ?"
            cursor.execute(query, (user,))
            result = cursor.fetchone()
            if result:
                # Menggunakan dictionary untuk hasil query
                return {
                    'name': result[0],
                    'address': result[1],
                    'gender': result[2],
                    'birth': result[3],
                    'telephone': result[4],
                    'uploaded_img': result[5],
                    'uploaded_files': result[6]
                }
            return None
        except Error as e:
            st.error(f"Terjadi kesalahan saat mengambil data: {e}")
            return None
   
    # Deskripsi Data
    def block_cipher_decrypt(text: str, key: str) -> str:
        result = []
        key_length = len(key)
        for i in range(len(text)):
            decrypted_char = (ord(text[i]) - ord(key[i % key_length]) + 256) % 256
            result.append(chr(decrypted_char))
        return ''.join(result)

    def from_hex(hex_input: str) -> str:
        result = []
        for i in range(0, len(hex_input), 2):
            byte = hex_input[i:i+2]
            result.append(chr(int(byte, 16)))
        return ''.join(result)

    def railfence_decrypt(cipher: str, key: int) -> str:   
        rail = [['\n' for _ in range(len(cipher))] for _ in range(key)]

        dir_down = None
        row, col = 0, 0

        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False

            rail[row][col] = '*'
            col += 1

            row = row + 1 if dir_down else row - 1

        index = 0
        for i in range(key):
            for j in range(len(cipher)):
                if rail[i][j] == '*' and index < len(cipher):
                    rail[i][j] = cipher[index]
                    index += 1

        result = []
        row, col = 0, 0
        for i in range(len(cipher)):
            if row == 0:
                dir_down = True
            if row == key - 1:
                dir_down = False

            if rail[row][col] != '*':
                result.append(rail[row][col])
                col += 1

            row = row + 1 if dir_down else row - 1

        return ''.join(result)

    # Mengecek apakah session sudah ada
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Fungsi untuk logout
    def logout():
        st.session_state.logged_in = False
        
    if 'input_restricted' not in st.session_state:
        st.session_state.input_restricted = False

    # Mengecek apakah pengguna sudah login
    if not st.session_state.logged_in:
        st.title("Anda belum login. Silakan login terlebih dahulu.")
    else:
        conn = connect_db()
        user = st.session_state.username
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM data_user WHERE username = ?", (user,))
            if cursor.fetchone()[0] > 0:
                st.session_state.input_restricted = True
                 
        if not st.session_state.input_restricted:
            st.title("Silahkan Menginput Data Anda")
        else:
            key = user
            key1 = 3
            conn = connect_db()
            if conn:
                user_info = get_user_info(conn, user)
                conn.close()
                
                if user_info:
                    st.write("Informasi mengenai akun:")
                    
                    # Name
                    name = user_info['name']
                    encryp = railfence_decrypt(name, key1)
                    encrypted_from_hex = from_hex(encryp)
                    decrypted_name = block_cipher_decrypt(encrypted_from_hex, key)
                    st.text_input("Nama Pengguna", decrypted_name, disabled=True)
                    
                    # Address
                    address = user_info['address']
                    encryp = railfence_decrypt(address, key1)
                    encrypted_from_hex = from_hex(encryp)
                    decrypted_address = block_cipher_decrypt(encrypted_from_hex, key)
                    st.text_input("Alamat", decrypted_address, disabled=True)
                    
                    # Gender
                    gender = user_info['gender']
                    encryp = railfence_decrypt(gender, key1)
                    encrypted_from_hex = from_hex(encryp)
                    decrypted_gender = block_cipher_decrypt(encrypted_from_hex, key)
                    st.text_input("Jenis Kelamin", decrypted_gender, disabled=True)
                    
                    # birth
                    birth = user_info['birth']
                    encryp = railfence_decrypt(birth, key1)
                    encrypted_from_hex = from_hex(encryp)
                    decrypted_birth = block_cipher_decrypt(encrypted_from_hex, key)
                    st.text_input("Tanggal Lahir", decrypted_birth, disabled=True)
                    
                    #telephone
                    telephone = user_info['telephone']
                    encryp = railfence_decrypt(telephone, key1)
                    encrypted_from_hex = from_hex(encryp)
                    decrypted_telephone = block_cipher_decrypt(encrypted_from_hex, key)
                    st.text_input("Nomor Telepon", decrypted_telephone, disabled=True)
                    
                    # Handling the profile image
                    uploaded_img_path = os.path.join(SAVE_FOLDER, user_info['uploaded_img'])
                    if uploaded_img_path:
                        if os.path.exists(uploaded_img_path):
                            # Menampilkan gambar
                            image = Image.open(uploaded_img_path)
                            st.image(image, caption="Foto Profil Anda", use_container_width=True)

                            # Menentukan MIME type berdasarkan ekstensi file
                            file_extension = uploaded_img_path.split('.')[-1].lower()
                            mime_type = None

                            if file_extension == 'jpg' or file_extension == 'jpeg':
                                mime_type = "image/jpeg"
                            elif file_extension == 'png':
                                mime_type = "image/png"
                            else:
                                mime_type = "application/octet-stream"  # Default if type is not recognized

                            # Menambahkan tombol untuk download gambar
                            with open(uploaded_img_path, "rb") as file:
                                st.download_button(
                                    label="Download Gambar Profil",
                                    data=file,
                                    file_name=user_info['uploaded_img'],
                                    mime=mime_type  # Menggunakan MIME type yang sudah ditentukan
                                )
                        else:
                            st.error(f"Gambar tidak ditemukan di path: {uploaded_img_path}")
                    else:
                        st.error("Path gambar tidak ditemukan!")
                        
                    pdf_path = os.path.join(SAVE_FOLDER2, f"protected_{user_info['uploaded_files']}")

                    # Menambahkan tombol download untuk PDF
                    if pdf_path:
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as file:
                                st.download_button(
                                    label="Download File PDF",
                                    data=file,
                                    file_name= f"protected_{user_info['uploaded_files']}",
                                    mime="pdf"
                                )
                        else:
                            st.error(f"File PDF tidak ditemukan di path: {pdf_path}")
                    else:
                        st.error("File PDF tidak ditemukan!")
        
        if st.button('Logout'):
            logout()
            st.write("Anda telah logout.")