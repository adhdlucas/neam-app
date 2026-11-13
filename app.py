import os
import io
import time
import json
import base64
from datetime import datetime
from typing import List, Dict, Tuple
import requests
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Clean Executive Light Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEAM | Executive Cognitive Scaffolding",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #0f172a;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    h1, h2, h3, h4, p, label, .stMarkdown {
        color: #0f172a;
    }
    .role-card {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 32px 24px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04);
    }
    .role-card:hover {
        border-color: #0284c7;
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.1);
    }
    .badge-blue {
        display: inline-block;
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .badge-green {
        display: inline-block;
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .workspace-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #0284c7;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }
    .workspace-box-green {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #059669;
        border-radius: 10px;
        padding: 18px 20px;
        margin-bottom: 14px;
    }
    .thermo-wrap {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 16px;
    }
    .thermo-track {
        width: 100%;
        height: 14px;
        background-color: #e2e8f0;
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 6px;
    }
    .slide-card {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #0284c7;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    div[data-testid="stChatInput"] {
        border-color: #cbd5e1 !important;
        background-color: #ffffff !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #0284c7 !important;
        box-shadow: 0 0 0 1px #0284c7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# High-Throughput API Configuration & Free-Tier ElevenLabs Voices
# ---------------------------------------------------------
BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"
ACTIVE_MODELS = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.6-flash",
    "models/gemini-4-argon",
    "models/gemini-3.8-flash",
]
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# Default ElevenLabs Premade Voices (Allowed on Free Tier API)
VOICE_HOST_A = "EXAVITQu4vr4xnSDxMaL"  # Sarah (Default Premade)
VOICE_HOST_B = "JBFqnCBsd6RMkjVDRZzb"  # George (Default Premade)

# ---------------------------------------------------------
# Session State & Closed-Loop Course Data Model
# ---------------------------------------------------------
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "name": "Lucas Giraldo Mejía",
        "program": "Executive MBA in Creative Leadership",
        "onboarded": False,
        "working_memory_chunking": True,
        "primary_modality": "Audio-First (Executive Podcast)",
        "task_initiation_scaffolding": True,
        "sparring_intensity": "Contrarian Devil's Advocate (Rigor)",
    }

if "selected_lesson_id" not in st.session_state:
    st.session_state.selected_lesson_id = None

if "course_data" not in st.session_state:
    st.session_state.course_data = {
        "course_name": "Strategic Alignment & Creative Leadership",
        "professor": "Prof. Dr. Mario Vaupel",
        "lessons": {
            "LES-01": {
                "title": "Lesson 1: Value Innovation & Blue Ocean Strategy",
                "summary": "Breaking the value-cost trade-off using the Strategy Canvas and the Four Actions Framework (ERRC Grid).",
                "task": (
                    "Identify one entrenched industry assumption in your executive domain. Using the Four Actions Framework "
                    "(Eliminate, Reduce, Raise, Create), formulate a strategic thesis explaining how eliminating that factor "
                    "lowers cost structure while unlocking uncontested buyer value."
                ),
                "materials": [
                    {
                        "id": "MAT-101",
                        "title": "Kim & Mauborgne — Value Innovation Core",
                        "type": "Core Reading",
                        "filename": "Blue_Ocean_Value_Innovation.txt",
                        "text": (
                            "Blue Ocean Strategy challenges companies to break out of red oceans of bloody competition "
                            "by creating uncontested market space that makes the competition irrelevant. Instead of choosing "
                            "between low cost and high differentiation, Value Innovation pursues both simultaneously."
                        ),
                    },
                    {
                        "id": "MAT-102",
                        "title": "The Four Actions Framework (ERRC Grid)",
                        "type": "Diagnostic Tool",
                        "filename": "ERRC_Framework_Guide.txt",
                        "text": (
                            "The Four Actions Framework asks four key questions to challenge an industry's strategic logic: "
                            "1) Which factors that the industry takes for granted should be Eliminated? "
                            "2) Which factors should be Reduced well below the industry standard? "
                            "3) Which factors should be Raised well above the industry standard? "
                            "4) Which factors should be Created that the industry has never offered?"
                        ),
                    },
                    {
                        "id": "MAT-103",
                        "title": "Executive Education Red Ocean Case",
                        "type": "Lecture Note",
                        "filename": "Executive_Education_Case.txt",
                        "text": (
                            "In executive education, traditional monomodal lecturing represents a high-overhead red ocean "
                            "that creates cognitive overload for neurodivergent leaders. Closed-loop multimodal scaffolding "
                            "eliminates passive friction while creating active dialectic proof-of-work."
                        ),
                    },
                ],
                "fallback_script": [
                    {"speaker": "Host_A", "text": "Most executives assume higher strategic rigor requires higher cost. Why does Value Innovation reject that?"},
                    {"speaker": "Host_B", "text": "Because competing on existing factors traps you in a red ocean. Eliminating low-value industry norms cuts cost while raising differentiation."},
                    {"speaker": "Host_A", "text": "So the ERRC Grid isn't just brainstorming—it's a structural filter."},
                    {"speaker": "Host_B", "text": "Exactly. By forcing simultaneous elimination and creation, you build a value curve competitors cannot imitate."}
                ],
            },
            "LES-02": {
                "title": "Lesson 2: Creating Shared Value (CSV) & Sustainable Leadership",
                "summary": "Reconnecting company success with social progress beyond traditional CSR philanthropy.",
                "task": (
                    "Contrast Corporate Social Responsibility (CSR) with Porter & Kramer's Creating Shared Value (CSV). "
                    "Propose one value-chain reconception in your organization that generates measurable economic profit "
                    "directly through solving a societal or environmental bottleneck."
                ),
                "materials": [
                    {
                        "id": "MAT-201",
                        "title": "Porter & Kramer — Shared Value Foundation",
                        "type": "Core Reading",
                        "filename": "Porter_Kramer_CSV.txt",
                        "text": (
                            "Creating Shared Value (CSV) focuses on policies and operating practices that enhance the competitiveness "
                            "of a company while simultaneously advancing the economic and social conditions in the communities in which "
                            "it operates. Unlike CSR, which is peripheral and driven by reputation, CSV is integral to profitability."
                        ),
                    },
                    {
                        "id": "MAT-202",
                        "title": "Three Pillars of Shared Value Execution",
                        "type": "Framework",
                        "filename": "Three_Pillars_CSV.txt",
                        "text": (
                            "Companies can create shared value in three distinct ways: 1) Reconceiving products and markets to meet "
                            "underserved societal needs; 2) Redefining productivity in the value chain (energy use, logistics, resource efficiency); "
                            "and 3) Enabling local cluster development around the company's operational hubs."
                        ),
                    },
                ],
                "fallback_script": [
                    {"speaker": "Host_A", "text": "Why do Porter and Kramer argue that traditional CSR fails to transform core business strategy?"},
                    {"speaker": "Host_B", "text": "Because CSR sits at the margin as a reputation cost center. Shared Value embeds societal impact directly into the profit engine."},
                    {"speaker": "Host_A", "text": "And that happens by reconceiving products, value chain productivity, or local clusters."},
                    {"speaker": "Host_B", "text": "Precisely. When social progress drives operational efficiency, sustainability becomes self-funding."}
                ],
            },
        },
    }

if "reviewed_materials" not in st.session_state:
    st.session_state.reviewed_materials = {}

if "micro_sprints" not in st.session_state:
    st.session_state.micro_sprints = {}

if "lesson_answers" not in st.session_state:
    st.session_state.lesson_answers = {}

if "lesson_sparring" not in st.session_state:
    st.session_state.lesson_sparring = {}

if "podcast_cache" not in st.session_state:
    st.session_state.podcast_cache = {}

if "slides_cache" not in st.session_state:
    st.session_state.slides_cache = {}

if "proof_of_work_log" not in st.session_state:
    st.session_state.proof_of_work_log = []

# ---------------------------------------------------------
# Sidebar: Engine Gateway & Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Gateway")
    GOOGLE_API_KEY = st.text_input(
        "Google AI Studio Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Your Tier 1 key (...djCg)",
    ).strip()
    ELEVENLABS_API_KEY = st.text_input(
        "ElevenLabs API Key",
        value=os.getenv("ELEVENLABS_API_KEY", ""),
        type="password",
    ).strip()

    if GOOGLE_API_KEY:
        st.caption(f"🟢 Primary LLM: `{ACTIVE_MODELS[0]}`")

    if st.session_state.current_role:
        st.divider()
        if st.session_state.current_role == "student" and st.session_state.selected_lesson_id:
            if st.button("← Back to Course Syllabus", use_container_width=True):
                st.session_state.selected_lesson_id = None
                st.rerun()
        if st.button("🏠 Switch Role (Landing)", use_container_width=True):
            st.session_state.current_role = None
            st.session_state.selected_lesson_id = None
            st.rerun()

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def compute_lesson_mastery(lesson_id: str, lesson: dict) -> Tuple[int, str]:
    total_mats = max(len(lesson.get("materials", [])), 1)
    reviewed_count = len(st.session_state.reviewed_materials.get(lesson_id, set()))
    mat_score = (reviewed_count / total_mats) * 50.0

    sprints = st.session_state.micro_sprints.get(lesson_id, [])
    if sprints:
        done_sprints = sum(1 for s in sprints if s.get("done"))
        sprint_score = (done_sprints / len(sprints)) * 20.0
    else:
        sprint_score = 0.0

    ans_data = st.session_state.lesson_answers.get(lesson_id, {})
    ans_score = 30.0 if ans_data.get("submitted") else (15.0 if len(ans_data.get("text", "").strip()) > 20 else 0.0)

    total = min(int(round(mat_score + sprint_score + ans_score)), 100)
    color = "#059669" if total == 100 else ("#0284c7" if total >= 50 else "#0ea5e9")
    return total, color


def cluster_lesson_materials(lesson: dict) -> str:
    blocks = []
    for idx, m in enumerate(lesson.get("materials", []), start=1):
        blocks.append(f"[Material {idx}: {m['title']} ({m['type']})]\n{m['text']}")
    return "\n\n".join(blocks)


def generate_micro_sprints_ai(task_text: str, clustered_text: str, api_key: str) -> List[Dict]:
    default_sprints = [
        {"step": "Sprint 1 (5 min): Extract the single core tension or assumption from the lesson materials.", "done": False},
        {"step": "Sprint 2 (10 min): Map 2 concrete strategic levers from the reading onto your thesis context.", "done": False},
        {"step": "Sprint 3 (10 min): Draft a sharp 3-sentence executive defense in the Lesson Answer Space.", "done": False},
    ]
    if not api_key:
        return default_sprints

    prompt = f"""
Break this MBA assignment task down into exactly 3 bite-sized, sequential 5-to-10 minute micro-sprints for an executive with ADHD.
Keep each step under 20 words. Return ONLY 3 lines formatted as:
1 | [Step 1]
2 | [Step 2]
3 | [Step 3]

Task: {task_text}
Context: {clustered_text[:1200]}
"""
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 250},
    }
    for model_path in ACTIVE_MODELS:
        try:
            resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                steps = []
                for line in raw.strip().splitlines():
                    if "|" in line:
                        _, desc = line.split("|", 1)
                        if desc.strip():
                            steps.append({"step": desc.strip(), "done": False})
                if len(steps) >= 2:
                    return steps[:3]
        except Exception:
            continue
    return default_sprints


