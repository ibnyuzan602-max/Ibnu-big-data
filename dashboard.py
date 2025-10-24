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
import base64
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
# NAMA KELAS & FUNGSI UTAMA
# =========================
CLASS_NAMES = ["kucing", "anjing", "manusia"] 
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

def reset_to_home_state():
    st.session_state.page = "home"

# =========================
# CSS: SOLUSI SCROLL + SELECTBOX
# =========================
st.markdown("""
<style>
/* 1. Kontainer Utama (Latar Belakang & Aurora) */
[data-testid="stAppViewContainer"] {
    background-color: #050510; 
    color: #E0E7FF;
    position: relative;
    overflow: hidden;
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background: 
        radial-gradient(circle at 20% 80%, rgba(66, 133, 244, 0.1) 0%, transparent 40%),
        radial-gradient(circle at 80% 20%, rgba(255, 102, 196, 0.08) 0%, transparent 45%), 
        radial-gradient(circle at 50% 50%, rgba(0, 255, 150, 0.05) 0%, transparent 50%);
    
    background-size: 200% 200%;
    z-index: 1;
    pointer-events: none;
    animation: auroraMovement 25s ease-in-out infinite alternate;
}
@keyframes auroraMovement {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
}
main, header, footer { position: relative; z-index: 10; }

/* 2. Sidebar Style */
[data-testid="stSidebar"] {
    background: rgba(15, 15, 25, 0.95);
    backdrop-filter: blur(10px);
    border-right: 1px solid #333;
    z-index: 15;
    /* PENTING: Beri tinggi penuh layar dan sembunyikan scroll di kontainer luar */
    height: 100vh !important;
    overflow: hidden !important; 
}
[data-testid="stSidebar"] * { color: white !important; }


/* === SOLUSI SCROLL SIDEBAR UTAMA === */
/* KUNCI: Targetkan konten sidebar untuk scroll */
[data-testid="stSidebarContent"] {
    /* Memaksa scroll bar vertikal muncul jika konten melebihi area */
    overflow-y: auto !important; 
    /* Pastikan elemen konten mengisi penuh area yang tersedia (di dalam kontainer 100vh) */
    height: 100%; 
    padding-bottom: 50px; 
}
/* =================================== */


/* === SOLUSI VISIBILITAS NAMA LAGU (SELECTBOX) === */
/* Teks yang terlihat di dalam selectbox saat terpilih */
[data-testid="stSelectbox"] div[data-testid="stBody"] {
    background-color: #333 !important; 
    color: white !important; 
}
/* Teks di dalam input (pastikan nama lagu terlihat) */
[data-testid="stSelectbox"] input {
    color: white !important;
}
/* Teks di dropdown list saat dibuka */
div.st-bb {
    color: #000 !important; /* Agar kontras dengan latar belakang putih default dropdown list */
}
/* ==================================================== */


/* 4. Elemen Umum */
h1, h2, h3 { text-align: center; font-family: 'Poppins', sans-serif; }
.lottie-center { display: flex; justify-content: center; align-items: center; margin-top: 30px; }
.result-card { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-top: 20px; text-align: center; box-shadow: 0 4px 25px rgba(0,0,0,0.25); }
.warning-box { background-color: rgba(255, 193, 7, 0.1); border-left: 5px solid #ffc107; color: #ffc107; padding: 10px; border-radius: 8px; text-align: center; width: 90%; margin: 15px auto; }
.music-button { position: fixed; bottom: 20px; right: 25px; background-color: #1db954; color: white; border-radius: 50%; width: 55px; height: 55px; display: flex; align-items: center; justify-content: center; font-size: 26px; cursor: pointer; z-index: 9999; box-shadow: 0 4px 15px rgba(0,0,0,0.3); transition: transform 0.2s ease; }
.music-button:hover { transform: scale(1.1); }
</style>
""", unsafe_allow_html=True)

