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
import base64  # untuk encode musik ke base64 agar bisa autoplay lewat HTML (manual play)

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
# CSS - DARK FUTURISTIK + PARTIKEL (TANPA MENGHAPUS BAGIAN APAPUN)
# =========================
st.markdown(
    """
<style>
/* Base app background (animated gradient) */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #061021, #0b0b17 40%, #111025 100%);
    background-size: 300% 300%;
    animation: bgShift 18s ease infinite;
    color: white;
    position: relative;
    overflow: visible;
}
@keyframes bgShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* particle canvas sits behind content */
#particle-canvas {
    position: fixed;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
    mix-blend-mode: screen;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(8,10,18,0.88);
    backdrop-filter: blur(6px);
    border-right: 1px solid rgba(255,255,255,0.03);
    z-index: 10;
}
[data-testid="stSidebar"] * { color: white !important; }

/* Headings and layout elements above particle layer */
h1, h2, h3 {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    position: relative;
    z-index: 5;
}

/* result card / warning - ensure above particles */
.result-card, .warning-box, .lottie-center, .stImage {
    position: relative;
    z-index: 5;
}

/* Music floating button */
.music-button {
    position: fixed;
    bottom: 20px;
    right: 25px;
    background: linear-gradient(135deg,#00e0ff,#7b61ff);
    color: #001;
    border-radius: 50%;
    width: 56px;
    height: 56px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    cursor:pointer;
    z-index:99999;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    transition: transform .12s ease;
}
.music-button:hover { transform: scale(1.06); }

/* rotating class for active */
.rotating { animation: rot 4s linear infinite; }
@keyframes rot { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }

/* small responsive tweak so canvas doesn't cover UI interactions */
@media (max-width: 680px) {
    .music-button { width:50px; height:50px; font-size:20px;}
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# PARTICLE CANVAS JS (blue-purple soft particles)
# =========================
# Inject a canvas and JS that draws subtle particles. This does not modify any existing Python logic.
particle_js = """
<canvas id="particle-canvas"></canvas>
<script>
(function(){
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let w, h, particles;
    const colors = ['rgba(96,165,250,0.14)','rgba(123,61,255,0.12)','rgba(94,234,210,0.10)'];

    function resize(){ w = canvas.width = innerWidth; h = canvas.height = innerHeight; initParticles(); }
    window.addEventListener('resize', resize);

    function rand(min,max){ return Math.random()*(max-min)+min; }

    function initParticles(){
        const count = Math.round((w*h)/70000); // adaptive density
        particles = [];
        for(let i=0;i<count;i++){
            particles.push({
                x: Math.random()*w,
                y: Math.random()*h,
                r: rand(0.6, 3.2),
                vx: rand(-0.2,0.2),
                vy: rand(-0.05,0.05),
                color: colors[Math.floor(Math.random()*colors.length)],
                phase: Math.random()*Math.PI*2,
                amp: rand(6,30)
            });
        }
    }

    function draw(){
        ctx.clearRect(0,0,w,h);
        for(let p of particles){
            p.phase += 0.002;
            p.x += p.vx + Math.sin(p.phase)*0.02;
            p.y += p.vy + Math.cos(p.phase)*0.01;

            // wrap
            if(p.x < -50) p.x = w + 50;
            if(p.x > w + 50) p.x = -50;
            if(p.y < -50) p.y = h + 50;
            if(p.y > h + 50) p.y = -50;

            // glow
            const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r*12);
            const colorMid = p.color.replace('0.12','0.28');
            grd.addColorStop(0, colorMid);
            grd.addColorStop(0.4, p.color);
            grd.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = grd;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r*8, 0, Math.PI*2);
            ctx.fill();

            // core dot
            ctx.beginPath();
            ctx.fillStyle = p.color.replace('0.12','0.9');
            ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
            ctx.fill();
        }
        requestAnimationFrame(draw);
    }

    resize();
    draw();
})();
</script>
"""
st.markdown(particle_js, unsafe_allow_html=True)

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
# ANIMASI LOTTIE URLS
# =========================
LOTTIE_WELCOME = "https://assets10.lottiefiles.com/packages/lf20_pwohahvd.json"
LOTTIE_DASHBOARD = "https://assets10.lottiefiles.com/packages/lf20_t24tpvcu.json"
LOTTIE_TRANSITION = "https://assets2.lottiefiles.com/packages/lf20_touohxv0.json"

# =========================
# SESSION PAGE (jika belum ada)
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# (keep any other session keys the app used previously)
# =========================
# SISTEM MUSIK (multi-file playlist di sidebar + floating control)
# =========================
music_folder = "music"
music_files = []
music_map = {}

if os.path.exists(music_folder):
    for fname in sorted(os.listdir(music_folder)):
        if fname.lower().endswith(".mp3"):
            music_files.append(fname)
            # preload base64 (could be heavy if many large files)
            try:
                with open(os.path.join(music_folder, fname), "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode()
                    music_map[fname] = "data:audio/mp3;base64," + b64
            except Exception:
                # skip unreadable files
                pass

# ensure session defaults
if "current_music" not in st.session_state:
    st.session_state.current_music = music_files[0] if len(music_files) > 0 else None
if "music_controls_visible" not in st.session_state:
    st.session_state.music_controls_visible = True

# inject persistent client-side player & floating controls (only if there are tracks)
if len(music_map) > 0:
    music_map_json = json.dumps(music_map)  # safe encoded map

    persistent_music_js = f"""
