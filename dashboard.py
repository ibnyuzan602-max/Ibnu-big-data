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
import random
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
# CSS DARK FUTURISTIK & TOMBOL BAWAH FIXED
# =========================
st.markdown("""
<style>
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

[data-testid="stSidebar"] button[kind="secondaryFormSubmit"] {
    position: fixed;
    bottom: 20px;
    width: 200px;
    left: 10px;
    z-index: 999;
}

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
# FUNGSI LOAD LOTTIE
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
# ANIMASI LOTTIE
# =========================
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

# =========================
# SISTEM HALAMAN
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# =========================
# SISTEM MUSIK (RANDOM START VERSION)
# =========================
MUSIC_FOLDER = "musik"
os.makedirs(MUSIC_FOLDER, exist_ok=True)

TRACKS = [
    os.path.join(MUSIC_FOLDER, "wildwest.mp3"),
    os.path.join(MUSIC_FOLDER, "lostsagalobby.mp3"),
]

existing_tracks = [p for p in TRACKS if os.path.exists(p)]

if len(existing_tracks) > 0:
    st.sidebar.markdown("---")
    st.sidebar.header("🎵 Musik Latar")

    # Simpan status musik
    if "show_audio_controls" not in st.session_state:
        st.session_state.show_audio_controls = True
    if "music_playing" not in st.session_state:
        st.session_state.music_playing = True
    if "audio_volume" not in st.session_state:
        st.session_state.audio_volume = 0.6
    if "random_start" not in st.session_state:
        st.session_state.random_start = random.randint(0, len(existing_tracks) - 1)

    show_ctrl = st.sidebar.checkbox("Tampilkan Kontrol Musik", value=st.session_state.show_audio_controls)
    st.session_state.show_audio_controls = show_ctrl

    # Tombol Play / Pause
    if st.sidebar.button("⏯️ Play / Pause Musik", key="music_pause_btn"):
        st.session_state.music_playing = not st.session_state.music_playing

    # Volume
    vol = st.sidebar.slider("Volume", 0.0, 1.0, st.session_state.audio_volume, 0.05)
    st.session_state.audio_volume = vol

    # Playlist dan pengaturan awal
    playlist_js = json.dumps(existing_tracks)
    controls_attr = "controls" if st.session_state.show_audio_controls else ""
    style_attr = "" if st.session_state.show_audio_controls else 'style="display:none;"'
    play_state = "true" if st.session_state.music_playing else "false"
    start_index = st.session_state.random_start

    audio_html = f"""
    <div style="position:fixed; bottom:20px; right:20px; z-index:9999;">
        <audio id="bgAudio" {controls_attr} {style_attr}>
            Your browser does not support the audio element.
        </audio>
    </div>
    <script>
    const playlist = {playlist_js};
    let index = {start_index};
    const audio = document.getElementById("bgAudio");
    audio.volume = {vol};

    function playTrack(i) {{
        audio.src = playlist[i];
        audio.play().catch(e => console.warn("Autoplay mungkin diblokir:", e));
    }}

    // Main lagu acak pertama
    playTrack(index);

    // Kalau musik selesai, lanjut ke lagu berikutnya
    audio.addEventListener("ended", () => {{
        index = (index + 1) % playlist.length;
        playTrack(index);
    }});

    if ({play_state} === false) {{
        audio.pause();
    }}
    </script>
    """
    st.components.v1.html(audio_html, height=0, scrolling=False)

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
# HALAMAN 2: DASHBOARD AI
# =========================
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=250, key="ai_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    # Mode AI
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")

    # Load model
    @st.cache_resource
    def load_models():
        try:
            yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
            classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
            return yolo_model, classifier
        except Exception as e:
            st.warning(f"⚠️ Gagal memuat model. Pastikan file model ada di folder 'model/'. Error: {e}")
            return None, None

    yolo_model, classifier = load_models()

    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file and yolo_model and classifier:
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
            st.download_button(
                label="📥 Download Hasil Deteksi",
                data=img_bytes,
                file_name="hasil_deteksi_yolo.png",
                mime="image/png"
            )

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
                <p><b>Kelas:</b> Index Kelas {class_index}</p>
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

    # Tombol kembali ke halaman awal (posisi fixed di sidebar)
    if st.sidebar.button("⬅️ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
