import streamlit as st
import datetime
import os
import io
import re
import base64
import requests
import streamlit.components.v1 as components
from google import genai
from google.genai import types

# ---------------------------------------------------------
# PAGE CONFIGURATION & THEME
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
    st.error("⚠️ GEMINI_API_KEY missing in Streamlit Secrets.")
    st.stop()

elevenlabs_key = st.secrets.get("ELEVENLABS_API_KEY", None)
PRIMARY_MODEL = "gemini-2.5-flash"

def call_gemini_api(prompt_text: str, system_instr: str = "", stream: bool = False):
    """
    Robust caller handling standard keys and AI Studio Auth Keys (AQ...)
    via REST fallback if SDK client raises protocol blocks.
    """
    key = api_keys[0]
    
    # 1. Try SDK Client
    try:
        client = genai.Client(api_key=key)
        cfg = types.GenerateContentConfig(
            system_instruction=system_instr if system_instr else None,
            temperature=0.6,
            max_output_tokens=300
        )
        if stream:
            return client.models.generate_content_stream(
                model=PRIMARY_MODEL,
                contents=[prompt_text],
                config=cfg
            )
        resp = client.models.generate_content(
            model=PRIMARY_MODEL,
            contents=[prompt_text],
            config=cfg
        )
        return resp.text
    except Exception:
        pass

    # 2. Direct HTTP Fallback supporting x-goog-api-key header
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{PRIMARY_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": key
    }
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 300}
    }
    if system_instr:
        payload["systemInstruction"] = {"parts": [{"text": system_instr}]}

    res = requests.post(url, headers=headers, json=payload, timeout=20)
    if res.status_code == 200:
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise RuntimeError(f"HTTP {res.status_code}: {res.text}")

def stream_socratic_response(prompt_text: str, system_instr: str):
    try:
        stream_obj = call_gemini_api(prompt_text, system_instr, stream=True)
        if hasattr(stream_obj, "__iter__") and not isinstance(stream_obj, str):
            for chunk in stream_obj:
                if chunk.text:
                    yield chunk.text
            return
        yield str(stream_obj)
    except Exception:
        # Fallback to single-call text generator
        try:
            full_txt = call_gemini_api(prompt_text, system_instr, stream=False)
            yield full_txt
        except Exception as e:
            yield f"⚠️ API Error: {e}"

def generate_studio_text(prompt_text: str):
    try:
        return call_gemini_api(prompt_text, stream=False)
    except Exception as e:
        st.error(f"⚠️ Error: {e}")
        return None

def synthesize_dual_voice_podcast(script_text: str, api_token: str) -> bytes:
    from elevenlabs.client import ElevenLabs
    client_tts = ElevenLabs(api_key=api_token)
    
    VOICE_HOST_A = "nPczCjzI2devNBz1zQrb"
    VOICE_HOST_B = "Xb7hH8MSUJpSbSDYk0k2"

    lines = script_text.strip().split("\n")
    combined_audio = io.BytesIO()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
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

def render_podcast_player(audio_bytes: bytes, title: str = "Executive Briefing"):
    b64_audio = base64.b64encode(audio_bytes).decode()
    player_html = f"""
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 16px 20px; margin: 12px 0;">
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
            <button id="play-pause-btn" onclick="togglePlay()" style="background: #1e40af; border: none; border-radius: 50%; width: 42px; height: 42px; color: #ffffff; font-size: 1rem; cursor: pointer; display: flex; align-items: center; justify-content: center;">
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

        function formatTime(sec) {{
            const m = Math.floor(sec / 60) || 0;
            const s = Math.floor(sec % 60) || 0;
            return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
        }}
        function togglePlay() {{
            if (audio.paused) {{ audio.play(); playBtn.innerHTML = '⏸'; }}
            else {{ audio.pause(); playBtn.innerHTML = '▶'; }}
        }}
        function skipTime(s) {{
            audio.currentTime = Math.min(Math.max(audio.currentTime + s, 0), audio.duration);
        }}
        audio.addEventListener('loadedmetadata', () => {{
            timeDisplay.innerText = '00:00 / ' + formatTime(audio.duration);
        }});
        audio.addEventListener('timeupdate', () => {{
            seekBar.value = (audio.currentTime / audio.duration) * 100 || 0;
            timeDisplay.innerText = formatTime(audio.currentTime) + ' / ' + formatTime(audio.duration);
        }});
        seekBar.addEventListener('input', () => {{
            audio.currentTime = (seekBar.value / 100) * audio.duration;
        }});
        audio.addEventListener('ended', () => {{
            playBtn.innerHTML = '▶';
            seekBar.value = 0;
        }});
    </script>
    """
    components.html(player_html, height=140)

