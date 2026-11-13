import os
import io
import time
import json
import base64
from datetime import datetime
from typing import List, Dict, Tuple
import requests
import streamlit as st

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False

# ---------------------------------------------------------
# Page Configuration & Unified Deep Navy Executive Theme
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
    /* Unified Deep Navy & Emerald Executive Palette (Matching Calibration Diagnostic) */
    .stApp {
        background-color: #0d1526;
        color: #f8fafc;
    }
    section[data-testid="stSidebar"] {
        background-color: #111b2e;
        border-right: 1px solid #263554;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, span, div {
        color: #f8fafc;
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #94a3b8 !important;
    }

    /* Inputs, Textareas, Selectboxes & Expanders */
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] > textarea,
    div[data-baseweb="select"] > div {
        background-color: #16243d !important;
        border-color: #2d3f63 !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }
    input, textarea {
        color: #f8fafc !important;
    }
    ul[data-baseweb="menu"] {
        background-color: #16243d !important;
        border: 1px solid #2d3f63 !important;
    }
    ul[data-baseweb="menu"] li {
        color: #f8fafc !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #1e3152 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #16243d !important;
        border: 1px solid #263554 !important;
        border-radius: 12px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: #263554 !important;
        background-color: #131f36;
        border-radius: 14px;
    }

    /* Buttons */
    button[kind="primary"] {
        background-color: #10b981 !important;
        border-color: #10b981 !important;
        color: #06281e !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }
    button[kind="primary"]:hover {
        background-color: #34d399 !important;
        border-color: #34d399 !important;
    }
    button[kind="secondary"] {
        background-color: #16243d !important;
        border: 1px solid #2d3f63 !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
    }
    button[kind="secondary"]:hover {
        border-color: #34d399 !important;
        color: #34d399 !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        color: #94a3b8 !important;
        font-weight: 600 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #34d399 !important;
        border-bottom-color: #34d399 !important;
    }

    /* Role Landing Cards */
    .role-card {
        background: #16243d;
        border: 1.5px solid #263554;
        border-radius: 16px;
        padding: 32px 24px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.25);
    }
    .role-card:hover {
        border-color: #34d399;
        transform: translateY(-2px);
        box-shadow: 0 14px 30px rgba(16, 185, 129, 0.14);
    }

    /* Eyebrow & Status Badges */
    .eyebrow-green {
        color: #34d399 !important;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .badge-blue {
        display: inline-block;
        background-color: rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38bdf8 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .badge-green {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.16);
        border: 1px solid rgba(52, 211, 153, 0.4);
        color: #34d399 !important;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .badge-amber {
        display: inline-block;
        background-color: rgba(245, 158, 11, 0.18);
        border: 1px solid rgba(251, 191, 36, 0.45);
        color: #fbbf24 !important;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    /* 5-Dimension Calibration Diagnostic Shell */
    .diag-shell {
        background-color: #16243d;
        border: 1px solid #263554;
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 18px;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
    }
    .diag-pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 16px 0 4px 0;
        padding-top: 14px;
        border-top: 1px solid #263554;
    }
    .diag-pill {
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #0f192d;
        color: #94a3b8 !important;
        border: 1px solid #263554;
    }
    .diag-pill-active {
        background-color: #10b981 !important;
        color: #06281e !important;
        border-color: #34d399 !important;
        font-weight: 700 !important;
    }

    /* Workspace Containers */
    .workspace-box {
        background-color: #16243d;
        border: 1px solid #263554;
        border-left: 5px solid #38bdf8;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .workspace-box-green {
        background-color: #132833;
        border: 1px solid #1e4647;
        border-left: 5px solid #10b981;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .material-viewer-card {
        background-color: #16243d;
        border: 1.5px solid #38bdf8;
        border-radius: 12px;
        padding: 16px;
        margin-top: 8px;
        margin-bottom: 14px;
    }
    .thermo-wrap {
        background: #16243d;
        border: 1px solid #263554;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 16px;
    }
    .thermo-track {
        width: 100%;
        height: 14px;
        background-color: #0d1526;
        border-radius: 9999px;
        overflow: hidden;
        margin-top: 6px;
        border: 1px solid #263554;
    }
    .slide-card {
        background-color: #16243d;
        border: 1px solid #263554;
        border-left: 5px solid #34d399;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.18);
    }
    .dossier-card {
        background-color: #16243d;
        border: 1px solid #263554;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
    }
    .sparring-bubble-ai {
        background-color: #16243d;
        border: 1px solid #263554;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .sparring-bubble-student {
        background-color: #132833;
        border: 1px solid #1e4647;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }

    /* Chat Input */
    div[data-testid="stChatInput"] {
        border-color: #2d3f63 !important;
        background-color: #16243d !important;
        border-radius: 12px !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #34d399 !important;
        box-shadow: 0 0 0 1px #34d399 !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #16243d !important;
        color: #f8fafc !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# High-Throughput API Configuration & Free-Tier Voices
# ---------------------------------------------------------
BASE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"
ACTIVE_MODELS = [
    "models/gemini-3.5-flash-lite",
    "models/gemini-3.6-flash",
    "models/gemini-4-argon",
    "models/gemini-3.8-flash",
]
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

VOICE_HOST_A = "EXAVITQu4vr4xnSDxMaL"  # Sarah (Default Premade)
VOICE_HOST_B = "JBFqnCBsd6RMkjVDRZzb"  # George (Default Premade)

# ---------------------------------------------------------
# Calibration Dimensions Catalog (Matching Your 5 Screens)
# ---------------------------------------------------------
DIM1_OPTIONS = [
    "Severe linear fatigue: Focus dissolves within 8–10 pages. (Enforces strict <130-word chunking).",
    "Moderate linear tolerance: Focus fades around page 20 without visual landmarks. (Caps at <175 words).",
    "High endurance if text is well-structured with executive takeaways. (Standard length).",
]

DIM2_OPTIONS = [
    "Listening on a walk / commute (Conversational Podcast Brief)",
    "Viewing visual diagrams & strategic slide canvases",
    "Talking out loud in real-time Socratic debate",
]

DIM3_OPTIONS = [
    "Blank-page paralysis: Starting the initial draft feels like an immovable barrier.",
    "Mid-stream organization: Brainstorming is fine, but sequencing into academic models is hard.",
    "Defensibility pressure: Starting is easy; the challenge is defending against scrutiny.",
]

DIM4_OPTIONS = [
    "Contrarian Devil's Advocate (Board-Level Counter-Interrogation)",
    "Encouraging Executive Coach (Supportive Socratic Guidance)",
]

DIM5_INTEREST_CATEGORIES = [
    "Video Games & Interactive Media (e.g. Nintendo Blue Ocean vs Sony/Xbox console wars)",
    "Music & Audio Production (e.g. Modular synthesizers disrupting digital audio software)",
    "Cinema, Sci-Fi & Screenwriting (e.g. Streaming unbundling Hollywood studio monopolies)",
    "Technology, AI & Startups (e.g. Disruptive SaaS displacing enterprise ERP monoliths)",
    "Architecture, Design & Fashion (e.g. Bauhaus and Scandinavian minimalism breaking cost-luxury trade-offs)",
    "High-Performance Sports & Racing (e.g. Formula 1 telemetry optimization and pitstop agility)",
]

# ---------------------------------------------------------
# Clean-Slate Session State (Zero Pre-Populated Dummy Data)
# ---------------------------------------------------------
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if "calib_step" not in st.session_state:
    st.session_state.calib_step = 1

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "id": "STU-LUCAS",
        "name": "Lucas Giraldo Mejía",
        "initials": "LG",
        "program": "Executive MBA in Creative Leadership",
        "onboarded": False,
        "working_memory": DIM1_OPTIONS[0],
        "sensory_channel": DIM2_OPTIONS[0],
        "task_initiation": DIM3_OPTIONS[1],
        "sparring_tone": DIM4_OPTIONS[0],
        "interest_domains": [DIM5_INTEREST_CATEGORIES[4]],
        "custom_passions": "",
    }

if "professor_profile" not in st.session_state:
    st.session_state.professor_profile = {
        "name": "Prof. Dr. Mario Vaupel",
        "title": "CEO & Professor of Sustainable Leadership • Steinbeis University Berlin",
    }

if "courses" not in st.session_state:
    st.session_state.courses = {}

if "cohort_records" not in st.session_state:
    st.session_state.cohort_records = {}

if "selected_student_course_id" not in st.session_state:
    st.session_state.selected_student_course_id = None

if "selected_lesson_id" not in st.session_state:
    st.session_state.selected_lesson_id = None

if "selected_material_by_lesson" not in st.session_state:
    st.session_state.selected_material_by_lesson = {}

if "open_full_reader_mat_id" not in st.session_state:
    st.session_state.open_full_reader_mat_id = None

if "selected_prof_course_id" not in st.session_state:
    st.session_state.selected_prof_course_id = None

if "selected_audit_student_id" not in st.session_state:
    st.session_state.selected_audit_student_id = None

if "reviewed_materials" not in st.session_state:
    st.session_state.reviewed_materials = {}

if "micro_sprints" not in st.session_state:
    st.session_state.micro_sprints = {}

if "lesson_answers" not in st.session_state:
    st.session_state.lesson_answers = {}

if "lesson_sparring" not in st.session_state:
    st.session_state.lesson_sparring = {}

if "material_podcast_cache" not in st.session_state:
    st.session_state.material_podcast_cache = {}

if "material_slides_cache" not in st.session_state:
    st.session_state.material_slides_cache = {}

# ---------------------------------------------------------
# Sidebar: Engine Gateway
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='eyebrow-green'>NEAM CORE ENGINE</div>", unsafe_allow_html=True)
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

    if st.session_state.student_profile.get("onboarded"):
        st.divider()
        st.markdown("<div class='eyebrow-green'>CALIBRATED PROFILE</div>", unsafe_allow_html=True)
        prof_s = st.session_state.student_profile
        st.caption(f"**Bandwidth:** {prof_s['working_memory'].split(':')[0]}")
        st.caption(f"**Channel:** {prof_s['sensory_channel'].split('(')[0].strip()}")
        st.caption(f"**Initiation:** {prof_s['task_initiation'].split(':')[0]}")
        st.caption(f"**Rigor:** {prof_s['sparring_tone'].split('(')[0].strip()}")
        if prof_s.get("custom_passions"):
            st.caption(f"**Anchors:** {prof_s['custom_passions'][:75]}")

# ---------------------------------------------------------
# Helper Functions: PDF Page Counter, Calibration & AI
# ---------------------------------------------------------
def extract_pdf_text_and_pages(file_bytes: bytes) -> Tuple[str, int]:
    if not HAS_PYPDF:
        return "", 1
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        num_pages = max(len(reader.pages), 1)
        pages = [page.extract_text() or "" for page in reader.pages[:40]]
        return "\n".join(pages).strip(), num_pages
    except Exception:
        return "", 1


def estimate_material_pages(mat: dict) -> int:
    if mat.get("page_count") and mat["page_count"] > 0:
        return int(mat["page_count"])
    word_count = len(mat.get("text", "").split())
    return max(1, round(word_count / 300))


def build_profile_prompt_directive(profile: dict) -> str:
    wm = profile.get("working_memory", DIM1_OPTIONS[0])
    sc = profile.get("sensory_channel", DIM2_OPTIONS[0])
    ti = profile.get("task_initiation", DIM3_OPTIONS[1])
    st_tone = profile.get("sparring_tone", DIM4_OPTIONS[0])
    domains = ", ".join(profile.get("interest_domains", []))
    custom = profile.get("custom_passions", "")
    anchors = f"{domains}. Specific passions: {custom}".strip()

    return (
        f"STUDENT COGNITIVE PROFILE (APPLY STRICTLY):\n"
        f"- Working Memory & Bandwidth: {wm}\n"
        f"- Primary Sensory Channel: {sc}\n"
        f"- Task Initiation Profile: {ti}\n"
        f"- Sparring Intensity & Rigor: {st_tone}\n"
        f"- Analogy & Metaphor Anchors (use vivid, non-repetitive examples from these interests): {anchors or 'Executive leadership & design'}\n"
    )


def get_word_cap_from_profile(profile: dict) -> Tuple[int, int]:
    wm = profile.get("working_memory", "")
    if "Severe linear fatigue" in wm:
        return 130, 320
    elif "Moderate linear tolerance" in wm:
        return 175, 420
    return 260, 650


def get_lesson_materials(course: dict, lesson_id: str) -> List[Dict]:
    mats = [m for m in course.get("materials_repo", []) if lesson_id in m.get("assigned_lessons", [])]
    return sorted(mats, key=lambda x: x["title"].lower())


def compute_lesson_mastery(course: dict, lesson_id: str) -> Tuple[int, str]:
    lesson_mats = get_lesson_materials(course, lesson_id)
    total_mats = max(len(lesson_mats), 1)
    reviewed_count = len([m for m in lesson_mats if m["id"] in st.session_state.reviewed_materials.get(lesson_id, set())])
    mat_score = (reviewed_count / total_mats) * 50.0 if lesson_mats else 0.0

    sprints = st.session_state.micro_sprints.get(lesson_id, [])
    if sprints:
        done_sprints = sum(1 for s in sprints if s.get("done"))
        sprint_score = (done_sprints / len(sprints)) * 20.0
    else:
        sprint_score = 0.0

    ans_data = st.session_state.lesson_answers.get(lesson_id, {})
    has_text = len(ans_data.get("text", "").strip()) > 15
    has_files = len(ans_data.get("attachments", [])) > 0
    ans_score = 30.0 if ans_data.get("submitted") else (15.0 if (has_text or has_files) else 0.0)

    total = min(int(round(mat_score + sprint_score + ans_score)), 100)
    color = "#10b981" if total == 100 else ("#34d399" if total >= 50 else "#38bdf8")
    return total, color


def format_single_material_context(mat: dict) -> str:
    extra = f" (YouTube Link: {mat['youtube_url']})" if mat.get("youtube_url") else ""
    pages = estimate_material_pages(mat)
    return f"MATERIAL TITLE: {mat['title']} ({mat.get('type', 'Reading')} • ~{pages} page(s)){extra}\nCONTENT:\n{mat.get('text', '')}"


def cluster_lesson_materials(materials: List[Dict]) -> str:
    if not materials:
        return "No materials currently assigned to this lesson."
    blocks = []
    for idx, m in enumerate(materials, start=1):
        extra = f" (YouTube Link: {m['youtube_url']})" if m.get("youtube_url") else ""
        blocks.append(f"[Material {idx}: {m['title']} ({m['type']}){extra}]\n{m['text']}")
    return "\n\n".join(blocks)


def sync_lucas_to_cohort(course_id: str, lesson_id: str):
    if course_id not in st.session_state.courses:
        return
    course = st.session_state.courses[course_id]
    if lesson_id not in course["lessons"]:
        return
    lesson = course["lessons"][lesson_id]
    pct, _ = compute_lesson_mastery(course, lesson_id)
    ans = st.session_state.lesson_answers.get(lesson_id, {})
    chat = st.session_state.lesson_sparring.get(lesson_id, [])

    sparring_turns = [
        {
            "role": m["role"],
            "time": m.get("time", datetime.now().strftime("%H:%M")),
            "content": m["content"],
        }
        for m in chat
        if m.get("role") in ("user", "model")
    ]

    record_key = f"STU-LUCAS-{lesson_id}"
    existing = st.session_state.cohort_records.get(record_key, {})
    prev_rubric = existing.get(
        "rubric",
        {"problem_clarification": 4.5, "theoretical_grounding": 4.5, "strategic_defensibility": 4.5, "feedback": ""},
    )

    st.session_state.cohort_records[record_key] = {
        "name": st.session_state.student_profile["name"],
        "initials": "LG",
        "course_id": course_id,
        "lesson_id": lesson_id,
        "lesson_title": lesson["title"],
        "mastery_pct": pct,
        "submitted": bool(ans.get("submitted", False)),
        "evaluated": bool(ans.get("evaluated", False)),
        "submitted_at": ans.get("submitted_at", "Active Session"),
        "hash": f"NEAM-BSCL-LUCAS-{lesson_id}-SHA256",
        "answer_text": ans.get("text", ""),
        "attachments": ans.get("attachments", []),
        "voice_notes": [],
        "sparring_dialogue": sparring_turns,
        "rubric": prev_rubric,
    }


def generate_micro_sprints_ai(task_text: str, context_text: str, profile: dict, api_key: str) -> List[Dict]:
    default_sprints = [
        {"step": "Sprint 1 (5 min): Extract the single core tension or assumption from the lesson materials.", "done": False},
        {"step": "Sprint 2 (10 min): Map 2 concrete strategic levers from the reading onto your thesis context.", "done": False},
        {"step": "Sprint 3 (10 min): Draft a sharp 3-sentence executive defense in the Lesson Answer Space.", "done": False},
    ]
    if not api_key:
        return default_sprints

    prof_dir = build_profile_prompt_directive(profile)
    prompt = f"""
{prof_dir}
Break this MBA assignment task down into exactly 3 bite-sized, sequential 5-to-10 minute micro-sprints calibrated to the student's Task Initiation profile.
Keep each step under 20 words. Return ONLY 3 lines formatted as:
1 | [Step 1]
2 | [Step 2]
3 | [Step 3]

Task: {task_text}
Context: {context_text[:1500]}
"""
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 260},
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


def generate_single_material_slides_ai(mat: dict, profile: dict, api_key: str) -> List[Dict]:
    mat_context = format_single_material_context(mat)
    sentences = [s.strip() for s in mat.get("text", "").split(".") if len(s.strip()) > 12]
    fallback_slides = [
        {
            "pillar": mat.get("type", "CORE MATERIAL").upper(),
            "title": mat["title"],
            "takeaway": sentences[0] + "." if sentences else mat["title"],
            "bullets": [s + "." for s in sentences[1:3]] or ["Review the full material or download the source file."],
            "question": f"How does '{mat['title']}' challenge your strategic assumptions?",
        }
    ]
    if not api_key:
        return fallback_slides

    prof_dir = build_profile_prompt_directive(profile)
    prompt = f"""
{prof_dir}
Convert ONLY this single course material into 4 high-impact, scannable executive slides.
Weave analogies or examples subtly from the student's Passions & Interests when helpful so concepts stick immediately.
Focus strictly on this specific document. Return ONLY lines in this exact pipe-delimited format (one slide per line):
PILLAR | SLIDE TITLE | CORE TAKEAWAY | BULLET 1; BULLET 2 | SPARRING QUESTION

{mat_context[:4500]}
"""
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.35, "maxOutputTokens": 700},
    }
    for model_path in ACTIVE_MODELS:
        try:
            resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=22)
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


