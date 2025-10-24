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
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="AI Vision Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# FUNGSI LOTTIE ANIMASI
# =========================
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"

# =========================
# PAGE STATE
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

def reset_to_home_state():
    st.session_state.page = "home"

# =========================
# BACKGROUND AURORA + PARTIKEL
# =========================
st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #071020 0%, #081427 30%, #0b0b17 60%, #05040a 100%);
    background-size: 300% 300%;
    animation: auroraMove 18s ease infinite;
    color: #e6f7ff;
    position: relative;
    overflow: hidden;
}
@keyframes auroraMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 20% 20%, rgba(0,200,255,0.06) 0%, transparent 25%),
      radial-gradient(circle at 80% 30%, rgba(123,61,255,0.045) 0%, transparent 30%),
      radial-gradient(circle at 60% 75%, rgba(0,255,150,0.035) 0%, transparent 40%);
    z-index: 0;
    pointer-events: none;
    transform-origin: center;
    animation: subtleShift 24s ease-in-out infinite;
}
@keyframes subtleShift {
    0% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-12px) scale(1.03); }
    100% { transform: translateY(0px) scale(1); }
}
[data-testid="stAppViewContainer"]::after {
    content:"";
    position:absolute;
    inset:0;
    background-image:
      radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
      radial-gradient(rgba(255,255,255,0.02) 1px, transparent 1px);
    background-size: 80px 80px, 120px 120px;
    opacity: 0.6;
    mix-blend-mode: overlay;
    z-index: 0;
    animation: rotateTexture 60s linear infinite;
}
@keyframes rotateTexture {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
main, header, footer, section, div {
    position: relative;
    z-index: 5;
}
[data-testid="stSidebar"] {
    background: rgba(6,8,12,0.9);
    backdrop-filter: blur(6px);
    border-right: 1px solid rgba(255,255,255,0.03);
    z-index: 10;
}
[data-testid="stSidebar"] * { color: #e6f7ff !important; }
.lottie-center {
    display:flex;
    justify-content:center;
    align-items:center;
    margin-top:18px;
    z-index:5;
}
.result-card {
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    z-index:5;
}
.music-button {
    position: fixed;
    bottom: 18px;
    right: 18px;
    width:56px;
    height:56px;
    border-radius:50%;
    background: linear-gradient(135deg,#00e0ff,#7b61ff);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
    cursor:pointer;
    z-index:99999;
    box-shadow: 0 10px 30px rgba(123,61,255,0.12);
    border: none;
}
.music-button:hover { transform: scale(1.05); }
.sidebar-bottom {
    position: sticky;
    bottom: 12px;
    width: calc(100% - 32px);
    margin: 8px 16px;
    z-index: 12;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# FITUR MUSIK (PILIH LAGU)
# =========================
music_folder = "music"
audio_b64 = None

if os.path.exists(music_folder):
    music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

    if len(music_files) == 0:
        st.sidebar.warning("⚠ Tidak ada file musik di folder 'music/'.")
    else:
        st.sidebar.markdown("#### 🎧 Player Musik")

        if "current_music" not in st.session_state:
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
        with open(music_path, "rb") as f:
            audio_data = f.read()
            audio_b64 = base64.b64encode(audio_data).decode()

        # Player manual di sidebar
        audio_html = f"""
        <audio id="bgMusic" controls loop style="width:100%">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            Browser Anda tidak mendukung audio.
        </audio>
        """
        st.sidebar.markdown(audio_html, unsafe_allow_html=True)
else:
    st.sidebar.warning("⚠ Folder 'music/' tidak ditemukan.")

# Tombol musik melayang (pause/play)
st.markdown(
    """
    <script>
    function toggleFloatingMusic(){
        const m=document.getElementById('bgMusic');
        if(!m)return;
        if(m.paused){m.play();}else{m.pause();}
    }
    </script>
    <button class="music-button" onclick="toggleFloatingMusic()" title="Play / Pause Musik">🎵</button>
    """,
    unsafe_allow_html=True,
)

# =========================
# HALAMAN HOME
# =========================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;margin-top:6px;'>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:#cfeffd;'>Sistem Cerdas untuk Deteksi Objek dan Klasifikasi Gambar</p>", unsafe_allow_html=True)

    lottie = load_lottie_url(LOTTIE_WELCOME)
    if lottie:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie, height=300, key="welcome_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Masuk ke Website", use_container_width=True):
            trans = load_lottie_url(LOTTIE_TRANSITION)
            if trans:
                st_lottie(trans, height=220, key="trans_lottie")
                time.sleep(1.2)
            st.session_state.page = "dashboard"
            st.rerun()

# =========================
# HALAMAN DASHBOARD
# =========================
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar")

    lottie_d = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_d:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_d, height=220, key="dashboard_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    # Tombol kembali
    st.sidebar.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)
    if st.sidebar.button("⬅ Kembali ke Halaman Awal", use_container_width=True):
        reset_to_home_state()
        st.rerun()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # LOAD MODEL
    # =========================
    @st.cache_resource
    def load_models():
        yolo_m = None
        clf = None
        try:
            yolo_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt")
            if os.path.exists(yolo_path):
                yolo_m = YOLO(yolo_path)
        except Exception as e:
            st.warning(f"⚠ Gagal memuat YOLO: {e}")
        try:
            cls_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5")
            if os.path.exists(cls_path):
                clf = tf.keras.models.load_model(cls_path)
        except Exception as e:
            st.warning(f"⚠ Gagal memuat classifier: {e}")
        return yolo_m, clf

    yolo_model, classifier = load_models()

    # =========================
    # UPLOAD & PROSES
    # =========================
    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="🖼 Gambar yang Diupload", use_column_width=True)
        except Exception as e:
            st.error(f"Gagal membuka gambar: {e}")
            img = None

        if img is not None:
            with st.spinner("🤖 AI sedang menganalisis gambar..."):
                time.sleep(1.2)

            if mode == "Deteksi Objek (YOLO)":
                st.info("🚀 Menjalankan deteksi objek...")
                if yolo_model is not None:
                    img_np = np.array(img)
                    results = yolo_model.predict(source=img_np)
                    result_img = results[0].plot()
                    st.image(result_img, caption="🎯 Hasil Deteksi", use_column_width=True)
                    buf = io.BytesIO()
                    Image.fromarray(result_img).save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button("📥 Download Hasil Deteksi", data=buf, file_name="hasil_deteksi_yolo.png", mime="image/png")
                else:
                    st.warning("Model YOLO tidak ditemukan.")
            else:
                st.info("🧠 Menjalankan klasifikasi gambar...")
                if classifier is not None:
                    img_resized = img.resize((128,128))
                    arr = image.img_to_array(img_resized)
                    arr = np.expand_dims(arr, axis=0) / 255.0
                    pred = classifier.predict(arr)
                    class_idx = int(np.argmax(pred, axis=1)[0])
                    confidence = float(np.max(pred))
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>🧾 Hasil Prediksi</h3>
                        <p><b>Kelas:</b> {class_idx}</p>
                        <p><b>Akurasi:</b> {confidence:.2%}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Model classifier tidak ditemukan.")
    else:
        st.markdown("<div class='result-card'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)
