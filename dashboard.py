import streamlit as st
from ultralytics import YOLO
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import requests
import time
import io
import os
import base64
from streamlit_lottie import st_lottie

# ==========================
# FUNGSI MEMUAT LOTTIE ANIMASI
# ==========================
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ==========================
# KONFIGURASI DASAR
# ==========================
st.set_page_config(page_title="Dashboard AI Futuristik", page_icon="🤖", layout="wide")

# CSS BACKGROUND ANIMASI
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 20% 20%, #00111a, #000000 90%);
    animation: bgmove 30s ease-in-out infinite alternate;
}
@keyframes bgmove {
    0% {background-position: 0% 50%;}
    100% {background-position: 100% 50%;}
}

[data-testid="stSidebar"] {
    background: rgba(0, 20, 40, 0.9);
    color: white;
}

h1, h2, h3, h4, h5, h6, p {
    color: #d4f1ff;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    background: rgba(0, 0, 0, 0.6);
    border-radius: 20px;
    box-shadow: 0 0 25px rgba(0,255,255,0.2);
    backdrop-filter: blur(12px);
}

.stButton button {
    background: linear-gradient(90deg, #00ffff, #0066ff);
    color: black !important;
    font-weight: bold;
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0,255,255,0.3);
    transition: 0.3s;
}
.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 30px rgba(0,255,255,0.6);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ==========================
# LOTTIE ANIMASI
# ==========================
col1, col2 = st.columns([1, 2])
with col1:
    lottie_ai = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_tfb3estd.json")
    if lottie_ai:
        st_lottie(lottie_ai, height=200, key="ai_anim")
with col2:
    st.title("🤖 Dashboard Deteksi Gambar Futuristik")
    st.markdown("Selamat datang di sistem deteksi cerdas dengan tampilan futuristik dan interaktif.")

st.write("---")

# ==========================
# MUSIK MELAYANG
# ==========================
music_path = "music/lostsagalobby.mp3"
if os.path.exists(music_path):
    with open(music_path, "rb") as f:
        music_data = f.read()
        audio_b64 = base64.b64encode(music_data).decode()

    music_html = f"""
    <audio id="bgMusic" loop>
        <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
    </audio>
    <div onclick="toggleMusic()" 
        style="position:fixed;bottom:25px;right:25px;
        width:60px;height:60px;border-radius:50%;
        background:linear-gradient(135deg,#00ffff,#0066ff);
        display:flex;align-items:center;justify-content:center;
        color:black;font-size:28px;cursor:pointer;
        box-shadow:0 0 15px rgba(0,255,255,0.5);z-index:9999;">
        🎵
    </div>
    <script>
    let playing = false;
    const music = document.getElementById('bgMusic');
    function toggleMusic() {{
        if (playing) {{ music.pause(); }} 
        else {{ music.play(); }}
        playing = !playing;
    }}
    </script>
    """
    st.markdown(music_html, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠️ File musik tidak ditemukan di folder 'music/'.")

# ==========================
# MENU UTAMA
# ==========================
menu = st.sidebar.radio("Navigasi", ["Beranda", "Deteksi Gambar", "Tentang"])

if menu == "Beranda":
    st.header("✨ Selamat Datang di Dashboard AI ✨")
    st.write("Gunakan menu di sisi kiri untuk mulai melakukan deteksi gambar atau pelajari lebih lanjut di bagian Tentang.")
    st.image("https://images.unsplash.com/photo-1504384308090-c894fdcc538d", use_column_width=True)

elif menu == "Deteksi Gambar":
    st.header("📸 Unggah Gambar untuk Deteksi")

    uploaded_file = st.file_uploader("Pilih gambar untuk dideteksi", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Gambar yang diunggah", use_column_width=True)

        with st.spinner("🔍 Sedang memproses..."):
            time.sleep(2)
            st.success("✅ Deteksi selesai! (simulasi)")

elif menu == "Tentang":
    st.header("ℹ️ Tentang Aplikasi")
    st.write(
        """
        Aplikasi ini dikembangkan menggunakan:
        - **Streamlit** untuk antarmuka interaktif
        - **YOLO & TensorFlow** untuk analisis visual
        - **Lottie Animations** untuk tampilan yang hidup
        - **HTML & CSS custom** untuk efek futuristik
        """
    )

# ==========================
# FOOTER
# ==========================
st.write("---")
st.markdown(
    "<div style='text-align:center;color:#00ffff;'>© 2025 Ibnu - Dashboard AI Futuristik 🚀</div>",
    unsafe_allow_html=True,
)

# ==========================
# TOMBOL KEMBALI (contoh fix indentasi)
# ==========================
if st.sidebar.button("⬅ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
    st.session_state.page = "home"
    st.rerun()
