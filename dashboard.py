import streamlit as st
from streamlit_lottie import st_lottie
from ultralytics import YOLO
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import requests
import io
import os
import time

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
h1, h2, h3 { text-align:center; font-family:'Poppins', sans-serif; color:white; }
.center { display:flex; justify-content:center; align-items:center; }
.music-btn {
    position:fixed;
    bottom:20px;
    right:20px;
    background:#0072ff;
    color:white;
    border:none;
    padding:10px 15px;
    border-radius:30px;
    cursor:pointer;
    font-weight:bold;
    z-index:99999;
}
.music-btn:hover { background:#005fd4; }
.lottie-center {
    display:flex;
    justify-content:center;
    align-items:center;
    margin-top:20px;
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

# =========================
# ANIMASI
# =========================
LOTTIE_LANDING = "https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json"
LOTTIE_AI = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
lottie_landing = load_lottie_url(LOTTIE_LANDING)
lottie_ai = load_lottie_url(LOTTIE_AI)

# =========================
# AUDIO PLAYER OTOMATIS
# =========================
playlist_js = [
    "musik/wildwest.mp3",
    "musik/lostsagalobby.mp3"
]
playlist_js = str(playlist_js).replace("'", '"')  # untuk JS array

audio_html = f"""
<div style="position:fixed; bottom:20px; right:20px; z-index:9999;">
    <button class="music-btn" onclick="toggleMusic()">🎵 Matikan/Jalankan Musik</button>
    <audio id="bgAudio">
        Your browser does not support the audio element.
    </audio>
</div>
<script>
const playlist = {playlist_js};
let index = 0;
const audio = document.getElementById("bgAudio");
audio.volume = 0.35;

function playTrack(i) {{
    audio.src = playlist[i];
    audio.play().catch(e => console.warn("Autoplay mungkin diblokir:", e));
}}
function toggleMusic() {{
    if (audio.paused) {{
        audio.play();
    }} else {{
        audio.pause();
    }}
}}
audio.addEventListener("ended", () => {{
    index = (index + 1) % playlist.length;
    playTrack(index);
}});
window.addEventListener('click', function() {{
    if (audio.paused) {{
        playTrack(index);
    }}
}}, {{once:true}});
</script>
"""
st.components.v1.html(audio_html, height=0, scrolling=False)

# =========================
# HALAMAN NAVIGASI
# =========================
if "page" not in st.session_state:
    st.session_state.page = "landing"

def go_to_dashboard():
    st.session_state.page = "dashboard"
    st.experimental_rerun()

# =========================
# HALAMAN 1: LANDING PAGE
# =========================
if st.session_state.page == "landing":
    st.title("🤖 Selamat Datang di AI Vision Pro")
    st.markdown("### Sistem Deteksi & Klasifikasi Gambar Cerdas")
    if lottie_landing:
        st_lottie(lottie_landing, height=300, key="landing_anim")
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    if st.button("🚀 Masuk ke Website", use_container_width=True):
        with st.spinner("Memuat sistem AI..."):
            time.sleep(2)
        go_to_dashboard()
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# HALAMAN 2: DASHBOARD AI
# =========================
elif st.session_state.page == "dashboard":
    # Sidebar mode pilihan
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar"])
    
    # Header
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Analisis Gambar Canggih dengan AI")

    # Animasi tengah
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=280, key="ai_center")
        st.markdown("</div>", unsafe_allow_html=True)

    # Upload gambar
    st.markdown("### 📤 Unggah Gambar untuk Analisis")
    uploaded_file = st.file_uploader("Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Gambar yang Diupload", use_container_width=True)
        time.sleep(1)
        st.info("🤖 AI sedang menganalisis gambar...")

        if mode == "Deteksi Objek (YOLO)":
            yolo = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
            img_cv2 = np.array(img)
            results = yolo.predict(source=img_cv2)
            result_img = results[0].plot()
            st.image(result_img, caption="🎯 Hasil Deteksi", use_container_width=True)

        elif mode == "Klasifikasi Gambar":
            classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
            img_resized = img.resize((128, 128))
            img_array = image.img_to_array(img_resized)
            img_array = np.expand_dims(img_array, axis=0) / 255.0
            pred = classifier.predict(img_array)
            idx = np.argmax(pred)
            conf = np.max(pred)
            st.success(f"🧾 Kelas: {idx} — Keyakinan: {conf:.2%}")