def generate_visual_slides_ai(lesson: dict, clustered_text: str, api_key: str) -> List[Dict]:
    fallback_slides = [
        {
            "pillar": "CORE PREMISE",
            "title": lesson["title"],
            "takeaway": lesson["summary"],
            "bullets": [m["title"] for m in lesson.get("materials", [])],
            "question": "Which assumption in this lesson challenges your current leadership practice most?",
        }
    ]
    if not api_key:
        return fallback_slides

    prompt = f"""
Convert the clustered lesson materials below into 3 high-impact, scannable executive slides.
Return ONLY lines in this exact pipe-delimited format (one slide per line):
PILLAR | SLIDE TITLE | CORE TAKEAWAY | BULLET 1; BULLET 2 | SPARRING QUESTION

Materials:
{clustered_text[:2500]}
"""
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 500},
    }
    for model_path in ACTIVE_MODELS:
        try:
            resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                slides = []
                for line in raw.strip().splitlines():
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 5:
                        slides.append({
                            "pillar": parts[0],
                            "title": parts[1],
                            "takeaway": parts[2],
                            "bullets": [b.strip() for b in parts[3].split(";") if b.strip()],
                            "question": parts[4],
                        })
                if slides:
                    return slides
        except Exception:
            continue
    return fallback_slides


