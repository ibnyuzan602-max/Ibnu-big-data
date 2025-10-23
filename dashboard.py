# ===============================
# IMPORT LIBRARY
# ===============================
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

# ===============================
# KONFIGURASI HALAMAN
# ===============================
st.set_page_config(page_title="AI Vision Pro", page_icon="🤖", layout="wide")

# ===============================
# CSS FUTURISTIK
# ===============================
st.markdown("""
    <style>
    /* Background gradien dinamis */
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    body {
        background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #000000);
        background-size: 400% 400%;
        animation: gradientMove 15s ease infinite;
        color: white;
    }

    /* Judul utama */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-family: 'Orbitron', sans-serif;
        color: cyan;
        text-shadow: 0 0 20px cyan;
        margin-bottom: 0.5em;
    }

    /* Subjudul */
    .sub-title {
        text-align: center;
        color: #aaa;
        font-size: 1.2rem;
        margin-bottom: 2em;
    }

    /* Kartu konten */
    .stCard {
        background-color: rgba(0, 0, 0, 0.5);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.2);
        transition: 0.3s;
    }
    .stCard:hover {
        box-shadow: 0 0 35px rgba(0, 255, 255, 0.6);
        transform: scale(1.02);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #001F3F, #001020);
        color: white;
        box-shadow: 2px 0 15px rgba(0,255,255,0.1);
    }

    /* Scrollbar custom */
    ::-webkit-scrollbar {
        width: 10px;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, cyan, blue);
        border-radius: 10px;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        font-size: 0.9rem;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# ===============================
# HEADER
# ===============================
st.markdown("<h1 class='main-title'>🤖 AI Vision Pro</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Sistem Deteksi Cerdas berbasis YOLOv8 dan Deep Learning</p>", unsafe_allow_html=True)

# ===============================
# SIDEBAR NAVIGASI
# ===============================
st.sidebar.title("⚙️ Navigasi")
st.sidebar.write("---")
menu = st.sidebar.radio("Pilih Halaman", ["Dashboard", "Tentang", "Kontak"])

# ===============================
# HALAMAN DASHBOARD
# ===============================
if menu == "Dashboard":
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.subheader("📊 Deteksi dan Analisis Gambar")

    uploaded_file = st.file_uploader("Unggah gambar untuk deteksi", type=["jpg", "png", "jpeg"])

    if uploaded_file:
        image_uploaded = Image.open(uploaded_file)
        st.image(image_uploaded, caption="Gambar yang diunggah", use_container_width=True)
        st.success("✅ Gambar berhasil dimuat!")

        # Placeholder untuk model (contoh)
        st.write("🔍 Proses deteksi dapat dilakukan di sini menggunakan YOLOv8...")
        # model = YOLO("model/best.pt")
        # hasil = model.predict(image_uploaded)
        # st.image(hasil[0].plot(), caption="Hasil Deteksi")
    else:
        st.info("Silakan unggah gambar untuk memulai analisis.")
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# HALAMAN TENTANG
# ===============================
elif menu == "Tentang":
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.subheader("ℹ️ Tentang AI Vision Pro")
    st.write("""
        **AI Vision Pro** adalah platform deteksi visual cerdas yang memanfaatkan
        algoritma YOLOv8 dan Deep Learning untuk mengenali objek dengan cepat dan akurat.

        Dibangun dengan tampilan futuristik dan efek neon yang elegan, website ini
        dirancang agar pengalaman pengguna tetap interaktif dan menyenangkan.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# HALAMAN KONTAK
# ===============================
elif menu == "Kontak":
    st.markdown("<div class='stCard'>", unsafe_allow_html=True)
    st.subheader("📞 Hubungi Kami")
    st.write("""
        - **Email:** support@aivisionpro.com  
        - **Instagram:** [@aivisionpro.ai](https://instagram.com/aivisionpro.ai)  
        - **LinkedIn:** [AI Vision Pro](https://linkedin.com/company/aivisionpro)
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# FOOTER
# ===============================
st.markdown("<div class='footer'>© 2025 AI Vision Pro — Futuristic Dashboard Design</div>", unsafe_allow_html=True)

# ===============================
# PEMUTAR MUSIK MELAYANG 🎵
# ===============================
music_path = os.path.join("music", "lostsagalobby.mp3")

if os.path.exists(music_path):
    with open(music_path, "rb") as f:
        audio_data = f.read()
        audio_b64 = base64.b64encode(audio_data).decode()

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
         box-shadow:0 0 20px rgba(0,255,255,0.7);
         z-index:9999;">
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