<script>
(function(){{
    window.__aiVisionMusic = window.__aiVisionMusic || {{}};
    // track map
    window.__aiVisionMusic.trackMap = window.__aiVisionMusic.trackMap || {music_map_json};

    // create persistent audio element once
    if (!window.__aiVisionMusic.bgMusic) {{
        const audio = document.createElement('audio');
        audio.id = 'bgMusic';
        audio.loop = true;
        audio.style.display = 'none';
        document.body.appendChild(audio);
        window.__aiVisionMusic.bgMusic = audio;
        window.__aiVisionMusic.isPlaying = false;
        window.__aiVisionMusic.current = null;
    }}

    // create floating controls once
    if (!window.__aiVisionMusic.controls) {{
        const cont = document.createElement('div');
        cont.id = 'ai-music-controls';
        cont.style.position = 'fixed';
        cont.style.bottom = '18px';
        cont.style.right = '18px';
        cont.style.display = 'flex';
        cont.style.gap = '8px';
        cont.style.zIndex = 99999;

        function makeBtn(html, onclick){{
            const b = document.createElement('button');
            b.className = 'music-button';
            b.innerHTML = html;
            b.onclick = onclick;
            return b;
        }}

        const playBtn = makeBtn('🎵', function(){{
            const aud = window.__aiVisionMusic.bgMusic;
            if (!window.__aiVisionMusic.isPlaying) {{
                // try play
                aud.play().then(()=>{{
                    window.__aiVisionMusic.isPlaying = true;
                    playBtn.innerHTML = '🔊';
                    playBtn.classList.add('rotating');
                }}).catch(err=>console.log('play failed',err));
            }} else {{
                aud.pause();
                window.__aiVisionMusic.isPlaying = false;
                playBtn.innerHTML = '🎵';
                playBtn.classList.remove('rotating');
            }}
        }});

        const prevBtn = makeBtn('⏮', function(){{
            const keys = Object.keys(window.__aiVisionMusic.trackMap);
            if (keys.length === 0) return;
            let idx = keys.indexOf(window.__aiVisionMusic.current);
            if (idx <= 0) idx = keys.length - 1; else idx--;
            const k = keys[idx];
            window.__aiVisionMusic.bgMusic.src = window.__aiVisionMusic.trackMap[k];
            window.__aiVisionMusic.current = k;
            if (window.__aiVisionMusic.isPlaying) window.__aiVisionMusic.bgMusic.play();
        }});

        const nextBtn = makeBtn('⏭', function(){{
            const keys = Object.keys(window.__aiVisionMusic.trackMap);
            if (keys.length === 0) return;
            let idx = keys.indexOf(window.__aiVisionMusic.current);
            if (idx === -1 || idx >= keys.length-1) idx = 0; else idx++;
            const k = keys[idx];
            window.__aiVisionMusic.bgMusic.src = window.__aiVisionMusic.trackMap[k];
            window.__aiVisionMusic.current = k;
            if (window.__aiVisionMusic.isPlaying) window.__aiVisionMusic.bgMusic.play();
        }});

        const hideBtn = makeBtn('👁️', function(){{
            if (cont.style.display === 'none') {{
                cont.style.display = 'flex';
                window.__aiVisionMusic.visible = true;
            }} else {{
                cont.style.display = 'none';
                window.__aiVisionMusic.visible = false;
            }}
        }});

        cont.appendChild(prevBtn);
        cont.appendChild(playBtn);
        cont.appendChild(nextBtn);
        cont.appendChild(hideBtn);

        document.body.appendChild(cont);
        window.__aiVisionMusic.controls = cont;

        // restore visibility if saved
        if (window.__aiVisionMusic.visible === false) {{
            cont.style.display = 'none';
        }}
    }}
}})();
</script>
"""
    st.markdown(persistent_music_js, unsafe_allow_html=True)

    # Sidebar playlist UI (select box)
    st.sidebar.markdown("#### 🎧 Player Musik")
    if len(music_files) == 0:
        st.sidebar.warning("⚠ Tidak ada file .mp3 di folder 'music/'.")
    else:
        sel = st.sidebar.selectbox("Pilih Lagu:", options=music_files, index=music_files.index(st.session_state.current_music) if st.session_state.current_music in music_files else 0)
        if sel != st.session_state.current_music:
            st.session_state.current_music = sel
            # instruct client to change current src and keep playing state
            data_url = music_map.get(sel, "")
            set_src_js = f"""
