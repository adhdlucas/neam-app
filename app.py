import streamlit as st
import datetime
import os
import io
import re
import base64
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# ---------------------------------------------------------
# PAGE CONFIGURATION & THEME (CLEAN WHITE / COBALT / EMERALD)
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEAM | Executive Academic Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    .portal-banner {
        background: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        padding: 16px 28px;
        margin: -4rem -4rem 1.5rem -4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .portal-brand {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        letter-spacing: -0.02em;
    }
    .portal-sub {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
    }

    .role-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .role-card:hover {
        border-color: #1e40af;
        box-shadow: 0 6px 12px rgba(30,64,175,0.08);
    }
    .role-icon {
        font-size: 2.8rem;
        margin-bottom: 12px;
    }
    .role-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 6px;
    }
    .role-desc {
        font-size: 0.85rem;
        color: #64748b;
        line-height: 1.5;
        min-height: 60px;
    }

    .warrior-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .warrior-avatar {
        font-size: 2.2rem;
        background: #f1f5f9;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #059669;
    }
    .gear-badges {
        display: flex;
        gap: 8px;
        margin-top: 6px;
    }
    .gear-badge {
        font-size: 0.72rem;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    .gear-unlocked {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
    }
    .gear-locked {
        background-color: #f1f5f9;
        color: #94a3b8;
        border: 1px dashed #cbd5e1;
    }

    .instruction-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .instruction-text {
        font-size: 0.95rem;
        line-height: 1.55;
        color: #1e293b;
        margin-bottom: 16px;
    }

    input, textarea, [data-testid="stChatInput"] textarea {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 8px !important;
    }

    .stButton>button {
        background-color: #1e40af;
        color: #ffffff;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: #ffffff;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# GEMINI & ELEVENLABS CLIENT INITIALIZATION
# ---------------------------------------------------------
raw_keys = st.secrets.get("GEMINI_API_KEY", "")
api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not api_keys:
    st.error("⚠️ GEMINI_API_KEY missing. Please configure it in Streamlit Secrets.")
    st.stop()

elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY", None)

def get_gemini_client(key: str):
    return genai.Client(api_key=key)

# Modelos oficiales válidos de Google GenAI SDK con fallback
MODEL_CANDIDATES = ["gemini-2.5-flash", "gemini-1.5-flash"]

# Socratic sparring streaming optimizado para ultra-baja latencia (<1s)
def stream_socratic_response(prompt_text: str, system_instr: str):
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.6,
        max_output_tokens=220,
    )
    last_err = None
    for model_name in MODEL_CANDIDATES:
        for key in api_keys:
            try:
                client = get_gemini_client(key)
                response_stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=[prompt_text],
                    config=config
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                last_err = e
                continue
    yield f"⚠️ Latency spike on the model endpoint. Please retry. ({last_err})"

# Generador de guiones y blueprints
def generate_studio_text(prompt_text: str):
    config = types.GenerateContentConfig(temperature=0.7)
    last_err = None
    for model_name in MODEL_CANDIDATES:
        for key in api_keys:
            try:
                client = get_gemini_client(key)
                resp = client.models.generate_content(
                    model=model_name,
                    contents=[prompt_text],
                    config=config
                )
                if resp and resp.text:
                    return resp.text
            except Exception as e:
                last_err = e
                continue
    st.error(f"⚠️ Error al conectar con Gemini: {last_err}")
    return None

# Multi-speaker dual-voice neural audio generator (ElevenLabs API v1.x+)
def synthesize_dual_voice_podcast(script_text: str, api_token: str) -> bytes:
    from elevenlabs.client import ElevenLabs
    client_tts = ElevenLabs(api_key=api_token)
    
    VOICE_HOST_A = "nPczCjzI2devNBz1zQrb"  # Brian
    VOICE_HOST_B = "Xb7hH8MSUJpSbSDYk0k2"  # Alice

    lines = script_text.strip().split("\n")
    combined_audio = io.BytesIO()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        speaker = None
        utterance = ""
        
        if line.startswith("**Host A:**") or line.startswith("Host A:"):
            speaker = VOICE_HOST_A
            utterance = re.sub(r"^\*{0,2}Host A:\*{0,2}\s*", "", line)
        elif line.startswith("**Host B:**") or line.startswith("Host B:"):
            speaker = VOICE_HOST_B
            utterance = re.sub(r"^\*{0,2}Host B:\*{0,2}\s*", "", line)
        else:
            utterance = line
            speaker = VOICE_HOST_A

        if utterance.strip():
            try:
                audio_stream = client_tts.text_to_speech.convert(
                    voice_id=speaker,
                    text=utterance.strip(),
                    model_id="eleven_turbo_v2_5"
                )
            except AttributeError:
                audio_stream = client_tts.generate(
                    text=utterance.strip(),
                    voice=speaker,
                    model="eleven_turbo_v2_5"
                )

            for chunk in audio_stream:
                combined_audio.write(chunk)

    combined_audio.seek(0)
    return combined_audio.read()

# Reproductor interactivo con controles de salto +-10s
def render_podcast_player(audio_bytes: bytes, title: str = "Executive Briefing"):
    b64_audio = base64.b64encode(audio_bytes).decode()
    player_html = f"""
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 16px 20px; margin: 12px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <span style="font-weight: 700; font-size: 0.9rem; color: #0f172a;">🎧 {title}</span>
            <span id="audio-time" style="font-size: 0.8rem; font-family: monospace; color: #64748b; font-weight: 600;">00:00 / 00:00</span>
        </div>
        
        <audio id="neam-audio" src="data:audio/mp3;base64,{b64_audio}" preload="metadata"></audio>
        
        <input type="range" id="seek-bar" value="0" min="0" max="100" style="width: 100%; accent-color: #059669; cursor: pointer; margin-bottom: 12px;">

        <div style="display: flex; justify-content: center; align-items: center; gap: 14px;">
            <button onclick="skipTime(-10)" style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 6px 14px; font-weight: 700; color: #1e293b; cursor: pointer; font-size: 0.82rem;">
                ⏪ -10s
            </button>
            <button id="play-pause-btn" onclick="togglePlay()" style="background: #1e40af; border: none; border-radius: 50%; width: 42px; height: 42px; color: #ffffff; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(30,64,175,0.25);">
                ▶
            </button>
            <button onclick="skipTime(10)" style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 6px 14px; font-weight: 700; color: #1e293b; cursor: pointer; font-size: 0.82rem;">
                +10s ⏩
            </button>
        </div>
    </div>

    <script>
        const audio = document.getElementById('neam-audio');
        const playBtn = document.getElementById('play-pause-btn');
        const seekBar = document.getElementById('seek-bar');
        const timeDisplay = document.getElementById('audio-time');

        function formatTime(seconds) {{
            const mins = Math.floor(seconds / 60) || 0;
            const secs = Math.floor(seconds % 60) || 0;
            return `${{mins < 10 ? '0' : ''}}${{mins}}:${{secs < 10 ? '0' : ''}}${{secs}}`;
        }}

        function togglePlay() {{
            if (audio.paused) {{
                audio.play();
                playBtn.innerHTML = '⏸';
                playBtn.style.background = '#059669';
            }} else {{
                audio.pause();
                playBtn.innerHTML = '▶';
                playBtn.style.background = '#1e40af';
            }}
        }}

        function skipTime(seconds) {{
            audio.currentTime = Math.min(Math.max(audio.currentTime + seconds, 0), audio.duration);
        }}

        audio.addEventListener('loadedmetadata', () => {{
            timeDisplay.innerText = `00:00 / ${{formatTime(audio.duration)}}`;
        }});

        audio.addEventListener('timeupdate', () => {{
            const progress = (audio.currentTime / audio.duration) * 100 || 0;
            seekBar.value = progress;
            timeDisplay.innerText = `${{formatTime(audio.currentTime)}} / ${{formatTime(audio.duration)}}`;
        }});

        seekBar.addEventListener('input', () => {{
            audio.currentTime = (seekBar.value / 100) * audio.duration;
        }});

        audio.addEventListener('ended', () => {{
            playBtn.innerHTML = '▶';
            playBtn.style.background = '#1e40af';
            seekBar.value = 0;
        }});
    </script>
    """
    components.html(player_html, height=140)

# ---------------------------------------------------------
# GLOBAL STATE & CURRICULUM ARCHITECTURE
# ---------------------------------------------------------
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Lucas",
        "industry": "Creative Direction / Retail Management",
        "passions": "Cinema Production, Industrial Design, Mid-Century Architecture",
        "working_memory_limit": 140,
        "stance": "Adversarial Boardroom Critic"
    }

