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
from streamlit_lottie import st_lottie

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="AI Vision Pro Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================
# STYLING: DARK NEON + PARTICLES
# ==========================
st.markdown(
    """
    <style>
    /* Gradient background with slow movement */
    [data-testid="stAppViewContainer"] {
      background: radial-gradient(circle at 20% 20%, #0f2027, #203a43, #2c5364);
      background-size: 400% 400%;
      animation: gradientMove 18s ease infinite;
      color: #e6eef8;
      min-height:100vh;
    }
    @keyframes gradientMove {
      0% {background-position: 0% 50%;}
      50% {background-position: 100% 50%;}
      100% {background-position: 0% 50%;}
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
      background: rgba(8, 12, 20, 0.82);
      border-right: 1px solid rgba(0,224,255,0.06);
      color: #e6eef8;
      padding-top: 20px;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
      color: #00e0ff;
      text-shadow: 0 0 10px rgba(0,224,255,0.06);
    }

    /* Headings */
    h1, h2, h3 { font-family: 'Poppins', sans-serif; color: #e6eef8; text-align:center; }
    h1 { font-size: 40px; text-shadow:0 0 18px rgba(0,224,255,0.12); }

    /* Main content block */
    .main-block {
      background: rgba(6,8,16,0.55);
      border-radius: 14px;
      padding: 28px;
      box-shadow: 0 10px 40px rgba(3,6,20,0.6);
      border: 1px solid rgba(255,255,255,0.02);
    }

    /* Result card */
    .result-card {
      background: linear-gradient(90deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 6px 30px rgba(0,0,0,0.5);
      border: 1px solid rgba(255,255,255,0.02);
    }

    .warning-box {
      background-color: rgba(255, 193, 7, 0.06);
      border-left: 5px solid #ffc107;
      color: #ffc107;
      padding: 10px;
      border-radius: 8px;
      text-align: center;
      width: 95%;
      margin: 12px auto;
    }

    /* Buttons */
    .stButton>button, button[kind="primary"] {
      background: linear-gradient(90deg,#00e0ff,#0078ff);
      color: #fff;
      border-radius: 10px;
      border: none;
      padding: 8px 16px;
      transition: transform .12s ease, box-shadow .12s ease;
    }
    .stButton>button:hover { transform: scale(1.04); box-shadow: 0 10px 30px rgba(0,120,255,0.12); }

    /* Particle container behind everything */
    #particles-js {
      position: fixed;
      width: 100%;
      height: 100%;
      top: 0;
      left: 0;
      z-index: -1;
      pointer-events: none;
      mix-blend-mode: screen;
    }

    /* Make file uploader look nicer */
    .stFileUploader>div { border-radius: 12px; border: 1px solid rgba(255,255,255,0.03); padding: 10px; }

    /* Responsive */
    @media (max-width: 800px) {
      h1 { font-size: 28px; }
    }
    </style>

    <div id="particles-js"></div>
    <script src="https://cdn.jsdelivr.net/npm/particles.js@2.0.0/particles.min.js"></script>
    <script>
    particlesJS('particles-js', {
      "particles": {
        "number": {"value": 70, "density": {"enable": true,"value_area": 800}},
        "color": {"value": ["#5EEAD4","#60A5FA","#C084FC"]},
        "shape": {"type": "circle"},
        "opacity": {"value": 0.12, "random": true},
        "size": {"value": 2, "random": true},
        "line_linked": {"enable": true, "distance": 140, "color": "#60A5FA", "opacity": 0.08, "width": 1},
        "move": {"enable": true, "speed": 0.9, "direction": "none", "out_mode": "out"}
      },
      "interactivity": {"detect_on":"canvas","events":{"onhover":{"enable":false},"onclick":{"enable":false},"resize":true}}
    });
    </script>
    """,
    unsafe_allow_html=True,
)

# ==========================
# LOTTIE LOADER
# ==========================
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

# ==========================
# PAGE STATE
# ==========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==========================
# MODELS LOADER (cached)
# ==========================
@st.cache_resource
def load_models():
    yolo_model = None
    classifier = None
    errors = []
    # load YOLO if exists
    try:
        yolo_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt")
        if os.path.exists(yolo_path):
            yolo_model = YOLO(yolo_path)
        else:
            errors.append(f"YOLO model not found at {yolo_path}")
    except Exception as e:
        errors.append(f"YOLO load error: {e}")

    # load classifier if exists
    try:
        cls_path = os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5")
        if os.path.exists(cls_path):
            classifier = tf.keras.models.load_model(cls_path)
        else:
            errors.append(f"Classifier model not found at {cls_path}")
    except Exception as e:
        errors.append(f"Classifier load error: {e}")

    return yolo_model, classifier, errors

yolo_model, classifier, model_errors = load_models()