# ---------------------------------------------------------
# GLOBAL STATE & INITIALIZATION
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
# VIEW ROUTING
# ---------------------------------------------------------
if st.session_state.current_role is None:
    st.markdown("""
    <div style="text-align: center; margin: 3rem 0 2rem 0;">
        <span style="font-size: 0.85rem; font-weight: 700; color: #1e40af; background: #dbeafe; padding: 4px 12px; border-radius: 20px;">
            Steinbeis University • Berlin School of Creative Leadership
        </span>
        <h1 style="font-size: 2.4rem; font-weight: 800; color: #0f172a; margin-top: 12px;">
            NEAM Executive Academic Portal
        </h1>
        <p style="font-size: 1.05rem; color: #64748b; max-width: 650px; margin: 0 auto;">
            Closed-loop cognitive scaffolding and verified Socratic assessment gateway.
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
        r1_body = st.text_area("Reading 1 Key Excerpt", value=active_mod["resources"][0]["content"])
        
        r2_title = st.text_input("Reading 2 Title", value=active_mod["resources"][1]["title"])
        r2_body = st.text_area("Reading 2 Key Excerpt", value=active_mod["resources"][1]["content"])

        r3_title = st.text_input("Reading 3 Title", value=active_mod["resources"][2]["title"])
        r3_body = st.text_area("Reading 3 Key Excerpt", value=active_mod["resources"][2]["content"])

        if st.form_submit_button("💾 Save & Publish Module", use_container_width=True):
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
            st.success("✅ Module updated successfully!")

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
            feedback = st.text_area("Faculty Socratic Critique & Feedback")
            if st.button("Publish Evaluation", use_container_width=True):
                st.session_state.faculty_grades["Lucas"] = {"grade": grade, "feedback": feedback, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
                st.success("✅ Evaluation recorded!")

elif st.session_state.current_role == "student":
    st.markdown(f"""
    <div class="portal-banner">
        <div>
            <div class="portal-brand">🎓 Steinbeis NEXT | Executive Workspace</div>
            <div class="portal-sub">{active_mod['tag']} • {active_mod['submodule']}</div>
        </div>
        <div>
            <span style="font-size: 0.85rem; font-weight: 600; color: #047857; background: #ecfdf5; padding: 6px 12px; border-radius: 20px;">
                ● Evaluator: Prof. Dr. Mario Vaupel Active
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Switch Institutional Role"):
        st.session_state.current_role = None
        st.rerun()

    num_completed = len(st.session_state.completed_resources)
    exercise_done = st.session_state.exercise_submitted

    if exercise_done:
        warrior_icon = "👑"
        warrior_title = "Grand Executive Strategist"
        stage_desc = "Mastery Level Reached. Thesis submitted."
    elif num_completed == 3:
        warrior_icon = "⚔️"
        warrior_title = "Socratic Champion"
        stage_desc = "Fully Armed. Ready for Final Defense."
    elif num_completed == 2:
        warrior_icon = "🛡️"
        warrior_title = "Defensive Strategist"
        stage_desc = "Shield unlocked. 1 reading remaining."
    elif num_completed == 1:
        warrior_icon = "🪖"
        warrior_title = "Theoretical Scout"
        stage_desc = "Helmet unlocked."
    else:
        warrior_icon = "🥋"
        warrior_title = "Academic Initiate"
        stage_desc = "Base scaffolding."

    b_h = "gear-unlocked" if num_completed >= 1 else "gear-locked"
    b_s = "gear-unlocked" if num_completed >= 2 else "gear-locked"
    b_w = "gear-unlocked" if num_completed >= 3 else "gear-locked"
    b_c = "gear-unlocked" if exercise_done else "gear-locked"

    st.markdown(f"""
    <div class="warrior-card">
        <div class="warrior-avatar">{warrior_icon}</div>
        <div style="flex-grow: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 700; font-size: 1rem; color: #0f172a;">Student Avatar: {st.session_state.profile['name']} — <span style="color: #047857;">{warrior_title}</span></span>
                <span style="font-size: 0.8rem; font-weight: 600; color: #64748b;">Progress: {num_completed}/3 Readings</span>
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">{stage_desc}</div>
            <div class="gear-badges">
                <span class="gear-badge {b_h}">🪖 Reading A (Helmet)</span>
                <span class="gear-badge {b_s}">🛡️ Reading B (Shield)</span>
                <span class="gear-badge {b_w}">⚔️ Reading C (Blade)</span>
                <span class="gear-badge {b_c}">👑 Final Defense (Crown)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<div class='instruction-label'>Module Instructions</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='instruction-text'>{active_mod['instructions']}</div>", unsafe_allow_html=True)

        st.markdown("<div class='instruction-label'>Curriculum Resources</div>", unsafe_allow_html=True)
        for res in active_mod["resources"]:
            is_done = res["id"] in st.session_state.completed_resources
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**{'✅' if is_done else '📄'} {res['title']}**")
            with c2:
                if st.button("Focus 🎯", key=f"f_{res['id']}", use_container_width=True):
                    st.session_state.active_reading = res
                    st.rerun()

        curr_r = st.session_state.active_reading
        st.markdown(f"**Selected:** `{curr_r['title']}`")

        t_read, t_audio = st.tabs(["📖 Summary", "🎙️ Neural Audio"])
        with t_read:
            st.info(curr_r["content"])
            if st.button(f"Mark Read (+Equip Gear)", use_container_width=True):
                st.session_state.completed_resources.add(curr_r["id"])
                st.rerun()

        with t_audio:
            if st.button("Synthesize Neural Podcast", use_container_width=True):
                prof = st.session_state.profile
                p_text = f"Host A and Host B discuss {curr_r['content']} for executive {prof['name']} ({prof['industry']}). Alternating Host A: / Host B: lines. Approx 150 words."
                script = generate_studio_text(p_text)
                if script and elevenlabs_key:
                    audio_b = synthesize_dual_voice_podcast(script, elevenlabs_key)
                    st.session_state.active_audio = audio_b
                    st.session_state.completed_resources.add(curr_r["id"])
                    st.rerun()

            if "active_audio" in st.session_state and st.session_state.active_audio:
                render_podcast_player(st.session_state.active_audio, title=curr_r['title'])

    with col_right:
        st.markdown("<div class='instruction-label'>Module Defense Task</div>", unsafe_allow_html=True)
        st.info(active_mod['exercise'])

        st.markdown("<div class='instruction-label'>Socratic Sparring Partner</div>", unsafe_allow_html=True)
        chat_box = st.container(height=340)
        with chat_box:
            for m in st.session_state.messages:
                with st.chat_message(m["role"]):
                    st.markdown(m["content"])

        prompt = st.chat_input("Defend your thesis...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_box:
                with st.chat_message("user"):
                    st.markdown(prompt)
                sys_inst = f"Socratic partner inside NEAM. Challenge assumptions for student {st.session_state.profile['name']}. Under 100 words."
                with st.chat_message("assistant"):
                    reply = st.write_stream(stream_socratic_response(prompt, sys_inst))
                    st.session_state.messages.append({"role": "assistant", "content": reply})

        if st.button("🏆 Submit Final Defense to Faculty", use_container_width=True):
            if len(st.session_state.messages) < 2:
                st.warning("Engage in Socratic sparring first.")
            else:
                st.session_state.exercise_submitted = True
                st.balloons()
                st.success("Submitted successfully!")
                st.rerun()