if "curriculum_modules" not in st.session_state:
    st.session_state.curriculum_modules = {
        "mod_1": {
            "title": "Module 1: Evolution of Human Resource Management",
            "tag": "HR MANAGEMENT (MBA)",
            "submodule": "Evolution of Strategic Human Capital",
            "instructions": (
                "Looking into the literature, you will notice an evolution of terms describing Human Resource "
                "Management in organizations, starting as Labor Management, via HR Administration and evolving "
                "into People Management. Analyze the different definitions to discern the mindset of executive "
                "leaders. How has it developed over the years in response to organizational friction and agility?"
            ),
            "exercise": (
                "Formulate a 3-part strategic positioning argument defending why People Management must act as "
                "an adaptive scaffold rather than a rigid compliance function in high-divergence creative industries."
            ),
            "resources": [
                {
                    "id": "res_1",
                    "title": "Lengnick-Hall: The Evolution of Strategic HRM",
                    "type": "Literature (Core Paper)",
                    "content": "The transition from personnel administration to strategic capital involves scaffolding organizational capabilities rather than enforcing static compliance."
                },
                {
                    "id": "res_2",
                    "title": "Vaupel & Meyer: Strategic Management & Vision Framework",
                    "type": "Slides / Academic Lecture",
                    "content": "Strategic positioning requires synchronizing cognitive agility, defensible value architectures, and executive empathy across cross-functional leadership teams."
                },
                {
                    "id": "res_3",
                    "title": "Boon & Eckardt: Integrating Strategic Human Capital",
                    "type": "Literature (Advanced Reading)",
                    "content": "Micro-foundations of human capital suggest individual variance and neurodivergent divergence constitute non-linear drivers of sustained innovation."
                }
            ]
        }
    }