# =========================
# SISTEM MUSIK (Fitur Inti)
# =========================
music_folder = "music"
if os.path.exists(music_folder):
    music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

    if len(music_files) == 0:
        st.sidebar.warning("⚠ Tidak ada file musik di folder 'music/'.")
    else:
        st.sidebar.markdown("#### 🎧 Player Musik")
        
        # Inisialisasi/Validasi current_music
        if "current_music" not in st.session_state or st.session_state.current_music not in music_files:
            st.session_state.current_music = music_files[0]

        selected_music = st.sidebar.selectbox(
            "Pilih Lagu:",
            options=music_files,
            index=music_files.index(st.session_state.current_music)
        )

        if selected_music != st.session_state.current_music:
            st.session_state.current_music = selected_music
            st.rerun()

        music_path = os.path.join(music_folder, st.session_state.current_music)
        try:
            with open(music_path, "rb") as f:
                audio_data = f.read()
                audio_b64 = base64.b64encode(audio_data).decode()

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
# HALAMAN 1: WELCOME
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
                anim = load_lottie_url(LOTTIE_TRANSITION)
                if anim:
                    st_lottie(anim, height=200, key="transition_anim")
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

    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br>", unsafe_allow_html=True) 

    @st.cache_resource
    def load_models():
        yolo_model, classifier = None, None
        
        yolo_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt")
        if os.path.exists(yolo_path):
            try: yolo_model = YOLO(yolo_path)
            except Exception as e: st.warning(f"⚠ Gagal memuat YOLO: {e}")
        else: st.warning("⚠ Model YOLO tidak ditemukan di path: model/Ibnu Hawari Yuzan_Laporan 4.pt")

        cls_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5")
        if os.path.exists(cls_path):
            try: classifier = tf.keras.models.load_model(cls_path)
            except Exception as e: st.warning(f"⚠ Gagal memuat Classifier: {e}")
        else: st.warning("⚠ Model Classifier tidak ditemukan di path: model/Ibnu Hawari Yuzan_Laporan 2.h5")
            
        return yolo_model, classifier

    yolo_model, classifier = load_models()

    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    # Tombol Kembali (Diposisikan di akhir sidebar)
    st.sidebar.markdown("---")
    if st.sidebar.button("⬅ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
        reset_to_home_state()
        st.rerun()
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if uploaded_file:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="🖼 Gambar yang Diupload", use_column_width=True)
        except Exception as e:
            st.error(f"Gagal membuka gambar: {e}")
            img = None

        if img is not None:
            if yolo_model is None and classifier is None:
                st.markdown("<div class='warning-box'>❌ Semua model AI gagal dimuat.</div>", unsafe_allow_html=True)
            else:
                with st.spinner("🤖 AI sedang menganalisis gambar..."):
                    time.sleep(1.5)

                if mode == "Deteksi Objek (YOLO)":
                    if yolo_model:
                        st.info("🚀 Menjalankan deteksi objek...")
                        img_cv2 = np.array(img)
                        results = yolo_model.predict(source=img_cv2)
                        result_img = results[0].plot()
                        st.image(result_img, caption="🎯 Hasil Deteksi", use_column_width=True)
                        img_bytes = io.BytesIO()
                        Image.fromarray(result_img).save(img_bytes, format="PNG")
                        img_bytes.seek(0)
                        st.download_button("📥 Download Hasil Deteksi", data=img_bytes, file_name="hasil_deteksi_yolo.png", mime="image/png")
                    else:
                        st.warning("Model YOLO tidak tersedia.")

                elif mode == "Klasifikasi Gambar":
                    if classifier:
                        st.info("🧠 Menjalankan klasifikasi gambar...")
                        img_resized = img.resize((128, 128))
                        img_array = image.img_to_array(img_resized)
                        img_array = np.expand_dims(img_array, axis=0) / 255.0
                        prediction = classifier.predict(img_array)
                        class_index = np.argmax(prediction)
                        confidence = np.max(prediction)
                        
                        predicted_class_name = CLASS_NAMES[class_index] if class_index < len(CLASS_NAMES) else f"Kelas tidak dikenal ({class_index})"
                        
                        st.markdown(f"""
                        <div class="result-card">
                            <h3>🧾 Hasil Prediksi</h3>
                            <p><b>Kelas:</b> **{predicted_class_name.upper()}**</p>
                            <p><b>Akurasi:</b> {confidence:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Model Classifier tidak tersedia.")

                elif mode == "AI Insight":
                    st.info("🔍 Mode Insight Aktif")
                    st.markdown("""
                    <div class="result-card">
                        <h3>💬 Insight Otomatis</h3>
                        <p>Fitur ini masih dalam tahap pengembangan.</p>
                    </div>
                    """, unsafe_allow_html=True)

    elif uploaded_file is None:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)
