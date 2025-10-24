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
import base64

# =========================
# INISIALISASI SESSION STATE PALING AMAN (HANYA CURRENT MUSIC)
# =========================
# Kita hanya inisialisasi current_music di sini karena 'page' akan dibaca dengan .get()
if "current_music" not in st.session_state:
    st.session_state.current_music = None

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
# CSS DARK FUTURISTIK + TOMBOL MUSIK MELAYANG
# =========================
st.markdown("""
<style>
/* ... (kode CSS Anda sebelumnya) ... */

/* === SOLUSI VISIBILITAS NAMA LAGU (EXTREME) === */
.st-bk input {
    color: white !important; 
    background-color: #1a1a2e !important;
}
div[role="listbox"] div[data-testid="stVirtualList"] div[role="option"] {
    color: black !important; 
    background-color: white !important; 
}
/* ... (lanjutan kode CSS) ... */
</style>
""", unsafe_allow_html=True)

# =========================
# FUNGSI LOAD LOTTIE & NAVIGASI
# =========================
# ... (Fungsi load_lottie_url) ...
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

# Fungsi Navigasi (tetap menggunakan sintaks atribut untuk MENULIS state)
def reset_to_home_state():
    st.session_state.page = "home"

# =========================
# SISTEM MUSIK
# =========================
music_folder = "music"
if os.path.exists(music_folder):
    music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

    if len(music_files) == 0:
        st.sidebar.warning("⚠ Tidak ada file musik di folder 'music/'.")
    else:
        st.sidebar.markdown("#### 🎧 Player Musik")

        # Inisialisasi/Validasi current_music
        if st.session_state.current_music is None or st.session_state.current_music not in music_files:
            st.session_state.current_music = music_files[0]

        # Dropdown untuk pilih lagu
        selected_music = st.sidebar.selectbox(
            "Pilih Lagu:",
            options=music_files,
            index=music_files.index(st.session_state.current_music)
        )

        # Update jika lagu diganti
        if selected_music != st.session_state.current_music:
            st.session_state.current_music = selected_music
            st.rerun()

        # Path file musik aktif
        music_path = os.path.join(music_folder, st.session_state.current_music)

        # Encode file musik ke base64 untuk diputar di HTML
        try:
            with open(music_path, "rb") as f:
                audio_data = f.read()
                audio_b64 = base64.b64encode(audio_data).decode()

            # Player musik (manual control)
            audio_html = f"""
            <audio controls loop style="width:100%">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                Browser Anda tidak mendukung audio.
            </audio>
            """
            st.sidebar.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.sidebar.error(f"Gagal memuat file musik: {e}")

else:
    st.sidebar.warning("⚠ Folder 'music/' tidak ditemukan.")

# =========================
# LOGIKA PENGENDALI HALAMAN UTAMA
# =========================

# KUNCI PERBAIKAN: Gunakan .get() untuk membaca state!
# Ini akan mengembalikan "home" jika 'page' belum ada, menghilangkan error di baris 176.
current_page = st.session_state.get("page", "home")

# HALAMAN 1: WELCOME (Menggantikan if st.session_state.page == "home":)
if current_page == "home":
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
            st.session_state.page = "dashboard" # Menulis state tetap menggunakan .page
            with st.spinner("🔄 Memuat halaman..."):
                anim = load_lottie_url(LOTTIE_TRANSITION)
                if anim:
                    st_lottie(anim, height=200, key="transition_anim")
                time.sleep(1.5)
            st.rerun()

# =========================
# HALAMAN 2: DASHBOARD (Menggantikan elif st.session_state.page == "dashboard":)
# =========================
elif current_page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=250, key="ai_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    @st.cache_resource
    def load_models():
        yolo_model, classifier = None, None
        
        yolo_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt")
        cls_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5")
        
        if os.path.exists(yolo_path):
            try: yolo_model = YOLO(yolo_path)
            except Exception as e: st.warning(f"⚠ Gagal memuat YOLO: {e}")
        else: st.warning("⚠ Model YOLO tidak ditemukan.")

        if os.path.exists(cls_path):
            try: classifier = tf.keras.models.load_model(cls_path)
            except Exception as e: st.warning(f"⚠ Gagal memuat Classifier: {e}")
        else: st.warning("⚠ Model Classifier tidak ditemukan.")
            
        return yolo_model, classifier

    yolo_model, classifier = load_models()

    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file and yolo_model and classifier:
        try:
            img = Image.open(uploaded_file)
            st.image(img, caption="🖼 Gambar yang Diupload", use_column_width=True)
            with st.spinner("🤖 AI sedang menganalisis gambar..."):
                time.sleep(1.5)

            # ... (Logika deteksi & klasifikasi) ...
            if mode == "Deteksi Objek (YOLO)":
                st.info("🚀 Menjalankan deteksi objek...")
                img_cv2 = np.array(img)
                results = yolo_model.predict(source=img_cv2)
                result_img = results[0].plot()
                st.image(result_img, caption="🎯 Hasil Deteksi", use_column_width=True)
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

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses gambar: {e}")

    elif uploaded_file and (yolo_model is None or classifier is None):
        st.markdown("<div class='warning-box'>⚠ Model AI gagal dimuat. Harap periksa path model.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)

    # 🔹 TOMBOL KEMBALI
    if st.sidebar.button("⬅ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
        reset_to_home_state()
        st.rerun()