<script>
(function(){{
    if (window.__aiVisionMusic && window.__aiVisionMusic.bgMusic){{
        window.__aiVisionMusic.bgMusic.src = "{data_url}";
        window.__aiVisionMusic.current = "{sel}";
        try {{
            if (window.__aiVisionMusic.isPlaying) window.__aiVisionMusic.bgMusic.play();
        }} catch(e){{ console.log('resume failed', e); }}
    }}
}})();
</script>
"""
            st.markdown(set_src_js, unsafe_allow_html=True)
            # reflect immediately
            st.rerun()

        # ensure initial src is set (when first load)
        if st.session_state.current_music:
            init_js = f"""
<script>
(function(){{
    if (window.__aiVisionMusic && window.__aiVisionMusic.bgMusic) {{
        if (!window.__aiVisionMusic.bgMusic.src || window.__aiVisionMusic.current !== "{st.session_state.current_music}") {{
            window.__aiVisionMusic.bgMusic.src = "{music_map[st.session_state.current_music]}";
            window.__aiVisionMusic.current = "{st.session_state.current_music}";
        }}
    }}
}})();
</script>
"""
            st.markdown(init_js, unsafe_allow_html=True)

else:
    # no music folder or files
    st.sidebar.warning("⚠ Folder 'music/' tidak ditemukan atau tidak ada .mp3 di dalamnya.")

# =========================
# HALAMAN: WELCOME / DASHBOARD (tetap menjaga semua bagian)
# =========================
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sistem Cerdas untuk Deteksi Objek dan Klasifikasi Gambar</p>", unsafe_allow_html=True)

    lottie = load_lottie_url(LOTTIE_WELCOME)
    if lottie:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie, height=300, key="welcome_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        if st.button("🚀 Masuk ke Website", use_container_width=True):
            st.session_state.page = "dashboard"
            with st.spinner("🔄 Memuat halaman..."):
                anim = load_lottie_url(LOTTIE_TRANSITION)
                if anim:
                    st_lottie(anim, height=200, key="transition_anim")
                time.sleep(1.5)
            st.rerun()

# =========================
# DASHBOARD PAGE
# =========================
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    lottie_ai = load_lottie_url(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=250, key="ai_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar controls: Mode AI (keep original behavior)
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Ensure Back button appears (in sidebar) when not on home
    if st.sidebar.button("⬅ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    # Load models (cached)
    @st.cache_resource
    def load_models():
        try:
            yolo_model = YOLO(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 4.pt"))
            classifier = tf.keras.models.load_model(os.path.join("model", "Ibnu Hawari Yuzan_Laporan 2.h5"))
            return yolo_model, classifier
        except Exception as e:
            st.warning(f"⚠ Gagal memuat model: {e}")
            return None, None

    yolo_model, classifier = load_models()

    # File uploader and main logic
    uploaded_file = st.file_uploader("📤 Unggah Gambar (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file and yolo_model and classifier:
        try:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="🖼 Gambar yang Diupload", use_container_width=True)
        except Exception as e:
            st.error(f"Gagal membuka gambar: {e}")
            img = None

        if img is not None:
            with st.spinner("🤖 AI sedang menganalisis gambar..."):
                time.sleep(1.5)

            if mode == "Deteksi Objek (YOLO)":
                st.info("🚀 Menjalankan deteksi objek...")
                try:
                    img_cv2 = np.array(img)
                    results = yolo_model.predict(source=img_cv2)
                    result_img = results[0].plot()
                    st.image(result_img, caption="🎯 Hasil Deteksi", use_container_width=True)
                    img_bytes = io.BytesIO()
                    Image.fromarray(result_img).save(img_bytes, format="PNG")
                    img_bytes.seek(0)
                    st.download_button("📥 Download Hasil Deteksi", data=img_bytes, file_name="hasil_deteksi_yolo.png", mime="image/png")
                except Exception as e:
                    st.error(f"Gagal menjalankan YOLO: {e}")

            elif mode == "Klasifikasi Gambar":
                st.info("🧠 Menjalankan klasifikasi gambar...")
                try:
                    img_resized = img.resize((128,128))
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
                except Exception as e:
                    st.error(f"Gagal menjalankan classifier: {e}")

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
        st.markdown("<div class='warning-box'>⚠ Model AI gagal dimuat. Harap periksa path model.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>📂 Silakan unggah gambar terlebih dahulu.</div>", unsafe_allow_html=True)
