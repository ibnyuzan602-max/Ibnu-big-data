import streamlit as st
import os, json, time, requests, io
import numpy as np
import tensorflow as tf
from ultralytics import YOLO
from PIL import Image
from tensorflow.keras.preprocessing import image
from streamlit_lottie import st_lottie

# ================
# CONFIG
# ================
st.set_page_config(page_title="AI Vision Pro", page_icon="🤖", layout="wide")

# ================
# CSS DASAR
# ================
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at 10% 20%, #0b0b17, #1b1b2a 80%);
    color: white;
}
[data-testid="stSidebar"] {
    background: rgba(15,15,25,0.95);
    border-right: 1px solid #333;
}
h1, h2, h3 { text-align:center; font-family:'Poppins',sans-serif; }
.result-card {
    background: rgba(255,255,255,0.05);
    border-radius: 15px;
    padding: 20px;
    margin-top: 20px;
    text-align: center;
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

# ================
# LOTTIE HELPER
# ================
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

# ================
# SISTEM HALAMAN
# ================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ================
# FLOATING MUSIC BUTTON 🎵
# ================
def floating_music_button():
    MUSIC_FOLDER = "musik"
    os.makedirs(MUSIC_FOLDER, exist_ok=True)
    TRACKS = [
        os.path.join(MUSIC_FOLDER, "wildwest.mp3"),
        os.path.join(MUSIC_FOLDER, "lostsagalobby.mp3"),
    ]
    existing_tracks = [p for p in TRACKS if os.path.exists(p)]
    if not existing_tracks:
        st.warning("🎵 File musik belum ditemukan di folder 'musik/'.")
        return
    
    playlist_js = json.dumps(existing_tracks)
    
    html = f"""
    <div style="
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 99999;
    ">
        <button id="musicBtn" 
            style="
                background-color:#1e1e2f;
                border:none;
                color:white;
                font-size:22px;
                width:55px;
                height:55px;
                border-radius:50%;
                cursor:pointer;
                box-shadow:0 0 10px rgba(0,0,0,0.4);
            ">🎵</button>
    </div>
    <audio id="bgMusic" loop></audio>

    <script>
    const tracks = {playlist_js};
    let audio = document.getElementById("bgMusic");
    let btn = document.getElementById("musicBtn");
    let playing = false;
    let current = 0;

    function playTrack() {{
        audio.src = tracks[current];
        audio.volume = 0.6;
        audio.play().catch(e => console.log("Klik dibutuhkan untuk memulai musik."));
    }}

    btn.onclick = function() {{
        if (!playing) {{
            playTrack();
            btn.innerText = "⏸️";
            playing = true;
        }} else {{
            audio.pause();
            btn.innerText = "🎵";
            playing = false;
        }}
    }}

    audio.addEventListener("ended", () => {{
        current = (current + 1) % tracks.length;
        playTrack();
    }});
    </script>
    """
    st.components.v1.html(html, height=80, scrolling=False)

# ================
# HALAMAN HOME
# ================
if st.session_state.page == "home":
    st.markdown("<h1>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sistem Cerdas untuk Deteksi Objek dan Klasifikasi Gambar</p>", unsafe_allow_html=True)
    
    lottie = load_lottie_url(LOTTIE_WELCOME)
    if lottie:
        st_lottie(lottie, height=300, key="welcome_anim")
    
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        if st.button("🚀 Masuk ke Website", use_container_width=True):
            st.session_state.page = "dashboard"
            with st.spinner("🔄 Memuat halaman..."):
                trans_anim = load_lottie_url(LOTTIE_TRANSITION)
                if trans_anim:
                    st_lottie(trans_anim, height=200, key="transition_anim")
                time.sleep(1.5)
            st.rerun()
    
    floating_music_button()

# ================
# HALAMAN DASHBOARD
# ================
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    floating_music_button()

    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st_lottie(lottie_ai, height=250, key="ai_anim")

    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])

    @st.cache_resource
    def load_models():
        try:
            yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
            classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
            return yolo_model, classifier
        except Exception as e:
            st.warning(f"⚠️ Gagal memuat model. {e}")
            return None, None

    yolo_model, classifier = load_models()

    uploaded_file = st.file_uploader("📤 Unggah Gambar", type=["jpg", "jpeg", "png"])
    if uploaded_file and yolo_model and classifier:
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Gambar yang diunggah", use_container_width=True)
        time.sleep(1.2)
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
                <p><b>Kelas:</b> Index {class_index}</p>
                <p><b>Akurasi:</b> {confidence:.2%}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("🔍 Insight Otomatis Aktif")
            st.markdown("<div class='result-card'>AI menganalisis pola dan warna utama.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)

    if st.sidebar.button("⬅️ Kembali ke Halaman Awal"):
        st.session_state.page = "home"
        st.rerun()