def call_socratic_sparring(
    prompt: str,
    history: list,
    lesson: dict,
    clustered_text: str,
    profile: dict,
    api_key: str,
) -> str:
    if not api_key:
        return "⚠️ Please enter your Google AI Studio Key in the sidebar to activate Socratic sparring."

    intensity = profile.get("sparring_intensity", "Contrarian Devil's Advocate (Rigor)")
    max_tokens = 320 if profile.get("working_memory_chunking") else 800

    system_instruction = f"""
You are NEAM, an executive Socratic sparring partner for Steinbeis University / Berlin School of Creative Leadership.
Candidate: {profile.get('name')} ({profile.get('program')}).
Active Lesson: {lesson['title']}
Lesson Assignment Task: {lesson['task']}

STRICT SAFEGUARDS:
1. CLOSED-LOOP GROUNDING: Base every argument strictly on the clustered lesson materials provided below.
2. ANTI-GHOSTWRITING: Never write the student's final answer or essay for them. Challenge weak assumptions, test logic against the lesson frameworks, and ask sharp dialectic questions.
3. COGNITIVE CALIBRATION: Tone = {intensity}. Keep replies concise (under 140 words) with clear bullet points or bold key concepts for executive scannability.

CLUSTERED LESSON MATERIALS:
\"\"\"{clustered_text}\"\"\"
"""
    contents = []
    for m in history:
        contents.append({"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.35, "maxOutputTokens": max_tokens},
        "systemInstruction": {"parts": [{"text": system_instruction}]},
    }

    for model_path in ACTIVE_MODELS:
        try:
            resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            elif resp.status_code in [503, 429, 500, 404]:
                continue
            else:
                return f"API Error ({resp.status_code}): {resp.text[:180]}"
        except Exception:
            continue

    return (
        "Socratic Pushback (Closed-Loop): Your argument touches the surface, but how does it hold up against the core framework "
        "in this lesson's uploaded readings? Identify the exact trade-off you are eliminating before finalizing your answer."
    )


def generate_podcast_audio(
    lesson: dict,
    clustered_text: str,
    gemini_key: str,
    eleven_key: str,
    progress_fn=None,
) -> Dict:
    if progress_fn:
        progress_fn("Clustering lesson materials & generating dialogue script...")

    script_prompt = f"""
Convert these clustered Steinbeis lesson materials into a punchy 4-line executive podcast dialogue between Host_A and Host_B.
Host_A poses the strategic dilemma. Host_B explains the theoretical insight from the materials.
Keep each line under 28 words. Output ONLY 4 lines in this exact format:
Host_A | [Line 1]
Host_B | [Line 2]
Host_A | [Line 3]
Host_B | [Line 4]

Materials:
{clustered_text[:2200]}
"""
    script = []
    if gemini_key:
        headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}
        payload = {
            "contents": [{"role": "user", "parts": [{"text": script_prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 350},
        }
        for model_path in ACTIVE_MODELS:
            try:
                resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=20)
                if resp.status_code == 200:
                    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = []
                    for line in raw.strip().splitlines():
                        if "|" in line:
                            spk, dlg = line.split("|", 1)
                            speaker = "Host_B" if "B" in spk else "Host_A"
                            clean = dlg.strip().strip('"').strip("*")
                            if clean:
                                parsed.append({"speaker": speaker, "text": clean})
                    if parsed:
                        script = parsed
                        break
            except Exception:
                continue

    if not script:
        script = lesson.get("fallback_script") or [
            {"speaker": "Host_A", "text": f"Let's unpack {lesson['title']}."},
            {"speaker": "Host_B", "text": lesson["summary"]},
        ]

    if not eleven_key:
        return {"bytes": None, "script": script, "warning": "No ElevenLabs key provided — using browser voice reader."}

    audio_buffer = io.BytesIO()
    for i, turn in enumerate(script):
        if progress_fn:
            progress_fn(f"Synthesizing voice turn {i + 1}/{len(script)} via ElevenLabs...")
        v_id = VOICE_HOST_A if turn["speaker"] == "Host_A" else VOICE_HOST_B
        try:
            tts_resp = requests.post(
                f"{ELEVENLABS_TTS_URL}/{v_id}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": eleven_key,
                },
                json={
                    "text": turn["text"],
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
                },
                timeout=25,
            )
            if tts_resp.status_code == 200:
                audio_buffer.write(tts_resp.content)
            else:
                return {
                    "bytes": None,
                    "script": script,
                    "warning": f"ElevenLabs returned {tts_resp.status_code}. Switched to instant browser audio.",
                }
        except Exception as e:
            return {"bytes": None, "script": script, "warning": f"ElevenLabs timeout ({e}). Switched to instant browser audio."}

    audio_buffer.seek(0)
    return {"bytes": audio_buffer.read(), "script": script, "warning": None}


# =========================================================
# 1. LANDING VIEW (STUDENT vs. PROFESSOR)
# =========================================================
if st.session_state.current_role is None:
    st.markdown("<h1 style='text-align: center; margin-top: 20px; color: #0f172a;'>NEAM</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #475569; font-size: 1.1rem; margin-bottom: 32px;'>"
        "Neurodivergent Executive AI Module & Closed-Loop Cognitive Scaffolding<br>"
        "<b>Steinbeis University Berlin • Berlin School of Creative Leadership</b>"
        "</p>",
        unsafe_allow_html=True,
    )

    _, col_s, col_p, _ = st.columns([1, 2.2, 2.2, 1], gap="large")

    with col_s:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge-blue">Executive Candidate</span>
                <div style="font-size: 3rem; margin: 8px 0;">🎓</div>
                <h2 style="margin-bottom: 8px;">Student</h2>
                <p style="color: #475569; font-size: 0.92rem;">
                    Autonomous cognitive calibration, multimodal course materials, micro-sprints, and Socratic sparring.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Enter as Student", use_container_width=True, type="primary"):
            st.session_state.current_role = "student"
            st.rerun()

    with col_p:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge-green">Faculty & Curriculum</span>
                <div style="font-size: 3rem; margin: 8px 0;">🏛️</div>
                <h2 style="margin-bottom: 8px;">Professor</h2>
                <p style="color: #475569; font-size: 0.92rem;">
                    Upload lesson materials, define strategic tasks, and audit student Proof-of-Work sparring logs.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        if st.button("Enter as Professor", use_container_width=True):
            st.session_state.current_role = "professor"
            st.rerun()


# =========================================================
# 2. STUDENT FLOW
# =========================================================
elif st.session_state.current_role == "student":
    profile = st.session_state.student_profile

    if not profile["onboarded"]:
        st.markdown("## 🧠 Autonomous Cognitive Calibration")
        st.info("First-time setup: Calibrate NEAM's executive scaffolding to your cognitive processing style before entering your course.")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                q_chunk = st.checkbox(
                    "Working Memory Chunking (Cap AI responses < 140 words)",
                    value=profile["working_memory_chunking"],
                )
                q_modality = st.selectbox(
                    "Preferred Sensory Ingestion Channel:",
                    ["Audio-First (Executive Podcast)", "Visual Slide Deck (Scannable)", "Raw Readings"],
                    index=0,
                )
            with c2:
                q_init = st.checkbox(
                    "Task Initiation Scaffolding (Enable 3-Step Bite-Sized Micro-Sprints)",
                    value=profile["task_initiation_scaffolding"],
                )
                q_tone = st.selectbox(
                    "Socratic Sparring Rigor:",
                    ["Contrarian Devil's Advocate (Rigor)", "Supportive Socratic Coach"],
                    index=0,
                )

            st.write("")
            if st.button("Save Calibration & Launch Course Workspace →", type="primary"):
                st.session_state.student_profile.update({
                    "onboarded": True,
                    "working_memory_chunking": q_chunk,
                    "primary_modality": q_modality,
                    "task_initiation_scaffolding": q_init,
                    "sparring_intensity": q_tone,
                })
                st.rerun()

    elif st.session_state.selected_lesson_id is None:
        h_avatar, h_info, h_cal = st.columns([0.7, 5, 1.5])
        with h_avatar:
            st.markdown(
                "<div style='width:56px;height:56px;border-radius:50%;background:#0284c7;color:white;"
                "display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:1.3rem;'>LG</div>",
                unsafe_allow_html=True,
            )
        with h_info:
            st.markdown(f"### {profile['name']}")
            st.caption(f"{profile['program']} • Calibration: **{profile['primary_modality']}**")
        with h_cal:
            if st.button("⚙️ Recalibrate", use_container_width=True):
                st.session_state.student_profile["onboarded"] = False
                st.rerun()

        st.divider()

        course = st.session_state.course_data
        st.markdown(f"<span class='badge-green'>Active MBA Course</span>", unsafe_allow_html=True)
        st.markdown(f"## {course['course_name']}")
        st.caption(f"Faculty Lead: **{course['professor']}** • Select a syllabus lesson below to launch its closed-loop workspace:")
        st.write("")

        for l_id, lesson in course["lessons"].items():
            pct, bar_color = compute_lesson_mastery(l_id, lesson)
            mat_count = len(lesson.get("materials", []))
            with st.container(border=True):
                c_title, c_prog, c_btn = st.columns([4, 2, 1.5])
                with c_title:
                    st.markdown(f"#### {lesson['title']}")
                    st.caption(f"{lesson['summary']} ({mat_count} uploaded materials)")
                with c_prog:
                    st.markdown(f"**Lesson Mastery: {pct}%**")
                    st.progress(pct / 100.0)
                with c_btn:
                    st.write("")
                    if st.button("Open Lesson →", key=f"open_{l_id}", type="primary", use_container_width=True):
                        st.session_state.selected_lesson_id = l_id
                        st.rerun()

    else:
        l_id = st.session_state.selected_lesson_id
        course = st.session_state.course_data
        lesson = course["lessons"][l_id]
        clustered_text = cluster_lesson_materials(lesson)

        if l_id not in st.session_state.reviewed_materials:
            st.session_state.reviewed_materials[l_id] = set()
        if l_id not in st.session_state.lesson_sparring:
            st.session_state.lesson_sparring[l_id] = [
                {
                    "role": "model",
                    "content": (
                        f"Closed-loop sparring locked to **{lesson['title']}** ({len(lesson['materials'])} clustered materials). "
                        "Test your thesis premise or ask me to challenge your draft before submitting."
                    ),
                }
            ]

        pct, thermo_color = compute_lesson_mastery(l_id, lesson)
        top_av, top_title, top_thermo = st.columns([0.6, 3.8, 2.6])
        with top_av:
            st.markdown(
                "<div style='width:50px;height:50px;border-radius:50%;background:#0284c7;color:white;"
                "display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:1.15rem;'>LG</div>",
                unsafe_allow_html=True,
            )
        with top_title:
            st.caption(course["course_name"].upper())
            st.markdown(f"### {lesson['title']}")
        with top_thermo:
            status_emoji = "🏆" if pct == 100 else "🌡️"
            st.markdown(
                f"""
                <div class="thermo-wrap">
                    <div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:700;">
                        <span>{status_emoji} Lesson Mastery Thermometer</span>
                        <span style="color:{thermo_color};">{pct}%</span>
                    </div>
                    <div class="thermo-track">
                        <div style="width:{pct}%; height:100%; background:{thermo_color}; transition: width 0.4s ease;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        rail_col, main_col = st.columns([1.35, 2.65], gap="large")

        with rail_col:
            st.markdown("#### 📂 Lesson Materials")
            st.caption("Click each uploaded item to review & boost mastery, or download:")

            materials = lesson.get("materials", [])
            for idx, mat in enumerate(materials):
                is_done = mat["id"] in st.session_state.reviewed_materials[l_id]
                icon = "✅" if is_done else "📄"
                with st.expander(f"{icon} {mat['title']}", expanded=(idx == 0 and not is_done)):
                    st.caption(f"Type: **{mat['type']}**")
                    st.write(mat["text"])
                    b1, b2 = st.columns(2)
                    with b1:
                        if not is_done:
                            if st.button("Mark Reviewed (+)", key=f"rev_{l_id}_{mat['id']}", use_container_width=True):
                                st.session_state.reviewed_materials[l_id].add(mat["id"])
                                st.rerun()
                        else:
                            st.success("Reviewed")
                    with b2:
                        st.download_button(
                            "⬇️ Download",
                            data=mat["text"].encode("utf-8"),
                            file_name=mat.get("filename", f"{mat['id']}.txt"),
                            mime="text/plain",
                            key=f"dl_{l_id}_{mat['id']}",
                            use_container_width=True,
                        )

            st.divider()
            st.markdown("#### 🔄 Transform Clustered Materials")
            st.caption(f"Clusters all **{len(materials)} lesson materials** into your preferred sensory channel:")

            transform_mode = st.radio(
                "Sensory Channel",
                ["🎧 Dual-Voice Podcast", "📊 Visual Slide Deck"],
                horizontal=True,
                label_visibility="collapsed",
            )

            if transform_mode == "🎧 Dual-Voice Podcast":
                if st.button("Synthesize Lesson Podcast", type="primary", use_container_width=True):
                    prog = st.empty()
                    res = generate_podcast_audio(
                        lesson=lesson,
                        clustered_text=clustered_text,
                        gemini_key=GOOGLE_API_KEY,
                        eleven_key=ELEVENLABS_API_KEY,
                        progress_fn=lambda msg: prog.info(msg),
                    )
                    st.session_state.podcast_cache[l_id] = res
                    for m in materials:
                        st.session_state.reviewed_materials[l_id].add(m["id"])
                    prog.empty()
                    st.rerun()

                pod = st.session_state.podcast_cache.get(l_id)
                if pod:
                    if pod.get("warning"):
                        st.warning(pod["warning"])
                    if pod.get("bytes"):
                        b64 = base64.b64encode(pod["bytes"]).decode("utf-8")
                        player_html = f"""
                        <div style="background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #cbd5e1;">
                            <audio id="podPlayer" controls style="width:100%;">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
                            </audio>
                            <div style="margin-top:8px; display:flex; gap:8px;">
                                <button onclick="document.getElementById('podPlayer').currentTime -= 10;" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">⏪ -10s</button>
                                <button onclick="document.getElementById('podPlayer').currentTime += 10;" style="background:#0284c7; color:white; border:none; padding:5px 10px; border-radius:4px; cursor:pointer;">+10s ⏩</button>
                            </div>
                        </div>
                        """
                        st.components.v1.html(player_html, height=115)
                    else:
                        full_dialogue = " ".join([f"{t['speaker'].replace('_', ' ')} says: {t['text']}" for t in pod["script"]])
                        safe_text = json.dumps(full_dialogue)
                        tts_html = f"""
                        <div style="background:#f0fdf4; padding:12px; border-radius:8px; border:1px solid #bbf7d0;">
                            <button onclick="window.speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance({safe_text}); u.rate=1.02; window.speechSynthesis.speak(u);" style="background:#059669; color:white; border:none; padding:7px 14px; border-radius:6px; cursor:pointer; font-weight:600;">▶️ Play Dialogue Audio</button>
                            <button onclick="window.speechSynthesis.cancel();" style="background:#e2e8f0; color:#0f172a; border:none; padding:7px 12px; border-radius:6px; cursor:pointer; margin-left:6px;">⏹️ Stop</button>
                        </div>
                        """
                        st.components.v1.html(tts_html, height=65)

                    with st.expander("View Podcast Transcript", expanded=True):
                        for t in pod["script"]:
                            who = "Host A (Sarah)" if t["speaker"] == "Host_A" else "Host B (George)"
                            st.markdown(f"**{who}:** {t['text']}")

            elif transform_mode == "📊 Visual Slide Deck":
                if st.button("Generate Scannable Slides", type="primary", use_container_width=True):
                    with st.spinner("Distilling clustered materials into visual slides..."):
                        st.session_state.slides_cache[l_id] = generate_visual_slides_ai(
                            lesson, clustered_text, GOOGLE_API_KEY
                        )
                        for m in materials:
                            st.session_state.reviewed_materials[l_id].add(m["id"])
                    st.rerun()

                slides = st.session_state.slides_cache.get(l_id, [])
                for idx_s, s in enumerate(slides, start=1):
                    bullets_html = "".join([f"<li>{b}</li>" for b in s["bullets"]])
                    st.markdown(
                        f"""
                        <div class="slide-card">
                            <span style="color:#0284c7; font-size:0.75rem; font-weight:700;">SLIDE {idx_s} • {s['pillar']}</span>
                            <h4 style="margin:4px 0 6px 0;">{s['title']}</h4>
                            <p style="color:#059669; font-weight:600; font-size:0.9rem;">{s['takeaway']}</p>
                            <ul style="font-size:0.88rem; color:#334155;">{bullets_html}</ul>
                            <div style="font-size:0.85rem; color:#0369a1; font-style:italic; border-top:1px dashed #cbd5e1; padding-top:6px;">
                                🥊 {s['question']}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with main_col:
            st.markdown(
                f"""
                <div class="workspace-box">
                    <span class="badge-blue">1 • Task for the Lesson</span>
                    <p style="margin:6px 0 0 0; font-size:0.98rem; color:#0f172a;">{lesson['task']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("⚡ 3-Step Bite-Sized Micro-Sprint (Task Initiation Scaffolding)", expanded=True):
                if l_id not in st.session_state.micro_sprints:
                    if st.button("Deconstruct Task into 3 Micro-Sprints", key=f"gen_sp_{l_id}"):
                        with st.spinner("Breaking task into low-friction sprints..."):
                            st.session_state.micro_sprints[l_id] = generate_micro_sprints_ai(
                                lesson["task"], clustered_text, GOOGLE_API_KEY
                            )
                        st.rerun()
                else:
                    sprints = st.session_state.micro_sprints[l_id]
                    changed = False
                    for idx_sp, sp in enumerate(sprints):
                        checked = st.checkbox(sp["step"], value=sp["done"], key=f"chk_{l_id}_{idx_sp}")
                        if checked != sp["done"]:
                            st.session_state.micro_sprints[l_id][idx_sp]["done"] = checked
                            changed = True
                    if changed:
                        st.rerun()

            st.markdown(
                """
                <div class="workspace-box-green">
                    <span class="badge-green">2 • Lesson Answer Space</span>
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#334155;">
                        Draft your strategic response below. Use the Socratic Sparring Box underneath to stress-test your logic before submitting.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            existing_ans = st.session_state.lesson_answers.get(l_id, {"text": "", "submitted": False})
            ans_text = st.text_area(
                "Your Executive Response",
                value=existing_ans["text"],
                height=140,
                placeholder="Write your strategic thesis & framework application here...",
                label_visibility="collapsed",
                key=f"ans_input_{l_id}",
            )
            ac1, ac2 = st.columns([1, 1])
            with ac1:
                if st.button("💾 Save Draft", key=f"save_{l_id}", use_container_width=True):
                    st.session_state.lesson_answers[l_id] = {"text": ans_text, "submitted": existing_ans["submitted"]}
                    st.toast("Draft saved!")
                    st.rerun()
            with ac2:
                if st.button("✅ Submit Final Answer to Professor", key=f"sub_{l_id}", type="primary", use_container_width=True):
                    if len(ans_text.strip()) < 15:
                        st.warning("Please write a substantive response before submitting.")
                    else:
                        st.session_state.lesson_answers[l_id] = {"text": ans_text, "submitted": True}
                        st.success("Answer submitted & locked into Faculty Proof-of-Work Ledger!")
                        st.rerun()

            st.write("")

            st.markdown(
                """
                <div class="workspace-box">
                    <span class="badge-blue">3 • Socratic Sparring Box (Closed-Loop)</span>
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#334155;">
                        Grounded strictly in this lesson's uploaded materials. Anti-ghostwriting active.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            spar_box = st.container(height=260)
            for msg in st.session_state.lesson_sparring[l_id]:
                with spar_box.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            spar_input = st.chat_input("Test your argument or ask NEAM to challenge your answer...", key=f"chat_{l_id}")
            if spar_input:
                st.session_state.lesson_sparring[l_id].append({"role": "user", "content": spar_input})
                with spar_box.chat_message("user"):
                    st.markdown(spar_input)

                with spar_box.chat_message("model"):
                    with st.spinner("Sparring with lesson materials..."):
                        reply = call_socratic_sparring(
                            prompt=spar_input,
                            history=st.session_state.lesson_sparring[l_id][:-1],
                            lesson=lesson,
                            clustered_text=clustered_text,
                            profile=profile,
                            api_key=GOOGLE_API_KEY,
                        )
                        st.markdown(reply)

                st.session_state.lesson_sparring[l_id].append({"role": "model", "content": reply})
                st.session_state.proof_of_work_log.append({
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "candidate": profile["name"],
                    "lesson": lesson["title"],
                    "student_prompt": spar_input,
                    "socratic_challenge": reply,
                })
                st.rerun()


# =========================================================
# 3. PROFESSOR PORTAL (UPLOAD MATERIALS & AUDIT)
# =========================================================
elif st.session_state.current_role == "professor":
    course = st.session_state.course_data
    st.markdown(f"<span class='badge-green'>Faculty Command Center</span>", unsafe_allow_html=True)
    st.title(f"Professor Workspace — {course['professor']}")
    st.caption(f"Course: **{course['course_name']}**")

    tab_upload, tab_audit = st.tabs(["📚 Manage Lesson Materials & Tasks", "📜 Student Proof-of-Work & Submissions"])

    with tab_upload:
        target_lesson_id = st.selectbox(
            "Select Lesson to Configure:",
            options=list(course["lessons"].keys()),
            format_func=lambda x: course["lessons"][x]["title"],
        )
        t_lesson = course["lessons"][target_lesson_id]

        st.subheader("1. Edit Lesson Assignment Task")
        new_task = st.text_area("Task for the Lesson", value=t_lesson["task"], height=90)
        if st.button("Update Lesson Task"):
            st.session_state.course_data["lessons"][target_lesson_id]["task"] = new_task
            st.success("Lesson task updated for students.")

        st.divider()
        st.subheader(f"2. Uploaded Materials in {t_lesson['title']} ({len(t_lesson['materials'])} items)")
        for m in t_lesson["materials"]:
            st.markdown(f"- **{m['title']}** ({m['type']}) — `{len(m['text'])} chars`")

        st.write("")
        st.markdown("#### ➕ Add New Material to This Lesson (No Limit)")
        with st.form(f"add_mat_{target_lesson_id}"):
            m_title = st.text_input("Material Title (e.g., Harvard Business Review Case Study)")
            m_type = st.selectbox("Material Category", ["Core Reading", "Case Study", "Lecture Note", "Framework"])
            uploaded_file = st.file_uploader("Upload TXT/MD file (or paste text below)", type=["txt", "md"])
            m_text = st.text_area("Material Content (Clustered automatically into Podcast, Slides & Sparring)", height=130)

            if st.form_submit_button("Upload & Cluster into Lesson", type="primary"):
                final_text = m_text.strip()
                fname = f"{m_title.replace(' ', '_')}.txt" if m_title else "Uploaded_Material.txt"
                if uploaded_file is not None:
                    final_text = uploaded_file.read().decode("utf-8", errors="ignore")
                    fname = uploaded_file.name

                if m_title and final_text:
                    new_id = f"MAT-{int(time.time())}"
                    st.session_state.course_data["lessons"][target_lesson_id]["materials"].append({
                        "id": new_id,
                        "title": m_title,
                        "type": m_type,
                        "filename": fname,
                        "text": final_text,
                    })
                    st.success(f"Added '{m_title}' to {t_lesson['title']}!")
                    st.rerun()
                else:
                    st.warning("Please provide both a title and text/file content.")

    with tab_audit:
        st.subheader("Submitted Lesson Answers")
        for l_id, lesson in course["lessons"].items():
            ans = st.session_state.lesson_answers.get(l_id)
            pct, _ = compute_lesson_mastery(l_id, lesson)
            with st.expander(f"{lesson['title']} — Mastery: {pct}% | Submitted: {'✅ Yes' if ans and ans.get('submitted') else '⏳ Draft'}"):
                if ans and ans.get("text"):
                    st.write(ans["text"])
                else:
                    st.info("No answer drafted yet.")

        st.divider()
        st.subheader("Chronological Socratic Proof-of-Work Trail")
        if st.session_state.proof_of_work_log:
            st.dataframe(st.session_state.proof_of_work_log, use_container_width=True)
        else:
            st.info("No student sparring turns recorded yet.")