def generate_single_material_podcast(
    mat: dict,
    profile: dict,
    gemini_key: str,
    eleven_key: str,
    progress_fn=None,
) -> Dict:
    est_pages = estimate_material_pages(mat)
    target_minutes = min(max(est_pages, 1), 20)
    target_words = target_minutes * 140
    target_turns = max(4, min(target_minutes * 4, 48))
    max_tokens = min(max(int(target_words * 1.6), 450), 4500)

    if progress_fn:
        progress_fn(
            f"Detected ~{est_pages} page(s) in '{mat['title']}' → Targeting ~{target_minutes} min podcast ({target_turns} dialogue turns)..."
        )

    prof_dir = build_profile_prompt_directive(profile)
    mat_context = format_single_material_context(mat)

    script_prompt = f"""
{prof_dir}

TASK: Convert ONLY this single Steinbeis course material into an engaging, deep-dive executive podcast dialogue between Host_A and Host_B.
- TARGET LENGTH: Approximately {target_minutes} minute(s) of spoken audio (~{target_words} total words across {target_turns} alternating turns).
- PACING & DEPTH: Cover every major concept, framework, and nuance in the document proportionally to its {est_pages}-page length. Do not rush or skip sections.
- NO META-INTRO FANFARE: Jump straight into the core strategic dilemma in turn 1.
- PERSONALIZED ANALOGIES: Weave vivid, non-repetitive analogies from the student's Passions & Interests profile to anchor abstract theories.
- STRICT FORMAT: Output ONLY alternating lines formatted exactly as:
Host_A | [Dialogue turn]
Host_B | [Dialogue turn]

{mat_context[:18000]}
"""
    script = []
    if gemini_key:
        headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}
        payload = {
            "contents": [{"role": "user", "parts": [{"text": script_prompt}]}],
            "generationConfig": {"temperature": 0.45, "maxOutputTokens": max_tokens},
        }
        for model_path in ACTIVE_MODELS:
            try:
                resp = requests.post(f"{BASE_GEMINI_URL}/{model_path}:generateContent", headers=headers, json=payload, timeout=45)
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
        sentences = [s.strip() for s in mat.get("text", "").split(".") if len(s.strip()) > 12]
        script = [
            {"speaker": "Host_A", "text": f"Let's unpack the strategic architecture of {mat['title']}."},
            {"speaker": "Host_B", "text": (sentences[0] + ".") if sentences else mat["title"]},
            {"speaker": "Host_A", "text": "How does that translate into executive decision-making under pressure?"},
            {"speaker": "Host_B", "text": (sentences[1] + ".") if len(sentences) > 1 else "It forces leaders to eliminate low-value overhead and focus on structural differentiation."},
        ]

    if not eleven_key:
        return {
            "bytes": None,
            "script": script,
            "target_minutes": target_minutes,
            "warning": "No ElevenLabs key provided — using instant browser voice reader.",
        }

    audio_buffer = io.BytesIO()
    for i, turn in enumerate(script):
        if progress_fn:
            progress_fn(f"Synthesizing voice turn {i + 1}/{len(script)} (~{target_minutes} min target) via ElevenLabs...")
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
                timeout=30,
            )
            if tts_resp.status_code == 200:
                audio_buffer.write(tts_resp.content)
            else:
                return {
                    "bytes": None,
                    "script": script,
                    "target_minutes": target_minutes,
                    "warning": f"ElevenLabs returned {tts_resp.status_code} (check credits/permissions). Switched to instant browser audio.",
                }
        except Exception as e:
            return {
                "bytes": None,
                "script": script,
                "target_minutes": target_minutes,
                "warning": f"ElevenLabs timeout ({e}). Switched to instant browser audio.",
            }

    audio_buffer.seek(0)
    return {"bytes": audio_buffer.read(), "script": script, "target_minutes": target_minutes, "warning": None}


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

    word_cap, max_tokens = get_word_cap_from_profile(profile)
    prof_dir = build_profile_prompt_directive(profile)

    system_instruction = f"""
You are NEAM, an executive Socratic sparring partner for Steinbeis University / Berlin School of Creative Leadership.
Candidate: {profile.get('name')} ({profile.get('program')}).
Active Lesson: {lesson['title']}
Lesson Assignment Task: {lesson['task']}

{prof_dir}

STRICT ARCHITECTURAL SAFEGUARDS:
1. CLOSED-LOOP GROUNDING: Base every argument strictly on the lesson materials provided below.
2. ANTI-GHOSTWRITING: Never write the student's final answer or essay for them. Challenge weak assumptions, test logic against the lesson frameworks, and ask sharp dialectic questions.
3. COGNITIVE BANDWIDTH CAP: Strictly cap your response under {word_cap} words to match the student's calibrated Working Memory profile. Use crisp bullet points or bold key concepts.

LESSON MATERIALS:
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


# =========================================================
# 1. LANDING VIEW (UNIFIED DEEP NAVY EXECUTIVE ARCHITECTURE)
# =========================================================
if st.session_state.current_role is None:
    st.markdown(
        "<div class='eyebrow-green' style='text-align: center; margin-top: 24px;'>"
        "STEINBEIS UNIVERSITY BERLIN • BERLIN SCHOOL OF CREATIVE LEADERSHIP"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<h1 style='text-align: center; margin-top: 4px; font-size: 3rem;'>NEAM</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #cbd5e1; font-size: 1.1rem; margin-bottom: 36px;'>"
        "Neurodivergent Executive AI Module &amp; Closed-Loop Cognitive Scaffolding"
        "</p>",
        unsafe_allow_html=True,
    )

    _, col_s, col_p, _ = st.columns([1, 2.2, 2.2, 1], gap="large")

    with col_s:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge-blue">Executive Candidate</span>
                <div style="font-size: 3rem; margin: 10px 0;">🎓</div>
                <h2 style="margin-bottom: 8px;">Student</h2>
                <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.5;">
                    5-Dimension cognitive calibration, single-material multimodal transformation, micro-sprints, and Socratic sparring.
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
                <span class="badge-green">Faculty &amp; Curriculum</span>
                <div style="font-size: 3rem; margin: 10px 0;">🏛️</div>
                <h2 style="margin-bottom: 8px;">Professor</h2>
                <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.5;">
                    Build courses &amp; lessons, upload PDF/Video/YouTube materials, and evaluate student Proof-of-Work dossiers.
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

    # -----------------------------------------------------
    # 2A. ONE-TIME 5-DIMENSION COGNITIVE DIAGNOSTIC
    # -----------------------------------------------------
    if not profile["onboarded"]:
        if st.button("← Back to Landing", key="back_cal_landing"):
            st.session_state.current_role = None
            st.rerun()

        step = st.session_state.calib_step
        pills_html = ""
        dim_labels = [
            "1. Working Memory",
            "2. Sensory Channel",
            "3. Task Initiation",
            "4. Sparring Tone",
            "5. Passions & Interests",
        ]
        for idx_d, lbl in enumerate(dim_labels, start=1):
            cls = "diag-pill diag-pill-active" if idx_d == step else "diag-pill"
            pills_html += f"<span class='{cls}'>{lbl}</span>"

        st.markdown(
            f"""
            <div class="diag-shell">
                <div class="eyebrow-green">NEAM COGNITIVE ONBOARDING DIAGNOSTIC • PERSONALIZED SCAFFOLDING</div>
                <h2 style="margin:0 0 6px 0;">Calibrate Your Executive Learning Engine</h2>
                <p style="margin:0; font-size:0.95rem; color:#cbd5e1 !important;">
                    NEAM diagnoses your working memory limits and personal passions to tailor every podcast, slide deck, and Socratic challenge to your mental model.
                </p>
                <div class="diag-pill-row">{pills_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            if step == 1:
                st.markdown("### Dimension 1: Working Memory & Cognitive Bandwidth")
                st.write("**When tackling a 40-page academic case study, where does your focus typically break down?**")
                sel_wm = st.radio(
                    "Working Memory Profile",
                    options=DIM1_OPTIONS,
                    index=DIM1_OPTIONS.index(profile["working_memory"]) if profile["working_memory"] in DIM1_OPTIONS else 0,
                    label_visibility="collapsed",
                )
                st.session_state.student_profile["working_memory"] = sel_wm

                st.write("")
                _, n_col = st.columns([4, 1.5])
                with n_col:
                    if st.button("Next Dimension →", type="primary", use_container_width=True):
                        st.session_state.calib_step = 2
                        st.rerun()

            elif step == 2:
                st.markdown("### Dimension 2: Primary Sensory Channel")
                st.write("**Do you retain strategic concepts better by listening on a walk, viewing diagrams, or talking out loud?**")
                sel_sc = st.radio(
                    "Primary Sensory Channel",
                    options=DIM2_OPTIONS,
                    index=DIM2_OPTIONS.index(profile["sensory_channel"]) if profile["sensory_channel"] in DIM2_OPTIONS else 0,
                    label_visibility="collapsed",
                )
                st.session_state.student_profile["sensory_channel"] = sel_sc

                st.write("")
                b_col, _, n_col = st.columns([1.2, 3, 1.5])
                with b_col:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.calib_step = 1
                        st.rerun()
                with n_col:
                    if st.button("Next Dimension →", type="primary", use_container_width=True):
                        st.session_state.calib_step = 3
                        st.rerun()

            elif step == 3:
                st.markdown("### Dimension 3: Task Initiation Friction (ADHD Blank-Page Paralysis)")
                st.write("**What is your biggest hurdle when starting an assignment: starting the draft or refining logic?**")
                sel_ti = st.radio(
                    "Task Initiation Friction",
                    options=DIM3_OPTIONS,
                    index=DIM3_OPTIONS.index(profile["task_initiation"]) if profile["task_initiation"] in DIM3_OPTIONS else 1,
                    label_visibility="collapsed",
                )
                st.session_state.student_profile["task_initiation"] = sel_ti

                st.write("")
                b_col, _, n_col = st.columns([1.2, 3, 1.5])
                with b_col:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.calib_step = 2
                        st.rerun()
                with n_col:
                    if st.button("Next Dimension →", type="primary", use_container_width=True):
                        st.session_state.calib_step = 4
                        st.rerun()

            elif step == 4:
                st.markdown("### Dimension 4: Sparring Intensity & Rigor")
                st.write("**Do you prefer an encouraging executive coach or a contrarian devil's advocate?**")
                sel_st = st.radio(
                    "Sparring Intensity",
                    options=DIM4_OPTIONS,
                    index=DIM4_OPTIONS.index(profile["sparring_tone"]) if profile["sparring_tone"] in DIM4_OPTIONS else 0,
                    label_visibility="collapsed",
                )
                st.session_state.student_profile["sparring_tone"] = sel_st

                st.write("")
                b_col, _, n_col = st.columns([1.2, 3, 1.5])
                with b_col:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.calib_step = 3
                        st.rerun()
                with n_col:
                    if st.button("Next Dimension →", type="primary", use_container_width=True):
                        st.session_state.calib_step = 5
                        st.rerun()

            elif step == 5:
                st.markdown("### Dimension 5: Personalized Anchor & Analogy Engine")
                st.write("**What are your personal passions & interests?**")
                st.caption("NEAM dynamically weaves examples and analogies from these fields into every podcast dialogue, slide deck, and Socratic challenge so concepts stick immediately.")

                selected_domains = st.multiselect(
                    "Select your core passion domains:",
                    options=DIM5_INTEREST_CATEGORIES,
                    default=[d for d in profile.get("interest_domains", []) if d in DIM5_INTEREST_CATEGORIES],
                )
                custom_passions = st.text_input(
                    "SPECIFIC SUB-INTERESTS OR OBSESSIONS (FREE-FORM):",
                    value=profile.get("custom_passions", ""),
                    placeholder="e.g., Mid-century architecture, cycling performance, sci-fi worldbuilding, specialty cocktails...",
                )

                st.session_state.student_profile["interest_domains"] = selected_domains
                st.session_state.student_profile["custom_passions"] = custom_passions

                st.write("")
                b_col, _, save_col = st.columns([1.2, 2.5, 2])
                with b_col:
                    if st.button("← Back", use_container_width=True):
                        st.session_state.calib_step = 4
                        st.rerun()
                with save_col:
                    if st.button("✅ Apply & Save Diagnostic Profile", type="primary", use_container_width=True):
                        st.session_state.student_profile["onboarded"] = True
                        st.session_state.calib_step = 1
                        st.rerun()

    # -----------------------------------------------------
    # 2B. STUDENT COURSE & SYLLABUS HOME
    # -----------------------------------------------------
    elif st.session_state.selected_lesson_id is None:
        nav_back, _ = st.columns([1.4, 6])
        with nav_back:
            if st.button("← Back to Landing", key="back_stu_landing", use_container_width=True):
                st.session_state.current_role = None
                st.rerun()

        st.markdown("<div class='diag-shell' style='padding: 20px 26px;'>", unsafe_allow_html=True)
        h_avatar, h_info, h_cal = st.columns([0.7, 5, 1.5])
        with h_avatar:
            st.markdown(
                "<div style='width:56px;height:56px;border-radius:50%;background:#10b981;color:#06281e;"
                "display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.3rem;'>LG</div>",
                unsafe_allow_html=True,
            )
        with h_info:
            st.markdown(f"<h3 style='margin:0;'>{profile['name']}</h3>", unsafe_allow_html=True)
            st.caption(f"{profile['program']} • Calibrated Channel: **{profile['sensory_channel'].split('(')[0].strip()}**")
        with h_cal:
            if st.button("⚙️ Recalibrate", use_container_width=True):
                st.session_state.student_profile["onboarded"] = False
                st.session_state.calib_step = 1
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if not st.session_state.courses:
            st.info(
                "No courses have been published yet. Switch to the **Professor** portal to create a course, "
                "add lessons, and upload your PDF/Video/YouTube materials."
            )
        else:
            course_ids = list(st.session_state.courses.keys())
            if st.session_state.selected_student_course_id not in course_ids:
                st.session_state.selected_student_course_id = course_ids[0]

            selected_c_id = st.selectbox(
                "Enrolled MBA Course:",
                options=course_ids,
                index=course_ids.index(st.session_state.selected_student_course_id),
                format_func=lambda cid: f"{st.session_state.courses[cid]['code']} — {st.session_state.courses[cid]['course_name']}",
            )
            st.session_state.selected_student_course_id = selected_c_id
            course = st.session_state.courses[selected_c_id]

            st.markdown("<span class='badge-green'>Active MBA Syllabus</span>", unsafe_allow_html=True)
            st.markdown(f"## {course['course_name']}")
            st.caption(f"Faculty Lead: **{st.session_state.professor_profile['name']}** • Select a syllabus lesson below:")
            st.write("")

            if not course["lessons"]:
                st.warning("This course has no lessons yet. Add lessons inside the Professor Workspace.")
            else:
                for l_id, lesson in course["lessons"].items():
                    pct, _ = compute_lesson_mastery(course, l_id)
                    lesson_mats = get_lesson_materials(course, l_id)
                    with st.container(border=True):
                        c_title, c_prog, c_btn = st.columns([4, 2, 1.5])
                        with c_title:
                            st.markdown(f"#### {lesson['title']}")
                            st.caption(f"{lesson['summary']} ({len(lesson_mats)} assigned materials)")
                        with c_prog:
                            st.markdown(f"**Lesson Mastery: {pct}%**")
                            st.progress(pct / 100.0)
                        with c_btn:
                            st.write("")
                            if st.button("Open Lesson →", key=f"open_{l_id}", type="primary", use_container_width=True):
                                st.session_state.selected_lesson_id = l_id
                                st.session_state.open_full_reader_mat_id = None
                                sync_lucas_to_cohort(selected_c_id, l_id)
                                st.rerun()

    # -----------------------------------------------------
    # 2C. ACTIVE LESSON WORKSPACE
    # -----------------------------------------------------
    else:
        c_id = st.session_state.selected_student_course_id
        course = st.session_state.courses[c_id]
        l_id = st.session_state.selected_lesson_id
        lesson = course["lessons"][l_id]
        materials = get_lesson_materials(course, l_id)
        clustered_text = cluster_lesson_materials(materials)

        if l_id not in st.session_state.reviewed_materials:
            st.session_state.reviewed_materials[l_id] = set()
        if l_id not in st.session_state.lesson_sparring:
            st.session_state.lesson_sparring[l_id] = [
                {
                    "role": "model",
                    "time": datetime.now().strftime("%H:%M"),
                    "content": (
                        f"Closed-loop sparring locked to **{lesson['title']}** and calibrated to your cognitive profile. "
                        "Inspect a material on the left, then test your thesis premise here before submitting."
                    ),
                }
            ]

        if st.button("← Back to Course Syllabus", key="back_to_syllabus"):
            st.session_state.selected_lesson_id = None
            st.session_state.open_full_reader_mat_id = None
            st.rerun()

        pct, thermo_color = compute_lesson_mastery(course, l_id)
        top_av, top_title, top_thermo = st.columns([0.6, 3.8, 2.6])
        with top_av:
            st.markdown(
                "<div style='width:50px;height:50px;border-radius:50%;background:#10b981;color:#06281e;"
                "display:flex;align-items:center;justify-content:center;font-weight:800;font-size:1.15rem;'>LG</div>",
                unsafe_allow_html=True,
            )
        with top_title:
            st.markdown(f"<div class='eyebrow-green'>{course['course_name']}</div>", unsafe_allow_html=True)
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

        # Full-Window Material Viewer
        if st.session_state.open_full_reader_mat_id:
            open_mat = next((m for m in materials if m["id"] == st.session_state.open_full_reader_mat_id), None)
            if open_mat:
                with st.container(border=True):
                    fr_h1, fr_h2 = st.columns([5, 1])
                    with fr_h1:
                        st.markdown(f"### 📖 Full Material Viewer: {open_mat['title']}")
                        st.caption(f"Format: **{open_mat.get('type', 'Reading')}** • Estimated Length: **~{estimate_material_pages(open_mat)} page(s)**")
                    with fr_h2:
                        if st.button("✖ Close Viewer", key="close_full_reader", use_container_width=True):
                            st.session_state.open_full_reader_mat_id = None
                            st.rerun()

                    if open_mat.get("youtube_url"):
                        st.info("This material is hosted on YouTube. Click below to open it directly in a new browser tab:")
                        st.link_button("▶️ Open YouTube Video in New Window", url=open_mat["youtube_url"], type="primary")
                        if open_mat.get("text"):
                            st.markdown("**Lecture Notes / Summary:**")
                            st.write(open_mat["text"])
                    elif open_mat.get("file_bytes") and open_mat.get("mime_type", "").startswith("video/"):
                        st.video(open_mat["file_bytes"])
                        if open_mat.get("text"):
                            st.write(open_mat["text"])
                    elif open_mat.get("file_bytes") and open_mat.get("mime_type") == "application/pdf":
                        b64_pdf = base64.b64encode(open_mat["file_bytes"]).decode("utf-8")
                        pdf_iframe = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="560" type="application/pdf" style="border:1px solid #263554; border-radius:8px;"></iframe>'
                        st.components.v1.html(pdf_iframe, height=575)
                        if open_mat.get("text"):
                            with st.expander("View Extracted PDF Text"):
                                st.write(open_mat["text"])
                    else:
                        st.markdown(
                            f"""
                            <div style="background:#16243d; border:1px solid #263554; border-radius:8px; padding:20px; font-size:1rem; line-height:1.6; color:#f8fafc;">
                                {open_mat.get('text', '')}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                st.write("")

        rail_col, main_col = st.columns([1.45, 2.55], gap="large")

        # -------------------------------------------------
        # LEFT RAIL: SELECT 1 MATERIAL -> VIEW / DOWNLOAD -> TRANSFORM ONLY THAT ONE
        # -------------------------------------------------
        with rail_col:
            st.markdown("#### 1️⃣ Select 1 Lesson Material")
            st.caption("Pick **one** material to view, download, or transform (~1 min podcast per page):")

            if not materials:
                st.info("No materials assigned to this lesson yet. Upload materials in the Professor Workspace.")
            else:
                mat_ids = [m["id"] for m in materials]
                default_mat_id = st.session_state.selected_material_by_lesson.get(l_id)
                if default_mat_id not in mat_ids:
                    default_mat_id = mat_ids[0]

                def format_mat_label(mid: str) -> str:
                    m_obj = next(x for x in materials if x["id"] == mid)
                    done_mark = "✅ " if mid in st.session_state.reviewed_materials[l_id] else ""
                    mtype = m_obj.get("type", "")
                    t_icon = "🎬" if "Video" in mtype or "YouTube" in mtype else ("📕" if "PDF" in mtype else "📄")
                    pg = estimate_material_pages(m_obj)
                    return f"{done_mark}{t_icon} {m_obj['title']} (~{pg}p)"

                chosen_mat_id = st.radio(
                    "Choose single material:",
                    options=mat_ids,
                    index=mat_ids.index(default_mat_id),
                    format_func=format_mat_label,
                    label_visibility="collapsed",
                    key=f"radio_mat_{l_id}",
                )
                st.session_state.selected_material_by_lesson[l_id] = chosen_mat_id
                selected_mat = next(m for m in materials if m["id"] == chosen_mat_id)
                is_done = chosen_mat_id in st.session_state.reviewed_materials[l_id]
                est_pg = estimate_material_pages(selected_mat)

                st.markdown(
                    f"""
                    <div class="material-viewer-card">
                        <span class="badge-blue">{selected_mat.get('type', 'Reading')} • ~{est_pg} page(s)</span>
                        <h4 style="margin:4px 0 6px 0;">{selected_mat['title']}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if selected_mat.get("youtube_url"):
                    st.write(selected_mat.get("text", ""))
                    st.link_button(
                        "▶️ Open on YouTube (New Window)",
                        url=selected_mat["youtube_url"],
                        type="primary",
                        use_container_width=True,
                    )
                elif selected_mat.get("file_bytes") and selected_mat.get("mime_type", "").startswith("video/"):
                    st.video(selected_mat["file_bytes"])
                else:
                    snippet = selected_mat.get("text", "")
                    st.write(snippet[:320] + ("..." if len(snippet) > 320 else ""))

                act1, act2, act3 = st.columns(3)
                with act1:
                    if st.button("🔍 Open Full View", key=f"open_view_{chosen_mat_id}", use_container_width=True):
                        st.session_state.open_full_reader_mat_id = chosen_mat_id
                        st.session_state.reviewed_materials[l_id].add(chosen_mat_id)
                        sync_lucas_to_cohort(c_id, l_id)
                        st.rerun()
                with act2:
                    if selected_mat.get("file_bytes"):
                        st.download_button(
                            "⬇️ Download",
                            data=selected_mat["file_bytes"],
                            file_name=selected_mat.get("filename", f"{chosen_mat_id}.bin"),
                            mime=selected_mat.get("mime_type", "application/octet-stream"),
                            key=f"dl_{chosen_mat_id}",
                            use_container_width=True,
                        )
                    elif not selected_mat.get("youtube_url"):
                        st.download_button(
                            "⬇️ Download",
                            data=selected_mat.get("text", "").encode("utf-8"),
                            file_name=selected_mat.get("filename", f"{chosen_mat_id}.txt"),
                            mime="text/plain",
                            key=f"dl_{chosen_mat_id}",
                            use_container_width=True,
                        )
                with act3:
                    if not is_done:
                        if st.button("✅ Mark Done", key=f"rev_{chosen_mat_id}", use_container_width=True):
                            st.session_state.reviewed_materials[l_id].add(chosen_mat_id)
                            sync_lucas_to_cohort(c_id, l_id)
                            st.rerun()
                    else:
                        st.success("Reviewed")

                st.divider()

                # -------------------------------------------------
                # STEP 2: TRANSFORM ONLY THIS SELECTED MATERIAL (~1 MIN / PAGE)
                # -------------------------------------------------
                st.markdown("#### 2️⃣ Transform Selected Material Only")
                st.caption(
                    f"Target runtime: **~{min(max(est_pg, 1), 20)} min** (~1 min/page) • Tailored to your calibrated passions & bandwidth."
                )

                default_radio_idx = 1 if "Visual" in profile.get("sensory_channel", "") else 0
                transform_mode = st.radio(
                    "Sensory Channel",
                    ["🎧 Dual-Voice Podcast", "📊 Visual Slide Deck"],
                    index=default_radio_idx,
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"tmode_{l_id}",
                )

                if transform_mode == "🎧 Dual-Voice Podcast":
                    if st.button(
                        f"Synthesize ~{min(max(est_pg, 1), 20)}-Min Podcast",
                        type="primary",
                        use_container_width=True,
                        key=f"btn_pod_{chosen_mat_id}",
                    ):
                        prog = st.empty()
                        res = generate_single_material_podcast(
                            mat=selected_mat,
                            profile=profile,
                            gemini_key=GOOGLE_API_KEY,
                            eleven_key=ELEVENLABS_API_KEY,
                            progress_fn=lambda msg: prog.info(msg),
                        )
                        st.session_state.material_podcast_cache[chosen_mat_id] = res
                        st.session_state.reviewed_materials[l_id].add(chosen_mat_id)
                        sync_lucas_to_cohort(c_id, l_id)
                        prog.empty()
                        st.rerun()

                    pod = st.session_state.material_podcast_cache.get(chosen_mat_id)
                    if pod:
                        if pod.get("warning"):
                            st.warning(pod["warning"])
                        if pod.get("bytes"):
                            b64 = base64.b64encode(pod["bytes"]).decode("utf-8")
                            player_html = f"""
                            <div style="background:#16243d; padding:12px; border-radius:10px; border:1px solid #263554;">
                                <audio id="podPlayer" controls style="width:100%;">
                                    <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
                                </audio>
                                <div style="margin-top:8px; display:flex; gap:8px;">
                                    <button onclick="document.getElementById('podPlayer').currentTime -= 10;" style="background:#10b981; color:#06281e; font-weight:700; border:none; padding:5px 12px; border-radius:6px; cursor:pointer;">⏪ -10s</button>
                                    <button onclick="document.getElementById('podPlayer').currentTime += 10;" style="background:#10b981; color:#06281e; font-weight:700; border:none; padding:5px 12px; border-radius:6px; cursor:pointer;">+10s ⏩</button>
                                </div>
                            </div>
                            """
                            st.components.v1.html(player_html, height=115)
                        else:
                            full_dialogue = " ".join([f"{t['speaker'].replace('_', ' ')} says: {t['text']}" for t in pod["script"]])
                            safe_text = json.dumps(full_dialogue)
                            tts_html = f"""
                            <div style="background:#16243d; padding:12px; border-radius:10px; border:1px solid #263554;">
                                <button onclick="window.speechSynthesis.cancel(); var u = new SpeechSynthesisUtterance({safe_text}); u.rate=1.02; window.speechSynthesis.speak(u);" style="background:#10b981; color:#06281e; border:none; padding:7px 14px; border-radius:6px; cursor:pointer; font-weight:700;">▶️ Play Dialogue Audio</button>
                                <button onclick="window.speechSynthesis.cancel();" style="background:#263554; color:#f8fafc; border:none; padding:7px 12px; border-radius:6px; cursor:pointer; margin-left:6px;">⏹️ Stop</button>
                            </div>
                            """
                            st.components.v1.html(tts_html, height=65)

                        with st.expander("View Podcast Transcript", expanded=True):
                            for t in pod["script"]:
                                who = "Host A (Sarah)" if t["speaker"] == "Host_A" else "Host B (George)"
                                st.markdown(f"**{who}:** {t['text']}")

                elif transform_mode == "📊 Visual Slide Deck":
                    if st.button("Generate Scannable Slides", type="primary", use_container_width=True, key=f"btn_sld_{chosen_mat_id}"):
                        with st.spinner(f"Distilling '{selected_mat['title']}' into visual slides..."):
                            st.session_state.material_slides_cache[chosen_mat_id] = generate_single_material_slides_ai(
                                selected_mat, profile, GOOGLE_API_KEY
                            )
                            st.session_state.reviewed_materials[l_id].add(chosen_mat_id)
                            sync_lucas_to_cohort(c_id, l_id)
                        st.rerun()

                    slides = st.session_state.material_slides_cache.get(chosen_mat_id, [])
                    for idx_s, s in enumerate(slides, start=1):
                        bullets_html = "".join([f"<li>{b}</li>" for b in s["bullets"]])
                        st.markdown(
                            f"""
                            <div class="slide-card">
                                <span style="color:#34d399; font-size:0.75rem; font-weight:700;">SLIDE {idx_s} • {s['pillar']}</span>
                                <h4 style="margin:4px 0 6px 0;">{s['title']}</h4>
                                <p style="color:#38bdf8; font-weight:600; font-size:0.9rem;">{s['takeaway']}</p>
                                <ul style="font-size:0.88rem; color:#cbd5e1;">{bullets_html}</ul>
                                <div style="font-size:0.85rem; color:#34d399; font-style:italic; border-top:1px dashed #2d3f63; padding-top:6px;">
                                    🥊 {s['question']}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        # -------------------------------------------------
        # RIGHT WORKSPACE: TASK + ANSWER + SPARRING
        # -------------------------------------------------
        with main_col:
            st.markdown(
                f"""
                <div class="workspace-box">
                    <span class="badge-blue">1 • Task for the Lesson</span>
                    <p style="margin:6px 0 0 0; font-size:0.98rem; color:#f8fafc;">{lesson['task']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("⚡ 3-Step Bite-Sized Micro-Sprint (Task Initiation Scaffolding)", expanded=True):
                if l_id not in st.session_state.micro_sprints:
                    if st.button("Deconstruct Task into 3 Micro-Sprints", key=f"gen_sp_{l_id}"):
                        with st.spinner("Breaking task into low-friction sprints..."):
                            st.session_state.micro_sprints[l_id] = generate_micro_sprints_ai(
                                lesson["task"], clustered_text, profile, GOOGLE_API_KEY
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
                        sync_lucas_to_cohort(c_id, l_id)
                        st.rerun()

            st.markdown(
                """
                <div class="workspace-box-green">
                    <span class="badge-green">2 • Lesson Answer Space &amp; Deliverable Upload</span>
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#cbd5e1;">
                        Write your executive response and/or attach supporting visuals, diagrams, or PDFs (JPG, PNG, PDF, DOCX).
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            existing_ans = st.session_state.lesson_answers.get(
                l_id, {"text": "", "submitted": False, "attachments": [], "evaluated": False}
            )
            ans_text = st.text_area(
                "Your Executive Response",
                value=existing_ans.get("text", ""),
                height=130,
                placeholder="Write your strategic thesis & framework application here...",
                label_visibility="collapsed",
                key=f"ans_input_{l_id}",
            )

            uploaded_deliverables = st.file_uploader(
                "📎 Attach Supporting Files (JPG, PNG, PDF, DOCX, ZIP)",
                type=["jpg", "jpeg", "png", "webp", "pdf", "docx", "txt", "zip"],
                accept_multiple_files=True,
                key=f"ans_files_{l_id}",
            )

            saved_attachments = list(existing_ans.get("attachments", []))
            if uploaded_deliverables:
                existing_names = {a["name"] for a in saved_attachments}
                for uf in uploaded_deliverables:
                    if uf.name not in existing_names:
                        saved_attachments.append({
                            "name": uf.name,
                            "type": uf.type or "application/octet-stream",
                            "bytes": uf.getvalue(),
                        })

            if saved_attachments:
                st.caption(f"**Attached Deliverables ({len(saved_attachments)}):** " + ", ".join([a["name"] for a in saved_attachments]))

            ac1, ac2 = st.columns([1, 1])
            with ac1:
                if st.button("💾 Save Draft", key=f"save_{l_id}", use_container_width=True):
                    st.session_state.lesson_answers[l_id] = {
                        "text": ans_text,
                        "submitted": existing_ans.get("submitted", False),
                        "attachments": saved_attachments,
                        "evaluated": existing_ans.get("evaluated", False),
                        "submitted_at": existing_ans.get("submitted_at", "Draft Saved"),
                    }
                    sync_lucas_to_cohort(c_id, l_id)
                    st.toast("Draft & attachments saved!")
                    st.rerun()
            with ac2:
                if st.button("✅ Submit Final Answer to Professor", key=f"sub_{l_id}", type="primary", use_container_width=True):
                    if len(ans_text.strip()) < 10 and not saved_attachments:
                        st.warning("Please write a response or attach a deliverable file before submitting.")
                    else:
                        st.session_state.lesson_answers[l_id] = {
                            "text": ans_text,
                            "submitted": True,
                            "attachments": saved_attachments,
                            "evaluated": False,
                            "submitted_at": datetime.now().strftime("Today at %H:%M CET"),
                        }
                        sync_lucas_to_cohort(c_id, l_id)
                        st.success("Submitted! Your profile is now highlighted in Dr. Vaupel's Evaluation Console.")
                        st.rerun()

            st.write("")

            st.markdown(
                """
                <div class="workspace-box">
                    <span class="badge-blue">3 • Socratic Sparring Box (Closed-Loop)</span>
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#cbd5e1;">
                        Grounded strictly in this lesson's uploaded materials. Anti-ghostwriting active.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            spar_box = st.container(height=250)
            for msg in st.session_state.lesson_sparring[l_id]:
                with spar_box.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            spar_input = st.chat_input("Test your argument or ask NEAM to challenge your answer...", key=f"chat_{l_id}")
            if spar_input:
                now_hm = datetime.now().strftime("%H:%M")
                st.session_state.lesson_sparring[l_id].append({"role": "user", "time": now_hm, "content": spar_input})
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

                st.session_state.lesson_sparring[l_id].append({"role": "model", "time": now_hm, "content": reply})
                sync_lucas_to_cohort(c_id, l_id)
                st.rerun()


# =========================================================
# 3. PROFESSOR WORKSPACE
# =========================================================
elif st.session_state.current_role == "professor":
    prof = st.session_state.professor_profile

    if st.session_state.selected_prof_course_id is None:
        if st.button("← Back to Landing", key="back_prof_landing"):
            st.session_state.current_role = None
            st.rerun()

        st.markdown(
            f"""
            <div class="diag-shell" style="padding: 22px 28px;">
                <div class="eyebrow-green">FACULTY COMMAND CENTER • STEINBEIS UNIVERSITY BERLIN</div>
                <h2 style="margin:2px 0 4px 0;">{prof['name']}</h2>
                <p style="margin:0; color:#cbd5e1 !important; font-size:0.95rem;">{prof['title']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        hdr_c, btn_c = st.columns([4, 1.6])
        with hdr_c:
            st.subheader("Courses Taught at the University")
            st.caption("Create a course and add lessons & materials to begin:")
        with btn_c:
            with st.popover("➕ Create New Course", use_container_width=True):
                st.markdown("#### New MBA Course")
                c_code = st.text_input("Course Code (e.g., EMBA-601)", key="new_c_code")
                c_name = st.text_input("Course Title", key="new_c_name")
                c_desc = st.text_area("Course Description", height=80, key="new_c_desc")
                if st.button("Create Course", type="primary", key="create_c_btn"):
                    if c_name.strip():
                        new_cid = f"CRS-{int(time.time())}"
                        st.session_state.courses[new_cid] = {
                            "course_name": c_name.strip(),
                            "code": c_code.strip() or "EMBA",
                            "description": c_desc.strip(),
                            "lessons": {},
                            "materials_repo": [],
                        }
                        st.session_state.selected_prof_course_id = new_cid
                        st.rerun()
                    else:
                        st.warning("Please enter a course title.")

        if not st.session_state.courses:
            st.info("No courses created yet. Click **➕ Create New Course** above to set up your first MBA course.")
        else:
            for cid, cdata in st.session_state.courses.items():
                l_count = len(cdata["lessons"])
                m_count = len(cdata["materials_repo"])
                pending_evals = sum(
                    1 for s in st.session_state.cohort_records.values()
                    if s.get("course_id") == cid and s.get("submitted") and not s.get("evaluated")
                )
                with st.container(border=True):
                    cc1, cc2 = st.columns([4.5, 1.5])
                    with cc1:
                        badge_extra = f" &nbsp;<span class='badge-amber'>🔔 {pending_evals} Pending Evaluation</span>" if pending_evals else ""
                        st.markdown(f"<span class='badge-blue'>{cdata['code']}</span>{badge_extra}", unsafe_allow_html=True)
                        st.markdown(f"### {cdata['course_name']}")
                        st.caption(f"{cdata['description']} • **{l_count} Lessons** | **{m_count} Course Materials**")
                    with cc2:
                        st.write("")
                        st.write("")
                        if st.button("Open Course →", key=f"prof_open_{cid}", type="primary", use_container_width=True):
                            st.session_state.selected_prof_course_id = cid
                            st.rerun()

    else:
        cid = st.session_state.selected_prof_course_id
        course = st.session_state.courses[cid]

        if st.button("← Back to Courses", key="back_prof_courses"):
            st.session_state.selected_prof_course_id = None
            st.rerun()

        st.markdown(f"<span class='badge-blue'>{course['code']}</span>", unsafe_allow_html=True)
        st.markdown(f"## {course['course_name']}")

        pending_count = sum(
            1 for s in st.session_state.cohort_records.values()
            if s.get("course_id") == cid and s.get("submitted") and not s.get("evaluated")
        )
        audit_label = f"🎓 Student Proof-of-Work & Evaluation ({pending_count} New)" if pending_count else "🎓 Student Proof-of-Work & Evaluation"

        tab_builder, tab_audit = st.tabs([
            "🗂️ Course Lessons & Materials Mapper (PDF / Video / YouTube)",
            audit_label
        ])

        with tab_builder:
            col_lessons, col_materials = st.columns([1.25, 1.45], gap="large")

            with col_lessons:
                lh1, lh2 = st.columns([3, 1.6])
                with lh1:
                    st.markdown("### 📘 Course's Lessons")
                with lh2:
                    with st.popover("➕ Add Lesson", use_container_width=True):
                        st.markdown("#### New Syllabus Lesson")
                        new_l_title = st.text_input("Lesson Title (e.g., Lesson 1: Value Innovation)", key=f"nl_t_{cid}")
                        new_l_sum = st.text_input("Short Summary", key=f"nl_s_{cid}")
                        new_l_task = st.text_area("Task / Assignment Prompt for Students", height=100, key=f"nl_task_{cid}")
                        if st.button("Create Lesson", type="primary", key=f"add_l_btn_{cid}"):
                            if new_l_title.strip():
                                new_lid = f"LES-{int(time.time())}"
                                st.session_state.courses[cid]["lessons"][new_lid] = {
                                    "title": new_l_title.strip(),
                                    "summary": new_l_sum.strip() or "Core syllabus lesson.",
                                    "task": new_l_task.strip() or "Synthesize the key strategic takeaways from the assigned materials.",
                                }
                                st.rerun()
                            else:
                                st.warning("Enter a lesson title.")

                if not course["lessons"]:
                    st.info("No lessons in this course yet. Click **➕ Add Lesson** above.")
                else:
                    for l_id, lesson in course["lessons"].items():
                        assigned_mats = get_lesson_materials(course, l_id)
                        with st.container(border=True):
                            st.markdown(f"#### {lesson['title']}")
                            st.caption(lesson["summary"])
                            st.markdown(f"**Assigned Materials ({len(assigned_mats)}):**")
                            if assigned_mats:
                                for am in assigned_mats:
                                    icon = "🎬" if "Video" in am["type"] or "YouTube" in am["type"] else ("📕" if "PDF" in am["type"] else "📄")
                                    st.markdown(f"- {icon} {am['title']} (~{estimate_material_pages(am)}p)")
                            else:
                                st.caption("_No materials assigned yet._")

                            with st.expander("✏️ Edit Lesson Task"):
                                updated_task = st.text_area(
                                    "Task for the Lesson",
                                    value=lesson["task"],
                                    key=f"edit_task_{cid}_{l_id}",
                                    height=90,
                                )
                                if st.button("Save Task", key=f"save_task_{cid}_{l_id}"):
                                    st.session_state.courses[cid]["lessons"][l_id]["task"] = updated_task
                                    st.success("Task updated!")
                                    st.rerun()

            with col_materials:
                hdr_m, btn_m = st.columns([3, 1.6])
                with hdr_m:
                    st.markdown("### 📚 Course's Materials")
                    st.caption("Sorted alphabetically (A–Z). Upload PDF, Video, YouTube, or Text:")
                with btn_m:
                    with st.popover("➕ Upload Material", use_container_width=True):
                        st.markdown("#### Upload New Course Material")
                        new_m_title = st.text_input("Material Title", key=f"new_mt_{cid}")
                        new_m_type = st.selectbox(
                            "Material Type",
                            ["PDF Document", "Video File", "YouTube Video", "Text / Reading"],
                            key=f"new_mtype_{cid}",
                        )

                        up_file = None
                        yt_link = ""
                        if new_m_type == "PDF Document":
                            up_file = st.file_uploader("Upload PDF", type=["pdf"], key=f"up_pdf_{cid}")
                        elif new_m_type == "Video File":
                            up_file = st.file_uploader("Upload Video (MP4, MOV, WEBM)", type=["mp4", "mov", "webm"], key=f"up_vid_{cid}")
                        elif new_m_type == "YouTube Video":
                            yt_link = st.text_input("Paste YouTube URL (https://www.youtube.com/watch?v=...)", key=f"yt_{cid}")
                        else:
                            up_file = st.file_uploader("Upload TXT/MD File (Optional)", type=["txt", "md"], key=f"up_txt_{cid}")

                        new_m_text = st.text_area(
                            "Summary / Key Notes (Used alongside PDF text when generating Podcast or Slides)",
                            height=100,
                            key=f"new_mtxt_{cid}",
                        )
                        default_lessons = st.multiselect(
                            "Assign immediately to lesson(s):",
                            options=list(course["lessons"].keys()),
                            format_func=lambda x: course["lessons"][x]["title"],
                            key=f"new_massign_{cid}",
                        )

                        if st.button("Add to Course", type="primary", key=f"add_m_btn_{cid}"):
                            if not new_m_title.strip():
                                st.warning("Please enter a material title.")
                            else:
                                fbytes = None
                                fmimetype = "text/plain"
                                fname = f"{new_m_title.strip().replace(' ', '_')}.txt"
                                extracted_text = new_m_text.strip()
                                page_count = 1

                                if up_file is not None:
                                    fbytes = up_file.getvalue()
                                    fmimetype = up_file.type or "application/octet-stream"
                                    fname = up_file.name
                                    if new_m_type == "PDF Document":
                                        pdf_txt, page_count = extract_pdf_text_and_pages(fbytes)
                                        if pdf_txt:
                                            extracted_text = (extracted_text + "\n\n" + pdf_txt).strip()
                                        elif not extracted_text:
                                            extracted_text = f"PDF Document uploaded: {fname}"
                                    elif new_m_type == "Video File":
                                        if not extracted_text:
                                            extracted_text = f"Uploaded video lecture: {fname}"
                                    elif new_m_type == "Text / Reading":
                                        if not extracted_text:
                                            extracted_text = fbytes.decode("utf-8", errors="ignore")
                                        page_count = max(1, round(len(extracted_text.split()) / 300))
                                else:
                                    page_count = max(1, round(len(extracted_text.split()) / 300))

                                if new_m_type == "YouTube Video":
                                    if not yt_link.strip():
                                        st.warning("Please paste a valid YouTube link.")
                                        st.stop()
                                    if not extracted_text:
                                        extracted_text = f"YouTube lecture video: {new_m_title.strip()} ({yt_link.strip()})"

                                st.session_state.courses[cid]["materials_repo"].append({
                                    "id": f"MAT-{int(time.time())}",
                                    "title": new_m_title.strip(),
                                    "type": new_m_type,
                                    "filename": fname if new_m_type != "YouTube Video" else None,
                                    "assigned_lessons": default_lessons,
                                    "text": extracted_text or new_m_title.strip(),
                                    "file_bytes": fbytes,
                                    "mime_type": fmimetype,
                                    "youtube_url": yt_link.strip() if new_m_type == "YouTube Video" else None,
                                    "page_count": page_count,
                                })
                                st.success("Material uploaded & added to repository!")
                                st.rerun()

                sorted_repo = sorted(course["materials_repo"], key=lambda x: x["title"].lower())
                lesson_ids = list(course["lessons"].keys())

                if not sorted_repo:
                    st.info("No materials uploaded yet. Click **➕ Upload Material** above to add PDFs, videos, YouTube links, or readings.")
                else:
                    for mat in sorted_repo:
                        mtype = mat.get("type", "Text / Reading")
                        icon = "🎬" if "Video" in mtype or "YouTube" in mtype else ("📕" if "PDF" in mtype else "📄")
                        pg = estimate_material_pages(mat)
                        with st.container(border=True):
                            st.markdown(f"**{icon} {mat['title']}** `{mtype} • ~{pg}p`")
                            if mat.get("youtube_url"):
                                st.caption(f"🔗 {mat['youtube_url']}")
                            else:
                                preview = mat.get("text", "")
                                st.caption(preview[:130] + ("..." if len(preview) > 130 else ""))

                            current_assigned = [lid for lid in mat.get("assigned_lessons", []) if lid in lesson_ids]
                            new_assigned = st.multiselect(
                                "Assigned to Lesson(s):",
                                options=lesson_ids,
                                default=current_assigned,
                                format_func=lambda x: course["lessons"][x]["title"],
                                key=f"assign_{cid}_{mat['id']}",
                            )
                            if set(new_assigned) != set(current_assigned):
                                for orig_m in st.session_state.courses[cid]["materials_repo"]:
                                    if orig_m["id"] == mat["id"]:
                                        orig_m["assigned_lessons"] = new_assigned
                                st.rerun()

        with tab_audit:
            cohort_for_course = {
                k: v for k, v in st.session_state.cohort_records.items() if v.get("course_id") == cid
            }

            if not cohort_for_course:
                st.info("No student activity or submissions recorded for this course yet. Enter as **Student**, open a lesson, and interact or submit work to see it appear here live.")
            else:
                roster_col, dossier_col = st.columns([1.15, 2.35], gap="large")

                with roster_col:
                    st.markdown("### 👥 Enrolled Students")
                    st.caption("Sorted alphabetically (A–Z). Highlighted names have ungraded submissions:")

                    cohort_list = sorted(cohort_for_course.values(), key=lambda x: x["name"].lower())
                    id_by_key = {f"{v['name']}_{v['lesson_id']}": k for k, v in cohort_for_course.items()}

                    for stu in cohort_list:
                        sid = id_by_key[f"{stu['name']}_{stu['lesson_id']}"]
                        needs_eval = stu.get("submitted") and not stu.get("evaluated")
                        is_selected = st.session_state.selected_audit_student_id == sid

                        border_color = "#fbbf24" if needs_eval else ("#34d399" if is_selected else "#263554")
                        bg_color = "#262115" if needs_eval else ("#1a2d4a" if is_selected else "#16243d")
                        bar_col = "#10b981" if stu["mastery_pct"] == 100 else "#38bdf8"

                        status_badge = (
                            "<span class='badge-amber'>🔔 Needs Evaluation</span>"
                            if needs_eval
                            else ("<span class='badge-green'>✓ Evaluated</span>" if stu.get("evaluated") else "<span class='badge-blue'>In Progress</span>")
                        )

                        st.markdown(
                            f"""
                            <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:12px; padding:12px 14px; margin-bottom:8px;">
                                <div style="display:flex; align-items:center; justify-content:space-between;">
                                    <div style="display:flex; align-items:center; gap:10px;">
                                        <div style="width:36px; height:36px; border-radius:50%; background:#10b981; color:#06281e; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:0.85rem;">
                                            {stu['initials']}
                                        </div>
                                        <div>
                                            <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">{stu['name']}</div>
                                            <div style="font-size:0.75rem; color:#94a3b8;">{stu['lesson_title']} • {stu['mastery_pct']}%</div>
                                        </div>
                                    </div>
                                    {status_badge}
                                </div>
                                <div style="width:100%; height:8px; background:#0d1526; border-radius:9999px; overflow:hidden; margin-top:8px;">
                                    <div style="width:{stu['mastery_pct']}%; height:100%; background:{bar_col};"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button("Inspect Dossier →", key=f"sel_stu_{sid}", use_container_width=True):
                            st.session_state.selected_audit_student_id = sid
                            st.rerun()

                with dossier_col:
                    active_sid = st.session_state.selected_audit_student_id
                    if active_sid not in cohort_for_course:
                        active_sid = next(iter(cohort_for_course.keys()))
                    stu = cohort_for_course[active_sid]

                    dossier_md = f"""# PROOF-OF-WORK VERIFICATION • {stu['hash']}
**Candidate:** {stu['name']}
**Lesson:** {stu['lesson_title']}
**Status:** {'Submitted' if stu['submitted'] else 'In Progress'} ({stu['submitted_at']})
**Lesson Mastery:** {stu['mastery_pct']}%

## 1. Student's Final Submitted Answer
{stu['answer_text'] or '_No written answer submitted yet._'}

## 2. Complete Socratic Sparring Dialogue (Anti-Ghostwriting: 100% Student Reasoning)
""" + ("\n".join([f"- **{t['role'].upper()}** [{t['time']}]: {t['content']}" for t in stu.get("sparring_dialogue", [])]) or "_No sparring turns recorded._")

                    dh1, dh2 = st.columns([3.5, 1.5])
                    with dh1:
                        st.markdown(f"<div class='eyebrow-green'>PROOF-OF-WORK VERIFICATION • {stu['hash']}</div>", unsafe_allow_html=True)
                        st.markdown(f"### {stu['name']} — {stu['lesson_title']}")
                        st.caption(f"{course['course_name']} • {stu['submitted_at']}")
                    with dh2:
                        st.write("")
                        st.download_button(
                            "⬇️ Download Dossier (.md)",
                            data=dossier_md.encode("utf-8"),
                            file_name=f"{stu['name'].replace(' ', '_')}_ProofOfWork.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    st.markdown(
                        f"""
                        <div class="dossier-card">
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#94a3b8; margin-bottom:6px;">
                                <span>1. STUDENT'S FINAL SUBMITTED ANSWER</span>
                                <span>{len(stu.get('answer_text', ''))} characters</span>
                            </div>
                            <p style="margin:0; font-size:0.95rem; color:#f8fafc;">{stu.get('answer_text') or 'No answer submitted yet.'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if stu.get("attachments"):
                        st.markdown("**📎 Student Uploaded Deliverables:**")
                        for att_idx, att in enumerate(stu["attachments"]):
                            ac_a, ac_b = st.columns([3, 1])
                            with ac_a:
                                if att.get("type", "").startswith("image/"):
                                    st.image(att["bytes"], caption=att["name"], width=280)
                                else:
                                    st.markdown(f"- 📄 **{att['name']}** (`{att.get('type', 'file')}`)")
                            with ac_b:
                                st.download_button(
                                    "⬇️ Download",
                                    data=att["bytes"],
                                    file_name=att["name"],
                                    mime=att.get("type", "application/octet-stream"),
                                    key=f"prof_dl_{active_sid}_{att_idx}",
                                )

                    st.markdown("**🥊 2. COMPLETE SOCRATIC SPARRING DIALOGUE (Anti-Ghostwriting: 100% Student Reasoning):**")
                    dialogue = stu.get("sparring_dialogue", [])
                    if dialogue:
                        for turn in dialogue:
                            if turn["role"] == "model":
                                st.markdown(
                                    f"""
                                    <div class="sparring-bubble-ai">
                                        <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#38bdf8;">
                                            <span>NEAM AI Sparring Partner</span>
                                            <span>{turn.get('time', '')}</span>
                                        </div>
                                        <div style="font-size:0.9rem; margin-top:4px; color:#f8fafc;">{turn['content']}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    f"""
                                    <div class="sparring-bubble-student">
                                        <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#34d399;">
                                            <span>{stu['name']}</span>
                                            <span>{turn.get('time', '')}</span>
                                        </div>
                                        <div style="font-size:0.9rem; margin-top:4px; color:#f8fafc;">{turn['content']}</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.caption("No sparring dialogue recorded yet.")

                    st.divider()

                    rubric = stu.get("rubric", {"problem_clarification": 4.0, "theoretical_grounding": 4.0, "strategic_defensibility": 4.0, "feedback": ""})
                    r1, r2, r3 = st.columns(3)
                    with r1:
                        s_prob = st.slider("Problem Clarification (0–5)", 0.0, 5.0, float(rubric["problem_clarification"]), 0.1, key=f"rub_p_{active_sid}")
                    with r2:
                        s_theo = st.slider("Theoretical Grounding (0–5)", 0.0, 5.0, float(rubric["theoretical_grounding"]), 0.1, key=f"rub_t_{active_sid}")
                    with r3:
                        s_strat = st.slider("Strategic Defensibility (0–5)", 0.0, 5.0, float(rubric["strategic_defensibility"]), 0.1, key=f"rub_s_{active_sid}")

                    composite = round((s_prob + s_theo + s_strat) / 3.0, 2)
                    st.markdown(
                        f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#132833; border:1px solid #1e4647; padding:12px 16px; border-radius:10px; margin:8px 0;">
                            <span style="font-weight:700; color:#34d399;">⚖️ FACULTY RUBRIC GRADING CONSOLE</span>
                            <span style="font-weight:800; font-size:1.1rem; color:#10b981;">Composite: {composite:.2f} / 5.0</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    qual_fb = st.text_area(
                        "PROFESSOR QUALITATIVE FEEDBACK:",
                        value=rubric.get("feedback", ""),
                        placeholder="Enter professor comments on strategic rigor, trade-off clarity, and defensibility...",
                        key=f"rub_fb_{active_sid}",
                        height=90,
                    )

                    if st.button("Save Grade & Rubric Evaluation", type="primary", key=f"save_grade_{active_sid}"):
                        st.session_state.cohort_records[active_sid]["rubric"] = {
                            "problem_clarification": s_prob,
                            "theoretical_grounding": s_theo,
                            "strategic_defensibility": s_strat,
                            "feedback": qual_fb,
                        }
                        st.session_state.cohort_records[active_sid]["evaluated"] = True
                        lid_target = stu["lesson_id"]
                        if lid_target in st.session_state.lesson_answers:
                            st.session_state.lesson_answers[lid_target]["evaluated"] = True
                        st.success(f"Evaluation saved for {stu['name']} ({composite:.2f}/5.0). Pending highlight cleared!")
                        st.rerun()
