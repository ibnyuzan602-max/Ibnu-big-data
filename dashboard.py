import streamlit as st
from ultralytics import YOLO
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import requests
import io
import time
import os
from streamlit_lottie import st_lottie

# =========================
# KONFIGURASI DASAR
# =========================
st.set_page_config(
    page_title="AI Vision Pro",
    page_icon="🤖",
    layout="wide"
)

# =========================
# CSS DARK FUTURISTIK
# =========================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 20%, #0b0b17, #1b1b2a 80%);
    color: white;
}
h1, h2, h3, h4 {
    text-align: center;
    font-family: 'Poppins', sans-serif;
}
.lottie-center {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
}
.result-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
    text-align: center;
    box-shadow: 0 4px 25px rgba(0,0,0,0.25);
}
.warning-box {
    background-color: rgba(255, 193, 7, 0.1);
    border-left: 5px solid #ffc107;
    color: #ffc107;
    padding: 10px;
    border-radius: 8px;
    margin-top: 15px;
    text-align: center;
    width: 90%;
    margin-left: auto;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNGSI LOAD LOTTIE
# =========================
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# Animasi
LOTTIE_INTRO = "https://assets10.lottiefiles.com/packages/lf20_touohxv0.json"
LOTTIE_TRANSITION = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_AI = "https://assets10.lottiefiles.com/packages/lf20_zrqthn6o.json"
LOTTIE_LOADING = "https://assets10.lottiefiles.com/packages/lf20_t9gkkhz4.json"

# =========================
# FUNGSI MUAT MODEL
# =========================
@st.cache_resource
def load_models():
    yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
    classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
    return yolo_model, classifier

yolo_model, classifier = load_models()

# =========================
# SISTEM HALAMAN
# =========================
if "page" not in st.session_state:
    st.session_state.page = "landing"

# =========================
# MUSIK LATAR
# =========================
music_path = os.path.join("music", "wildwest.mp3")

if os.path.exists(music_path):
    if "show_music" not in st.session_state:
        st.session_state.show_music = True

    toggle = st.checkbox("🎧 Tampilkan / Sembunyikan Musik", value=st.session_state.show_music)
    st.session_state.show_music = toggle

    if st.session_state.show_music:
        st.audio(music_path, format="audio/mp3", start_time=0)
else:
    st.warning("⚠️ File musik tidak ditemukan di folder 'music/'. Pastikan file `my_music.mp3` ada di folder `/music`.")

# =========================
# HALAMAN 1: LANDING PAGE
# =========================
if st.session_state.page == "landing":
    st.markdown("<h1>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("### Sistem Cerdas untuk Deteksi dan Klasifikasi Gambar")

    lottie_intro = load_lottie_url(LOTTIE_INTRO)
    if lottie_intro:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_intro, height=300, key="intro")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## 🚀 Siap untuk mulai?")
    if st.button("Masuk ke Website"):
        st.session_state.page = "dashboard"
        st.session_state.transition = True
        st.rerun()

# =========================
# HALAMAN 2: DASHBOARD
# =========================
elif st.session_state.page == "dashboard":

    # Efek transisi animasi saat masuk ke halaman 2
    if "transition" in st.session_state and st.session_state.transition:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(load_lottie_url(LOTTIE_TRANSITION), height=250, key="transition_anim")
        st.markdown("</div>", unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.transition = False
        st.rerun()

    st.title("🧠 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    # Animasi utama halaman 2
    st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
    st_lottie(load_lottie_url(LOTTIE_AI), height=250, key="main_ai")
    st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar mode pilihan
    st.sidebar.header("🧭 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar dan biarkan AI menganalisis.")

    # Upload gambar
    st.markdown("### 📤 Unggah Gambar untuk Analisis")
    uploaded_file = st.file_uploader("Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Gambar yang Diupload", use_container_width=True)

        # Animasi loading
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(load_lottie_url(LOTTIE_LOADING), height=180, key="loading")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>🤖 AI sedang menganalisis gambar...</p>", unsafe_allow_html=True)
        time.sleep(2)

        # Mode YOLO
        if mode == "Deteksi Objek (YOLO)":
            results = yolo_model.predict(np.array(img))
            result_img = results[0].plot()

            st.image(result_img, caption="🎯 Hasil Deteksi Objek", use_container_width=True)

            img_bytes = io.BytesIO()
            Image.fromarray(result_img).save(img_bytes, format="PNG")
            img_bytes.seek(0)

            st.download_button(
                label="📥 Download Hasil Deteksi",
                data=img_bytes,
                file_name="hasil_deteksi.png",
                mime="image/png"
            )

        # Mode Klasifikasi
        elif mode == "Klasifikasi Gambar":
            img_resized = img.resize((128, 128))
            img_array = np.expand_dims(image.img_to_array(img_resized), axis=0) / 255.0

            prediction = classifier.predict(img_array)
            class_index = np.argmax(prediction)
            confidence = np.max(prediction)

            st.markdown(f"""
            <div class='result-card'>
                <h3>🧾 Hasil Klasifikasi</h3>
                <p><b>Kelas:</b> {class_index}</p>
                <p><b>Kepercayaan:</b> {confidence:.2%}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu untuk memulai analisis.</div>", unsafe_allow_html=True)
