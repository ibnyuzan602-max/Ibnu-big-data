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
import json
from streamlit_lottie import st_lottie

# =========================
# KONFIGURASI DASAR
# =========================
st.set_page_config(
    page_title="AI Vision Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# FUNGSI CALLBACK (UNTUK TOMBOL YANG MENGUBAH HALAMAN)
# =========================
def go_home():
    """Mengubah session state untuk kembali ke halaman home."""
    st.session_state.page = "home"

# =========================
# CSS DARK FUTURISTIK & TOMBOL BAWAH (FIXED POSITION)
# =========================
st.markdown("""
<style>
/* ... (Bagian CSS Anda tetap sama) ... */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 20%, #0b0b17, #1b1b2a 80%);
    color: white;
}
[data-testid="stSidebar"] {
    background: rgba(15, 15, 25, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid #333;
    padding-bottom: 80px; 
}
[data-testid="stSidebar"] * { color: white !important; }

/* FIX: Perbaikan CSS untuk tombol kembali (memastikan posisi fixed) */
[data-testid="stSidebar"] div.stButton:has(button[kind="secondaryFormSubmit"]) {
    position: fixed;
    bottom: 20px;
    width: 200px; 
    left: 10px; 
    z-index: 999;
}
/* Hapus semua CSS terkait .music-button dan .rotating jika Anda menggunakan st.audio */

h1, h2, h3 {
    text-align: center;
    font-family: 'Poppins', sans-serif;
}
.lottie-center {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 30px;
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
    text-align: center;
    width: 90%;
    margin: 15px auto;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNGSI LOAD LOTTIE (Tidak Berubah)
# =========================
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# =========================
# ANIMASI LOTTIE (Tidak Berubah)
# =========================
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

# =========================
# SISTEM HALAMAN (Tidak Berubah)
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"


# =======================================================
# SISTEM MUSIK (MENGGUNAKAN DUA PLAYER st.audio) - FIX TYPERROR
# =======================================================
MUSIC_FOLDER = "music"
music_path_1 = os.path.join(MUSIC_FOLDER, "wildwest.mp3")
music_path_2 = os.path.join(MUSIC_FOLDER, "lostsagalobby.mp3")

def display_music_players():
    """
    Mengisolasi logika dan pemanggilan widget st.audio di sidebar.
    Ini membantu mencegah TypeErrors selama reruns.
    """
    exists_1 = os.path.exists(music_path_1)
    exists_2 = os.path.exists(music_path_2)

    # Hanya jalankan jika setidaknya satu file ada
    if not (exists_1 or exists_2):
        st.sidebar.warning("⚠️ Kedua file musik tidak ditemukan di folder `/music`.")
        return

    # Semua widget Streamlit harus ada di sini (di dalam fungsi)
    with st.sidebar:
        if "show_music" not in st.session_state:
            st.session_state.show_music = True

        st.markdown("---") # Tambahkan pemisah di atas widget musik
        toggle = st.checkbox("🎧 Tampilkan / Sembunyikan Music Players", value=st.session_state.show_music)
        st.session_state.show_music = toggle
        
        if st.session_state.show_music:
            st.header("🎶 Music Player")

            if exists_1:
                st.caption("Track 1: Wild West")
                # Pemanggilan yang menyebabkan error (Line 145) sekarang terisolasi
                st.audio(music_path_1, format="audio/mp3", start_time=0, key="audio_player_1")
            else:
                st.warning(f"⚠️ Track 1 (`wildwest.mp3`) tidak ditemukan.")
            
            st.markdown("---")

            if exists_2:
                st.caption("Track 2: Lost Saga Lobby")
                st.audio(music_path_2, format="audio/mp3", start_time=0, key="audio_player_2")
            else:
                st.warning(f"⚠️ Track 2 (`lostsagalobby.mp3`) tidak ditemukan.")
        st.markdown("---") # Garis pemisah di bawah widget musik

# Panggil fungsi di level tertinggi skrip
display_music_players()
# =======================================================

# =========================
# HALAMAN 1: WELCOME PAGE
# =========================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sistem Cerdas untuk Deteksi Objek dan Klasifikasi Gambar</p>", unsafe_allow_html=True)
    
    lottie = load_lottie_url(LOTTIE_WELCOME)
    if lottie:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie, height=300, key="welcome_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Masuk ke Website", use_container_width=True):
            st.session_state.page = "dashboard"
            with st.spinner("🔄 Memuat halaman..."):
                trans_anim = load_lottie_url(LOTTIE_TRANSITION)
                if trans_anim:
                    st_lottie(trans_anim, height=200, key="transition_anim")
                time.sleep(1.5)
            st.rerun()

# =========================
# HALAMAN 2: DASHBOARD
# =========================
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=250, key="ai_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    # =========================
    # MODE ANALISIS
    # =========================
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    
    # Placeholder untuk memisahkan tombol 'Mode AI' dan tombol 'Kembali'
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # =========================
    # LOGIKA MODEL & UPLOAD
    # =========================
    @st.cache_resource
    def load_models():
        try:
            yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
            classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
            return yolo_model, classifier
        except Exception as e:
            st.warning(f"⚠️ Gagal memuat model: {e}")
            return None, None

    yolo_model, classifier = load_models()

    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file and yolo_model and classifier:
        # ... (Logika Analisis Gambar)
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Gambar yang Diupload", use_container_width=True)
        with st.spinner("🤖 AI sedang menganalisis gambar..."):
            time.sleep(1.5)

        if mode == "Deteksi Objek (YOLO)":
            st.info("🚀 Menjalankan deteksi objek...")
            img_cv2 = np.array(img)
            results = yolo_model.predict(source=img_cv2)
            result_img = results[0].plot()
            st.image(result_img, caption="🎯 Hasil Deteksi", use_container_width=True)
            img_bytes = io.BytesIO()
            Image.fromarray(result_img).save(img_bytes, format="PNG")
            img_bytes.seek(0)
            st.download_button("📥 Download Hasil Deteksi", data=img_bytes, file_name="hasil_deteksi_yolo.png", mime="image/png")

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
                <p><b>Akurasi:</b> {confidence:.2%}</p>
            </div>
            """, unsafe_allow_html=True)

        elif mode == "AI Insight":
            st.info("🔍 Mode Insight Aktif")
            st.markdown("""
            <div class="result-card">
                <h3>💬 Insight Otomatis</h3>
                <p>AI menganalisis pola visual, bentuk, dan warna utama.</p>
                <p>Fitur ini masih dalam tahap pengembangan.</p>
            </div>
            """, unsafe_allow_html=True)
            
    elif uploaded_file and (yolo_model is None or classifier is None):
        st.markdown("<div class='warning-box'>⚠️ Model AI gagal dimuat. Harap periksa path model.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)
        
    # =========================
    # TOMBOL KEMBALI DI PALING BAWAH SIDEBAR (FIXED) - FIX TYPERROR
    # =========================
    st.sidebar.button("⬅️ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True, on_click=go_home)
