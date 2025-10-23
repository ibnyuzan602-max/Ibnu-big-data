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

# =========================
# KONFIGURASI DASAR
# =========================
st.set_page_config(page_title="AI Vision Pro", page_icon="🤖", layout="wide")

# =========================
# CSS DARK FUTURISTIK
# =========================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 20%, #0b0b17, #1b1b2a 80%);
    color: white;
}
h1, h2, h3 { text-align: center; font-family: 'Poppins', sans-serif; }
.stButton>button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    transition: 0.3s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    transform: scale(1.05);
}
.lottie-center {
    display: flex; justify-content: center; align-items: center;
    margin-top: 30px;
}
.result-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px; text-align: center;
    box-shadow: 0 4px 25px rgba(0,0,0,0.25);
}
.progress-bar {
    width: 100%; height: 22px; border-radius: 10px; overflow: hidden;
    background: #444; margin-top: 10px;
}
.progress-fill {
    height: 100%; color: white; font-weight: bold;
    background: linear-gradient(90deg, #00c6ff, #0072ff);
}
.warning-box {
    background-color: rgba(255,193,7,0.1);
    border-left: 5px solid #ffc107;
    color: #ffc107;
    padding: 10px; border-radius: 8px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNGSI LOTTIE
# =========================
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None

# Animasi
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_TRANSITION = "https://assets10.lottiefiles.com/packages/lf20_t9gkkhz4.json"

lottie_welcome = load_lottie_url(LOTTIE_WELCOME)
lottie_dashboard = load_lottie_url(LOTTIE_DASHBOARD)
lottie_transition = load_lottie_url(LOTTIE_TRANSITION)

# =========================
# MUSIK OTOMATIS + FITUR SEMBUNYIKAN
# =========================
music_path = os.path.join("music", "my_music.mp3")
if os.path.exists(music_path):
    with open(music_path, "rb") as f:
        encoded_audio = base64.b64encode(f.read()).decode()

    if "show_music" not in st.session_state:
        st.session_state.show_music = True

    col1, col2 = st.columns([8, 2])
    with col2:
        toggle = st.checkbox("🎧 Tampilkan Musik", value=st.session_state.show_music)
        st.session_state.show_music = toggle

    if st.session_state.show_music:
        st.markdown(f"""
        <audio controls autoplay loop>
            <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <audio autoplay loop style="display:none;">
            <source src="data:audio/mp3;base64,{encoded_audio}" type="audio/mp3">
        </audio>
        """, unsafe_allow_html=True)

# =========================
# HALAMAN BERDASARKAN STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# =========================
# HALAMAN 1 - WELCOME
# =========================
if st.session_state.page == "welcome":
    st.markdown("<h1>🌌 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Eksplorasi teknologi deteksi & klasifikasi gambar cerdas</h3>", unsafe_allow_html=True)

    if lottie_welcome:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_welcome, height=300, key="welcome_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Masuk ke Website"):
            with st.spinner("Memuat sistem AI..."):
                st_lottie(lottie_transition, height=200, key="transition_lottie")
                time.sleep(2)
            st.session_state.page = "dashboard"
            st.experimental_rerun()

# =========================
# HALAMAN 2 - DASHBOARD
# =========================
elif st.session_state.page == "dashboard":

    # Load Model
    @st.cache_resource
    def load_models():
        yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
        classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
        return yolo_model, classifier

    yolo_model, classifier = load_models()

    # Sidebar
    st.sidebar.header("⚙️ Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])

    # Header + Animasi
    st.markdown("<h1>🤖 AI Vision Pro Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")
    if lottie_dashboard:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_dashboard, height=250, key="dashboard_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    # Upload Gambar
    st.markdown("### 📤 Unggah Gambar untuk Analisis")
    uploaded_file = st.file_uploader("Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Gambar yang Diupload", use_container_width=True)
        st.markdown("<p style='text-align:center;'>🤖 AI sedang menganalisis gambar...</p>", unsafe_allow_html=True)
        st_lottie(lottie_transition, height=120, key="loading_anim")
        time.sleep(1.5)

        if mode == "Deteksi Objek (YOLO)":
            st.info("🚀 Menjalankan deteksi objek...")
            img_cv2 = np.array(img)
            results = yolo_model.predict(source=img_cv2)
            result_img = results[0].plot()
            st.image(result_img, caption="🎯 Hasil Deteksi", use_container_width=True)

        elif mode == "Klasifikasi Gambar":
            st.info("🧠 Menjalankan klasifikasi gambar...")
            img_resized = img.resize((128, 128))
            img_array = image.img_to_array(img_resized)
            img_array = np.expand_dims(img_array, axis=0) / 255.0
            prediction = classifier.predict(img_array)
            class_index = np.argmax(prediction)
            confidence = np.max(prediction)
            st.markdown(f"""
            <div class="result-card">
                <h3>🧾 Hasil Prediksi</h3>
                <p><b>Kelas:</b> {class_index}</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width:{confidence*100}%;">{confidence:.1%}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.info("🔍 Mode Insight Aktif — AI menganalisis konten gambar.")
            st.markdown("""
            <div class="result-card">
                <h3>💬 Insight Otomatis</h3>
                <p>AI mendeteksi karakteristik visual dominan seperti bentuk, warna, dan pola.</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu untuk memulai analisis.</div>", unsafe_allow_html=True)