# ==========================
# WELCOME PAGE
# ==========================
if st.session_state.page == "home":
    st.markdown("<h1>🤖 AI Vision Pro Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#cfeffd;'>Sistem Deteksi & Klasifikasi Gambar Berbasis AI</h3>", unsafe_allow_html=True)
    lottie = load_lottie_url(LOTTIE_WELCOME)
    if lottie:
        st.markdown("<div style='display:flex; justify-content:center; align-items:center; margin-top:6px;'>", unsafe_allow_html=True)
        st_lottie(lottie, height=260, key="welcome_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='main-block' style='margin-top:15px;'>", unsafe_allow_html=True)
    st.markdown("""
        <p style='color:#dbeefe; text-align:center; font-size:16px;'>
        Selamat datang di AI Vision Pro — platform sederhana untuk mendeteksi objek dan mengklasifikasikan gambar menggunakan model YOLO dan classifier.
        </p>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚀 Masuk ke Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            with st.spinner("🔄 Memuat..."):
                l2 = load_lottie_url(LOTTIE_TRANSITION)
                if l2:
                    st_lottie(l2, height=160, key="trans_lottie")
                time.sleep(1.0)
            st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# DASHBOARD PAGE
# ==========================
elif st.session_state.page == "dashboard":
    st.markdown("<h1 style='text-align:center;'>🤖 AI Vision Pro Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#cfeffd;'>Sistem Deteksi dan Klasifikasi Gambar Cerdas</h3>", unsafe_allow_html=True)
    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=200, key="ai_lottie")
        st.markdown("</div>", unsafe_allow_html=True)

    # sidebar controls
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    # debug model load errors if any
    if model_errors:
        st.sidebar.error("Model load issues: see console area below.")

    # uploader & main area
    st.markdown("<div class='main-block'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="🖼️ Gambar yang Diupload", use_column_width=True)
        except Exception as e:
            st.error(f"Gagal membuka gambar: {e}")
            img = None
    else:
        # placeholder illustration
        placeholder_image = """
            <div style='background:#ffffff; height:220px; border-radius:8px; display:flex; align-items:center; justify-content:center;'>
                <img src="https://img.icons8.com/fluency/96/000000/inspection.png" alt="illustration" />
            </div>
        """
        st.markdown(placeholder_image, unsafe_allow_html=True)

    # run analysis if uploaded
    if uploaded_file and img is not None:
        with st.spinner("🤖 AI sedang menganalisis..."):
            time.sleep(0.8)
            if mode == "Deteksi Objek (YOLO)":
                st.info("🚀 Menjalankan deteksi objek...")
                if yolo_model is not None:
                    try:
                        img_np = np.array(img)
                        results = yolo_model.predict(source=img_np)
                        result_img = results[0].plot()
                        st.image(result_img, caption="🎯 Hasil Deteksi", use_column_width=True)
                        # prepare download
                        img_bytes = io.BytesIO()
                        Image.fromarray(result_img).save(img_bytes, format="PNG")
                        img_bytes.seek(0)
                        st.download_button("📥 Download Hasil Deteksi", data=img_bytes, file_name="hasil_deteksi_yolo.png", mime="image/png")
                    except Exception as e:
                        st.error(f"Gagal menjalankan YOLO: {e}")
                else:
                    st.warning("Model YOLO belum tersedia. Pastikan file model berada di folder `model/` dan bernama dengan benar.")
            elif mode == "Klasifikasi Gambar":
                st.info("🧠 Menjalankan klasifikasi gambar...")
                if classifier is not None:
                    try:
                        img_resized = img.resize((128,128))
                        img_arr = image.img_to_array(img_resized)
                        img_arr = np.expand_dims(img_arr, axis=0) / 255.0
                        prediction = classifier.predict(img_arr)
                        class_idx = int(np.argmax(prediction, axis=1)[0])
                        confidence = float(np.max(prediction))
                        st.markdown(f"""
                        <div class="result-card">
                            <h3>🧾 Hasil Prediksi</h3>
                            <p><b>Kelas:</b> {class_idx}</p>
                            <p><b>Confidence:</b> {confidence:.2%}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Gagal menjalankan classifier: {e}")
                else:
                    st.warning("Model classifier belum tersedia. Pastikan file model berada di folder `model/` dan bernama dengan benar.")
            elif mode == "AI Insight":
                st.info("🔍 Mode Insight Aktif")
                st.markdown("""
                <div class="result-card">
                    <h3>💬 Insight Otomatis</h3>
                    <p>AI menganalisis pola visual, bentuk, dan warna utama dari gambar.</p>
                    <p>Fitur insight ini masih berupa demo — kamu bisa kembangkan sesuai kebutuhan.</p>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu untuk memulai analisis.</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close main-block

    # Display model load errors (if any) in main area for debugging
    if model_errors:
        st.markdown("<div style='margin-top:12px;'><details><summary style='color:#ffc107;'>⚠️ Model Loader Info (klik untuk lihat)</summary>", unsafe_allow_html=True)
        for e in model_errors:
            st.markdown(f"- {e}", unsafe_allow_html=True)
        st.markdown("</details></div>", unsafe_allow_html=True)

    # Back button
    if st.sidebar.button("⬅️ Kembali ke Halaman Awal", key="back_to_home", use_container_width=True):
        st.session_state.page = "home"
        st.experimental_rerun()

# ==========================
# FOOTER
# ==========================
st.markdown("<hr style='border: 1px solid rgba(0,224,255,0.06);'>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aab8cf;'>© 2025 AI Vision Pro | Desain Futuristik</p>", unsafe_allow_html=True)
