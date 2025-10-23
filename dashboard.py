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
# BASIC PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI Vision Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# CSS + STYLING (Dark Futuristic)
# =========================
st.markdown(
    """
    <style>
    /* App background */
    [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at 10% 20%, #060615, #0f1220 80%);
        color: #e6eef8;
        min-height:100vh;
        overflow-x:hidden;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 12, 20, 0.75);
        backdrop-filter: blur(6px);
        border-right: 1px solid rgba(255,255,255,0.03);
        color: #e6eef8;
    }
    [data-testid="stSidebar"] * { color: #e6eef8 !important; }

    /* Headings */
    h1,h2,h3 { font-family: 'Poppins', sans-serif; color: #e6eef8; text-align:center; }
    .lottie-center { display:flex; justify-content:center; align-items:center; margin-top:10px; }

    /* Result card */
    .result-card {
        background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 6px 30px rgba(12,14,20,0.6);
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

    /* Floating music control (melayang) */
    .music-float {
        position: fixed;
        bottom: 22px;
        right: 22px;
        z-index: 99999;
        display:flex;
        gap:8px;
        align-items:center;
        font-family: 'Poppins', sans-serif;
    }
    .music-btn {
        background: linear-gradient(90deg,#5ef3c8,#6bb7ff);
        border: none;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:20px;
        cursor:pointer;
        box-shadow: 0 8px 30px rgba(50, 120, 255, 0.18);
        transition: transform .12s ease;
    }
    .music-btn:hover { transform: scale(1.06); }
    .music-btn.rot { animation: spin 4s linear infinite; }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Hidden audio element */
    #hidden-audio { display: none; }

    /* Particle canvas covers full screen behind content */
    #particle-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        pointer-events: none; /* don't block clicks */
        mix-blend-mode: screen;
    }

    /* Ensure main content is above the canvas */
    .viewer > div:first-child { position: relative; z-index: 5; }

    /* small responsive tweaks */
    @media (max-width: 700px) {
        .music-btn { width:48px; height:48px; font-size:18px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# BACKGROUND PARTICLE CANVAS (neon blue-purple particles)
# =========================
# We'll inject a canvas + JS that draws animated particles.
particle_js = r"""
<canvas id="particle-canvas"></canvas>
<script>
(function(){
    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    let particles = [];
    let w = canvas.width = window.innerWidth;
    let h = canvas.height = window.innerHeight;
    const colors = [
        'rgba(110, 89, 255, 0.12)', // purple
        'rgba(79, 195, 255, 0.12)', // blue
        'rgba(130, 99, 255, 0.08)'
    ];

    function rand(min, max){ return Math.random()*(max-min)+min; }

    function resize(){
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);

    function createParticles(count){
        particles = [];
        for(let i=0; i<count; i++){
            particles.push({
                x: Math.random()*w,
                y: Math.random()*h,
                r: rand(0.6, 3.2),
                vx: rand(-0.2, 0.2),
                vy: rand(-0.05, 0.05),
                hue: colors[Math.floor(Math.random()*colors.length)],
                alpha: rand(0.03, 0.18),
                amp: rand(10,40),
                phase: Math.random()*Math.PI*2
            });
        }
    }

    function draw(){
        ctx.clearRect(0,0,w,h);
        // soft gradient background overlay for glow
        const g = ctx.createLinearGradient(0,0,w,h);
        g.addColorStop(0, 'rgba(6,7,21,0.12)');
        g.addColorStop(1, 'rgba(17,12,36,0.12)');
        ctx.fillStyle = g;
        ctx.fillRect(0,0,w,h);

        for(let p of particles){
            p.x += p.vx + Math.sin(p.phase)*0.02;
            p.y += p.vy + Math.cos(p.phase)*0.01;
            p.phase += 0.003;

            // wrap
            if(p.x < -50) p.x = w+50;
            if(p.x > w+50) p.x = -50;
            if(p.y < -50) p.y = h+50;
            if(p.y > h+50) p.y = -50;

            ctx.beginPath();
            const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r*12);
            gradient.addColorStop(0, p.hue.replace('0.12','0.30') );
            gradient.addColorStop(0.4, p.hue);
            gradient.addColorStop(1, 'rgba(0,0,0,0)');
            ctx.fillStyle = gradient;
            ctx.arc(p.x, p.y, p.r*8, 0, Math.PI*2);
            ctx.fill();

            // small core
            ctx.beginPath();
            ctx.fillStyle = p.hue.replace('0.12', String(Math.min(0.9, p.alpha*8)));
            ctx.arc(p.x, p.y, p.r, 0, Math.PI*2);
            ctx.fill();
        }
        requestAnimationFrame(draw);
    }

    createParticles(Math.round((window.innerWidth+window.innerHeight)/50));
    draw();
})();
</script>
"""
st.markdown(particle_js, unsafe_allow_html=True)

# =========================
# LOTTIE HELPERS
# =========================
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

# =========================
# PAGE SYSTEM
# =========================
if "page" not in st.session_state:
    st.session_state.page = "home"

# =========================
# MUSIC / PLAYLIST SETUP
# - persistent audio element is created on client window (window.bgMusic)
# - Python passes a mapping of filename -> base64 dataURL for all mp3s in /music
# =========================
music_folder = "music"
music_files = []
music_map = {}  # filename -> data:... base64

if os.path.exists(music_folder):
    for f in sorted(os.listdir(music_folder)):
        if f.lower().endswith(".mp3"):
            path = os.path.join(music_folder, f)
            try:
                with open(path, "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode()
                    data_url = f"data:audio/mp3;base64,{b64}"
                    music_files.append(f)
                    music_map[f] = data_url
            except Exception as e:
                # skip unreadable file
                pass

# Initialize session state for playlist
if "current_track" not in st.session_state:
    st.session_state.current_track = music_files[0] if len(music_files) > 0 else None
if "music_visible" not in st.session_state:
    st.session_state.music_visible = True
if "autoplay_on_first_click" not in st.session_state:
    st.session_state.autoplay_on_first_click = True  # allow first click to play

# Inject the music map into the page and create persistent player if not exists
# Only inject JS if there is at least one music file
if len(music_files) > 0:
    music_map_json = json.dumps(music_map)
    # JS: create window.bgMusic and window.musicControls once; append to body so rerun doesn't remove
    persistent_music_js = f"""
    <script>
    (function(){{
        window.__aiVisionMusic = window.__aiVisionMusic || {{}};
        // create a map of tracks
        window.__aiVisionMusic.trackMap = {music_map_json};
        // create audio element once
        if (!window.__aiVisionMusic.bgMusic) {{
            const audio = document.createElement('audio');
            audio.id = 'bgMusic';
            audio.loop = true;
            audio.style.display = 'none'; // hidden, controls provided by custom UI
            document.body.appendChild(audio);
            window.__aiVisionMusic.bgMusic = audio;
            window.__aiVisionMusic.isPlaying = false;
            window.__aiVisionMusic.current = null;
        }}

        // create floating controls container if not exists
        if (!window.__aiVisionMusic.controls) {{
            const cont = document.createElement('div');
            cont.className = 'music-float';
            cont.id = 'music-float';
            // Play/Pause button
            const btn = document.createElement('button');
            btn.className = 'music-btn';
            btn.id = 'music-play-btn';
            btn.innerHTML = '🎵';
            btn.onclick = function(e){{
                const aud = window.__aiVisionMusic.bgMusic;
                // try to play or pause
                if (!window.__aiVisionMusic.isPlaying) {{
                    aud.play().then(()=>{{
                        window.__aiVisionMusic.isPlaying = true;
                        btn.innerHTML = '🔊';
                        btn.classList.add('rot');
                    }}).catch((err)=>{{
                        // show a small console note
                        console.log('play failed', err);
                        // still toggle UI to encourage user
                        // do not set isPlaying true
                    }});
                }} else {{
                    aud.pause();
                    window.__aiVisionMusic.isPlaying = false;
                    btn.innerHTML = '🎵';
                    btn.classList.remove('rot');
                }}
            }};
            cont.appendChild(btn);

            // Prev button
            const prev = document.createElement('button');
            prev.className = 'music-btn';
            prev.id = 'music-prev-btn';
            prev.innerHTML = '⏮';
            prev.onclick = function(){{
                const keys = Object.keys(window.__aiVisionMusic.trackMap);
                if (keys.length < 1) return;
                let idx = keys.indexOf(window.__aiVisionMusic.current);
                if (idx <= 0) idx = keys.length-1; else idx--;
                const nextKey = keys[idx];
                window.__aiVisionMusic.bgMusic.src = window.__aiVisionMusic.trackMap[nextKey];
                window.__aiVisionMusic.current = nextKey;
                if (window.__aiVisionMusic.isPlaying) window.__aiVisionMusic.bgMusic.play();
            }};
            cont.appendChild(prev);

            // Next button
            const next = document.createElement('button');
            next.className = 'music-btn';
            next.id = 'music-next-btn';
            next.innerHTML = '⏭';
            next.onclick = function(){{
                const keys = Object.keys(window.__aiVisionMusic.trackMap);
                if (keys.length < 1) return;
                let idx = keys.indexOf(window.__aiVisionMusic.current);
                if (idx === -1 || idx >= keys.length-1) idx = 0; else idx++;
                const nextKey = keys[idx];
                window.__aiVisionMusic.bgMusic.src = window.__aiVisionMusic.trackMap[nextKey];
                window.__aiVisionMusic.current = nextKey;
                if (window.__aiVisionMusic.isPlaying) window.__aiVisionMusic.bgMusic.play();
            }};
            cont.appendChild(next);

            // Show / hide UI toggle (does not pause music)
            const hide = document.createElement('button');
            hide.className = 'music-btn';
            hide.id = 'music-hide-btn';
            hide.innerHTML = '👁️';
            hide.onclick = function(){{
                // toggle visibility of the float (but keep audio playing)
                const float = document.getElementById('music-float');
                if (!float) return;
                if (float.style.display === 'none') {{
                    float.style.display = 'flex';
                    // save visible state to window so it persists across reruns
                    window.__aiVisionMusic.visible = true;
                }} else {{
                    float.style.display = 'none';
                    window.__aiVisionMusic.visible = false;
                }}
            }};
            cont.appendChild(hide);

            document.body.appendChild(cont);
            window.__aiVisionMusic.controls = cont;
            // initial hide/show
            if (window.__aiVisionMusic.visible === false) {{
                cont.style.display = 'none';
            }}
        }}
    }})();
    </script>
    """
    st.markdown(persistent_music_js, unsafe_allow_html=True)

    # Sidebar UI: playlist selectbox + visibility toggle
    st.sidebar.markdown("### 🎧 Musik (Playlist)")
    if len(music_files) == 0:
        st.sidebar.warning("Tidak ada file .mp3 di folder `music/`.")
    else:
        # create selectbox; store selection in session_state
        if "selected_track" not in st.session_state:
            st.session_state.selected_track = st.session_state.current_track or music_files[0]
        # build options
        selected = st.sidebar.selectbox("Pilih lagu:", options=music_files, index=music_files.index(st.session_state.selected_track))
        # update session state & instruct client to change source
        if selected != st.session_state.selected_track:
            st.session_state.selected_track = selected
            # set current_track and issue JS to set src (and autoplay if playing)
            data_url = music_map[selected]
            set_src_js = f"""
            <script>
            (function(){{
                if(window.__aiVisionMusic && window.__aiVisionMusic.bgMusic){{
                    window.__aiVisionMusic.bgMusic.src = "{data_url}";
                    window.__aiVisionMusic.current = "{selected}";
                    // if the play button was active, try to resume playback
                    if (window.__aiVisionMusic.isPlaying){{
                        window.__aiVisionMusic.bgMusic.play().catch(e=>console.log('resume play failed', e));
                        // update UI
                        const b = document.getElementById('music-play-btn');
                        if (b) {{ b.innerHTML='🔊'; b.classList.add('rot'); }}
                    }} else {{
                        // keep paused but update current
                        const b = document.getElementById('music-play-btn');
                        if (b) {{ b.innerHTML='🎵'; b.classList.remove('rot'); }}
                    }}
                }}
            }})();
            </script>
            """
            st.markdown(set_src_js, unsafe_allow_html=True)
            # slight rerun to ensure sidebar updates reflect
            st.experimental_rerun()

    # show/hide player option in sidebar (this only toggles visibility of float)
    visible = st.sidebar.checkbox("Tampilkan Kontrol Musik (melayang)", value=True)
    # Sync to client
    if visible:
        st.markdown(
            """
            <script>
            (function(){
                if (window.__aiVisionMusic && window.__aiVisionMusic.controls){
                    window.__aiVisionMusic.controls.style.display = 'flex';
                    window.__aiVisionMusic.visible = true;
                }
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <script>
            (function(){
                if (window.__aiVisionMusic && window.__aiVisionMusic.controls){
                    window.__aiVisionMusic.controls.style.display = 'none';
                    window.__aiVisionMusic.visible = false;
                }
            })();
            </script>
            """,
            unsafe_allow_html=True,
        )

    # Ensure initial src is set (first-run)
    if st.session_state.current_track:
        init_js = f"""
        <script>
        (function(){{
            if(window.__aiVisionMusic && window.__aiVisionMusic.bgMusic){{
                // only set if not already set to avoid reload
                if(!window.__aiVisionMusic.bgMusic.src || window.__aiVisionMusic.current !== "{st.session_state.current_track}"){{
                    window.__aiVisionMusic.bgMusic.src = "{music_map[st.session_state.current_track]}";
                    window.__aiVisionMusic.current = "{st.session_state.current_track}";
                }}
            }}
        }})();
        </script>
        """
        st.markdown(init_js, unsafe_allow_html=True)
else:
    # no music folder or no files
    st.sidebar.warning("Folder `music/` tidak ditemukan atau tidak ada file .mp3 di dalamnya.")

# =========================
# Rest of original app: Welcome and Dashboard + Load models
# =========================

# FUNGSI LOAD LOTTIE (reuse)
def load_lottie_url_local(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# set page state
if "page" not in st.session_state:
    st.session_state.page = "home"

# WELCOME PAGE
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>🤖 Selamat Datang di AI Vision Pro</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Sistem Cerdas untuk Deteksi Objek dan Klasifikasi Gambar</p>", unsafe_allow_html=True)

    lottie = load_lottie_url_local(LOTTIE_WELCOME)
    if lottie:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie, height=300, key="welcome_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 Masuk ke Website", use_container_width=True):
            st.session_state.page = "dashboard"
            with st.spinner("🔄 Memuat halaman..."):
                trans_anim = load_lottie_url_local(LOTTIE_TRANSITION)
                if trans_anim:
                    st_lottie(trans_anim, height=180, key="transition_anim")
                time.sleep(1.2)
            st.rerun()

# DASHBOARD PAGE
elif st.session_state.page == "dashboard":
    st.title("🤖 AI Vision Pro Dashboard")
    st.markdown("### Sistem Deteksi dan Klasifikasi Gambar Cerdas")

    lottie_ai = load_lottie_url_local(LOTTIE_DASHBOARD)
    if lottie_ai:
        st.markdown("<div class='lottie-center'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=220, key="ai_anim")
        st.markdown("</div>", unsafe_allow_html=True)

    # Sidebar: Mode AI
    st.sidebar.header("🧠 Mode AI")
    mode = st.sidebar.radio("Pilih Mode:", ["Deteksi Objek (YOLO)", "Klasifikasi Gambar", "AI Insight"])
    st.sidebar.markdown("---")
    st.sidebar.info("💡 Unggah gambar, lalu biarkan AI menganalisis secara otomatis.")
    st.sidebar.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.sidebar.markdown("---")

    # Load models (cache)
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

    # Back button
    if st.sidebar.button("⬅️ Kembali ke Halaman Awal", key="back_to_home_fixed", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