if "active_module_id" not in st.session_state:
    st.session_state.active_module_id = "mod_1"

if "completed_resources" not in st.session_state:
    st.session_state.completed_resources = set()

if "exercise_submitted" not in st.session_state:
    st.session_state.exercise_submitted = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "faculty_grades" not in st.session_state:
    st.session_state.faculty_grades = {}

active_mod = st.session_state.curriculum_modules[st.session_state.active_module_id]

if "active_reading" not in st.session_state:
    st.session_state.active_reading = active_mod["resources"][0]

# ---------------------------------------------------------
# VIEW 1: LANDING PAGE (ROLE SELECTION)
# ---------------------------------------------------------
if st.session_state.current_role is None:
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 4px 12px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.05em;">
            Steinbeis University • Berlin School of Creative Leadership
        </span>
        <h1 style="font-size: 2.4rem; font-weight: 800; color: #0f172a; margin-top: 12px; letter-spacing: -0.03em;">
            NEAM Executive Academic Portal
        </h1>
        <p style="font-size: 1.05rem; color: #64748b; max-width: 650px; margin: 0 auto;">
            Closed-loop cognitive scaffolding and verified Socratic assessment gateway. Select your institutional role to enter.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="role-card">
            <div class="role-icon">🏛️</div>
            <div class="role-title">University Admin</div>
            <div class="role-desc">Upload core curriculum modules, literature PDFs, and configure Socratic task parameters.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter as University Admin", use_container_width=True):
            st.session_state.current_role = "admin"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="role-card">
            <div class="role-icon">👨‍🏫</div>
            <div class="role-title">Faculty Evaluator</div>
            <div class="role-desc">Review student defense ledgers, anti-ghostwriting proof dossiers, and grade submissions.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter as Faculty (Dr. Vaupel)", use_container_width=True):
            st.session_state.current_role = "teacher"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="role-card">
            <div class="role-icon">🎓</div>
            <div class="role-title">Executive Student</div>
            <div class="role-desc">Engage in fast Socratic sparring, generate dual-voice neural podcasts, and evolve your warrior avatar.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter as Student (Lucas)", use_container_width=True):
            st.session_state.current_role = "student"
            st.rerun()

# ---------------------------------------------------------
# VIEW 2: UNIVERSITY ADMIN ENVIRONMENT
# ---------------------------------------------------------
elif st.session_state.current_role == "admin":
    st.markdown("""
    <div class="portal-banner">
        <div>
            <div class="portal-brand">🏛️ University Curriculum Administration</div>
            <div class="portal-sub">Berlin School of Creative Leadership • Resource Repository Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Switch Institutional Role"):
        st.session_state.current_role = None
        st.rerun()

    st.markdown("### 📤 Upload & Configure Module Curriculum")
    st.caption("Materials uploaded here are immediately distributed to the Executive Student and Faculty review spaces.")

    with st.form("admin_module_creator"):
        c1, c2 = st.columns(2)
        with c1:
            mod_title = st.text_input("Module Name", value=active_mod["title"])
            mod_tag = st.text_input("Academic Tag", value=active_mod["tag"])
        with c2:
            mod_sub = st.text_input("Sub-Module Topic", value=active_mod["submodule"])
            mod_eval = st.text_input("Assigned Evaluator", value="Prof. Dr. Mario Vaupel")
        
        mod_inst = st.text_area("Faculty Instructions (Context)", value=active_mod["instructions"], height=100)
        mod_ex = st.text_area("Module Capstone Defense Task", value=active_mod["exercise"], height=100)

        st.markdown("#### 📚 Active Readings (3 Papers Required)")
        r1_title = st.text_input("Reading 1 Title", value=active_mod["resources"][0]["title"])
        r1_body = st.text_area("Reading 1 Key Excerpt / Core Thesis", value=active_mod["resources"][0]["content"])
        
        r2_title = st.text_input("Reading 2 Title", value=active_mod["resources"][1]["title"])
        r2_body = st.text_area("Reading 2 Key Excerpt / Core Thesis", value=active_mod["resources"][1]["content"])

        r3_title = st.text_input("Reading 3 Title", value=active_mod["resources"][2]["title"])
        r3_body = st.text_area("Reading 3 Key Excerpt / Core Thesis", value=active_mod["resources"][2]["content"])

        if st.form_submit_button("💾 Save & Publish Module to Portal", use_container_width=True):
            st.session_state.curriculum_modules["mod_1"] = {
                "title": mod_title,
                "tag": mod_tag,
                "submodule": mod_sub,
                "instructions": mod_inst,
                "exercise": mod_ex,
                "resources": [
                    {"id": "res_1", "title": r1_title, "type": "Literature (Core Paper)", "content": r1_body},
                    {"id": "res_2", "title": r2_title, "type": "Lecture Slides", "content": r2_body},
                    {"id": "res_3", "title": r3_title, "type": "Advanced Reading", "content": r3_body}
                ]
            }
            st.session_state.active_reading = st.session_state.curriculum_modules["mod_1"]["resources"][0]
            st.success("✅ Module updated successfully and propagated across the entire workspace!")

# ---------------------------------------------------------
# VIEW 3: TEACHER / FACULTY EVALUATOR ENVIRONMENT
# ---------------------------------------------------------
elif st.session_state.current_role == "teacher":
    st.markdown("""
    <div class="portal-banner">
        <div>
            <div class="portal-brand">👨‍🏫 Faculty Assessment Chamber | Prof. Dr. Mario Vaupel</div>
            <div class="portal-sub">Steinbeis NEXT • Anti-Ghostwriting & Socratic Proof-of-Work Verification</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Switch Institutional Role"):
        st.session_state.current_role = None
        st.rerun()

    st.markdown("### 📋 Student Submissions & Human Reasoning Audits")
    
    col_t1, col_t2 = st.columns([1, 1], gap="large")

    with col_t1:
        st.markdown("#### 🎓 Student Status: Lucas")
        st.markdown(f"""
        - **Domain:** {st.session_state.profile['industry']}
        - **Readings Mastered:** {len(st.session_state.completed_resources)}/3
        - **Task Status:** {'Submitted for Grading ✅' if st.session_state.exercise_submitted else 'In Progress ⏳'}
        - **Socratic Interaction Rounds:** {len(st.session_state.messages) // 2} rounds
        """)

        st.markdown("---")
        st.markdown("#### 📜 Proof-of-Work Socratic Reasoning Ledger")
        st.caption("Verifies human dialectical thinking vs generative ghostwriting.")

        if st.session_state.messages:
            for idx, msg in enumerate(st.session_state.messages):
                actor = "Student (Lucas)" if msg["role"] == "user" else "Socratic Sparring AI"
                with st.expander(f"Interaction #{idx + 1} | {actor}"):
                    st.write(msg["content"])
        else:
            st.info("No Socratic sparring interactions recorded for this student yet.")

    with col_t2:
        st.markdown("#### 📝 Faculty Assessment & Grading")
        if not st.session_state.exercise_submitted:
            st.warning("⏳ The student has not submitted the final capstone defense yet.")
        else:
            st.success("🎯 Capstone defense submitted by Lucas!")
            grade = st.selectbox("Qualitative Assessment Grade", ["Distinction (1.0 - 1.3)", "Merit (1.7 - 2.0)", "Pass (2.3 - 3.0)", "Revise & Resubmit"])
            feedback = st.text_area("Faculty Socratic Critique & Feedback", placeholder="Assess the integration of non-linear scaffolding and theoretical defensibility...")
            
            if st.button("Publish Faculty Evaluation & Record to Dossier", use_container_width=True):
                st.session_state.faculty_grades["Lucas"] = {"grade": grade, "feedback": feedback, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                st.success("✅ Evaluation recorded and stored in student record!")

        if "Lucas" in st.session_state.faculty_grades:
            fg = st.session_state.faculty_grades["Lucas"]
            st.info(f"**Recorded Grade:** {fg['grade']}\n\n**Feedback:** {fg['feedback']}\n\n*Logged on: {fg['date']}*")

# ---------------------------------------------------------
# VIEW 4: STUDENT ENVIRONMENT (TWO-COLUMN WORKSPACE)
# ---------------------------------------------------------
elif st.session_state.current_role == "student":
    st.markdown(f"""
    <div class="portal-banner">
        <div>
            <div class="portal-brand">🎓 Steinbeis NEXT | Executive Workspace</div>
            <div class="portal-sub">{active_mod['tag']} • {active_mod['submodule']}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 0.85rem; font-weight: 600; color: #047857; background: #ecfdf5; padding: 6px 12px; border-radius: 20px; border: 1px solid #a7f3d0;">
                ● Evaluator: Prof. Dr. Mario Vaupel Active
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_nav, _ = st.columns([1, 4])
    with col_nav:
        if st.button("← Switch Institutional Role"):
            st.session_state.current_role = None
            st.rerun()

    # Gamification Avatar HUD
    num_completed = len(st.session_state.completed_resources)
    exercise_done = st.session_state.exercise_submitted

    if exercise_done:
        warrior_icon = "👑"
        warrior_title = "Grand Executive Strategist"
        stage_desc = "Mastery Level Reached. Socratic thesis defended and sent to Prof. Dr. Mario Vaupel."
    elif num_completed == 3:
        warrior_icon = "⚔️"
        warrior_title = "Socratic Champion"
        stage_desc = "Fully Armed with Helmet, Shield & Blade. Ready for Final Boardroom Defense."
    elif num_completed == 2:
        warrior_icon = "🛡️"
        warrior_title = "Defensive Strategist"
        stage_desc = "Shield of Defensibility unlocked. 1 theoretical reading remaining."
    elif num_completed == 1:
        warrior_icon = "🪖"
        warrior_title = "Theoretical Scout"
        stage_desc = "Helmet of Vision unlocked. Groundwork established."
    else:
        warrior_icon = "🥋"
        warrior_title = "Academic Initiate"
        stage_desc = "Base scaffolding. Complete readings or listen to audio to forge your armor."

    badge_helmet = "gear-unlocked" if num_completed >= 1 else "gear-locked"
    badge_shield = "gear-unlocked" if num_completed >= 2 else "gear-locked"
    badge_sword = "gear-unlocked" if num_completed >= 3 else "gear-locked"
    badge_crown = "gear-unlocked" if exercise_done else "gear-locked"

    st.markdown(f"""
    <div class="warrior-card">
        <div class="warrior-avatar">{warrior_icon}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1rem; color: #0f172a;">Student Avatar: {st.session_state.profile['name']} — <span style="color: #047857;">{warrior_title}</span></span>
                <span style="font-size: 0.8rem; font-weight: 600; color: #64748b;">Progress: {num_completed}/3 Readings • Task: {'Completed ✅' if exercise_done else 'Pending ⏳'}</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">{stage_desc}</div>
            <div class="gear-badges">
                <span class="gear-badge {badge_helmet}">🪖 Reading A (Helmet)</span>
                <span class="gear-badge {badge_shield}">🛡️ Reading B (Shield)</span>
                <span class="gear-badge {badge_sword}">⚔️ Reading C (Blade)</span>
                <span class="gear-badge {badge_crown}">👑 Final Defense (Crown)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Main Two-Column Layout
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='instruction-label'>Module Instructions</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='instruction-text'>{active_mod['instructions']}</div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("<div class='instruction-label'>Curriculum Resources (Select & Transform)</div>", unsafe_allow_html=True)

        for res in active_mod["resources"]:
            is_done = res["id"] in st.session_state.completed_resources
            icon_status = "✅" if is_done else "📄"
            
            with st.container():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{icon_status} {res['title']}**")
                    st.caption(f"{res['type']} • Status: {'Completed' if is_done else 'Pending'}")
                with c2:
                    if st.button("Focus 🎯", key=f"focus_{res['id']}", use_container_width=True):
                        st.session_state.active_reading = res
                        st.rerun()

        st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        curr_r = st.session_state.active_reading
        st.markdown(f"**Focused Material:** `{curr_r['title']}`")

        t_read, t_audio, t_slides = st.tabs(["📖 Read Summary", "🎙️ Neural Audio (±10s)", "📊 Slide Deck"])

        with t_read:
            st.info(curr_r["content"])
            if st.button(f"Mark '{curr_r['title']}' as Read (+Equip Warrior)", use_container_width=True):
                st.session_state.completed_resources.add(curr_r["id"])
                st.toast("⚔️ Gear equipped! Armor upgraded.", icon="🛡️")
                st.rerun()

        with t_audio:
            st.caption("Generate a broadcast-quality dual-voice discussion between Host A & Host B grounded in this paper.")
            if st.button("Synthesize Neural Podcast", key="gen_pod_btn", use_container_width=True):
                prof = st.session_state.profile
                script_prompt = f"""
Executive brief script between Host A (inquiring professor) and Host B (pragmatic strategist).
Material: {curr_r['content']}
Executive: {prof['name']} ({prof['industry']}) | Metaphors: {prof['passions']}
Address {prof['name']} directly twice. Keep concise (approx 200 words).
Format strictly alternating:
Host A: ...
Host B: ...
"""
                with st.spinner("Synthesizing script and rendering neural audio..."):
                    script = generate_studio_text(script_prompt)
                    st.session_state.active_script = script
                    if script and elevenlabs_key:
                        audio_b = synthesize_dual_voice_podcast(script, elevenlabs_key)
                        st.session_state.active_audio = audio_b
                        st.session_state.completed_resources.add(curr_r["id"])
                        st.toast("🎙️ Podcast finished! Warrior weapon equipped.", icon="⚔️")
                    elif not elevenlabs_key:
                        st.warning("Please configure ELEVENLABS_API_KEY in Secrets for multi-speaker neural audio.")

            if "active_audio" in st.session_state and st.session_state.active_audio:
                render_podcast_player(st.session_state.active_audio, title=curr_r['title'])
                st.download_button(
                    label="📥 Download Episode (.mp3)",
                    data=st.session_state.active_audio,
                    file_name=f"Podcast_{curr_r['id']}.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )

            if "active_script" in st.session_state and st.session_state.active_script:
                with st.expander("View Full Dialogue Transcript"):
                    st.text(st.session_state.active_script)

        with t_slides:
            st.caption("Visual strategy blueprint for executive synthesis.")
            if st.button("Generate 3-Slide Architecture", use_container_width=True):
                deck_prompt = f"Create a 3-slide visual architecture grounded in: {curr_r['content']} for {st.session_state.profile['name']}"
                with st.spinner("Drafting deck architecture..."):
                    deck = generate_studio_text(deck_prompt)
                    if deck:
                        st.markdown(deck)

    with col_right:
        st.markdown("<div class='instruction-label'>Module Exercise & Defense Task</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
            <span style="font-weight: 700; color: #1e40af; font-size: 0.88rem;">🎯 Academic Milestone Objective:</span>
            <div style="font-size: 0.88rem; color: #1e3a8a; margin-top: 4px; line-height: 1.45;">{active_mod['exercise']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='instruction-label'>Socratic Sparring Partner (Defense Chamber)</div>", unsafe_allow_html=True)
        st.caption(f"Adversarial sparring grounded in Steinbeis curriculum. Limit: <{st.session_state.profile['working_memory_limit']} words.")

        chat_container = st.container(height=360)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        sparring_input = st.chat_input("Defend your thesis or question assumptions...")

        if sparring_input:
            prof = st.session_state.profile
            st.session_state.messages.append({"role": "user", "content": sparring_input})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(sparring_input)

                socratic_system = f"""
You are the Socratic sparring partner inside NEAM for executive {prof['name']}.
Evaluator: Prof. Dr. Mario Vaupel.
MATERIAL: {st.session_state.active_reading['content']}
EXERCISE: {active_mod['exercise']}

RULES:
1. Anti-Ghostwriting: Challenge assumptions, do not write the student's assignment.
2. Max words: <{prof['working_memory_limit']}.
3. Metaphors: {prof['passions']} and {prof['industry']}.
4. Stance: {prof['stance']}. Incisive, intellectual, direct.
"""
                with st.chat_message("assistant"):
                    reply_stream = stream_socratic_response(f"Student: {sparring_input}", socratic_system)
                    reply = st.write_stream(reply_stream)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("🏆 Submit Final Exercise Defense to Faculty", use_container_width=True):
            if len(st.session_state.messages) < 2:
                st.warning("⚠️ You must engage in at least one round of Socratic defense before final submission.")
            else:
                st.session_state.exercise_submitted = True
                st.balloons()
                st.success("🎉 Exercise Successfully Defended & Submitted! Crown of Executive Mastery Awarded.")
                st.rerun()

    # Footer Audit Log
    st.markdown("<hr style='margin: 2.5rem 0 1rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        st.caption("NEAM • Neurodivergent Executive AI Module • Steinbeis University / Berlin School of Creative Leadership")
    with col_f2:
        audit_data = f"# NEAM Academic Audit Log\nStudent: {st.session_state.profile['name']}\nCompleted Resources: {len(st.session_state.completed_resources)}/3\nSubmitted: {st.session_state.exercise_submitted}\nDate: {datetime.datetime.now().isoformat()}"
        st.download_button(
            "📥 Export Proof-of-Work Audit Dossier",
            data=audit_data,
            file_name=f"NEAM_Audit_{st.session_state.profile['name']}.md",
            mime="text/markdown",
            use_container_width=True
        )
