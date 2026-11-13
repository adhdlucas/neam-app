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
        margin-bottom: 8px;
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
        margin-bottom: 8px;
    }
    .badge-amber {
        display: inline-block;
        background-color: #fef3c7;
        color: #b45309;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .workspace-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #0284c7;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .workspace-box-green {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #059669;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .material-viewer-card {
        background-color: #f8fafc;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 16px;
        margin-top: 8px;
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
        padding: 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .dossier-card {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 14px;
    }
    .sparring-bubble-ai {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
    }
    .sparring-bubble-student {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #059669;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 8px;
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
# Session State & Multi-Course Data Model
# ---------------------------------------------------------
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "id": "STU-LUCAS",
        "name": "Lucas Giraldo Mejía",
        "initials": "LG",
        "program": "Executive MBA in Creative Leadership",
        "onboarded": False,
        "working_memory_chunking": True,
        "primary_modality": "Audio-First (Executive Podcast)",
        "task_initiation_scaffolding": True,
        "sparring_intensity": "Contrarian Devil's Advocate (Rigor)",
    }

if "professor_profile" not in st.session_state:
    st.session_state.professor_profile = {
        "name": "Prof. Dr. Mario Vaupel",
        "title": "CEO & Professor of Sustainable Leadership • Steinbeis University Berlin",
    }

if "selected_student_course_id" not in st.session_state:
    st.session_state.selected_student_course_id = "CRS-01"

if "selected_lesson_id" not in st.session_state:
    st.session_state.selected_lesson_id = None

if "selected_material_by_lesson" not in st.session_state:
    st.session_state.selected_material_by_lesson = {}  # {lesson_id: material_id}

if "open_full_reader_mat_id" not in st.session_state:
    st.session_state.open_full_reader_mat_id = None

if "selected_prof_course_id" not in st.session_state:
    st.session_state.selected_prof_course_id = None

if "selected_audit_student_id" not in st.session_state:
    st.session_state.selected_audit_student_id = "STU-ELENA"

if "courses" not in st.session_state:
    st.session_state.courses = {
        "CRS-01": {
            "course_name": "Strategic Alignment & Creative Leadership",
            "code": "EMBA-601",
            "description": "Value Innovation, Blue Ocean Strategy, and Creating Shared Value (CSV) for executive transformation.",
            "lessons": {
                "LES-01": {
                    "title": "Lesson 1: Value Innovation & Blue Ocean Strategy",
                    "summary": "Breaking the value-cost trade-off using the Strategy Canvas and the Four Actions Framework (ERRC Grid).",
                    "task": (
                        "Identify one entrenched industry assumption in your executive domain. Using the Four Actions Framework "
                        "(Eliminate, Reduce, Raise, Create), formulate a strategic thesis explaining how eliminating that factor "
                        "lowers cost structure while unlocking uncontested buyer value."
                    ),
                },
                "LES-02": {
                    "title": "Lesson 2: Creating Shared Value (CSV) & Sustainable Leadership",
                    "summary": "Reconnecting company success with social progress beyond traditional CSR philanthropy.",
                    "task": (
                        "Contrast Corporate Social Responsibility (CSR) with Porter & Kramer's Creating Shared Value (CSV). "
                        "Propose one value-chain reconception in your organization that generates measurable economic profit "
                        "directly through solving a societal or environmental bottleneck."
                    ),
                },
            },
            "materials_repo": [
                {
                    "id": "MAT-101",
                    "title": "Blue Ocean Strategy — Value Innovation Core (Kim & Mauborgne)",
                    "type": "Text / Reading",
                    "filename": "Blue_Ocean_Value_Innovation.txt",
                    "assigned_lessons": ["LES-01"],
                    "text": (
                        "Blue Ocean Strategy challenges companies to break out of red oceans of bloody competition "
                        "by creating uncontested market space that makes the competition irrelevant. Instead of choosing "
                        "between low cost and high differentiation, Value Innovation pursues both simultaneously. "
                        "Value innovation is created in the region where a company's actions favorably affect both its cost structure "
                        "and its value proposition to buyers. Cost savings are made by eliminating and reducing the factors an industry competes on. "
                        "Buyer value is lifted by raising and creating elements the industry has never offered."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
                {
                    "id": "MAT-103",
                    "title": "Executive Education Red Ocean Case",
                    "type": "Text / Reading",
                    "filename": "Executive_Education_Case.txt",
                    "assigned_lessons": ["LES-01"],
                    "text": (
                        "In executive education, traditional monomodal lecturing represents a high-overhead red ocean "
                        "that creates cognitive overload for neurodivergent leaders. Long static PDFs and passive slide decks "
                        "force working-memory bottlenecks. Closed-loop multimodal scaffolding eliminates passive friction "
                        "by letting executives isolate single artifacts, listen via conversational audio, and test ideas via active dialectic proof-of-work."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
                {
                    "id": "MAT-102",
                    "title": "Four Actions Framework (ERRC Diagnostic Grid)",
                    "type": "Text / Reading",
                    "filename": "ERRC_Framework_Guide.txt",
                    "assigned_lessons": ["LES-01"],
                    "text": (
                        "The Four Actions Framework asks four key questions to challenge an industry's strategic logic: "
                        "1) Which factors that the industry takes for granted should be Eliminated? "
                        "2) Which factors should be Reduced well below the industry standard? "
                        "3) Which factors should be Raised well above the industry standard? "
                        "4) Which factors should be Created that the industry has never offered? "
                        "The ERRC Grid pushes companies not only to ask all four questions but also to act on all four to create a new value curve."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
                {
                    "id": "MAT-104",
                    "title": "Kim & Mauborgne — Blue Ocean Strategy Keynote (YouTube)",
                    "type": "YouTube Video",
                    "filename": None,
                    "assigned_lessons": ["LES-01"],
                    "text": (
                        "Video Lecture Summary: W. Chan Kim and Renée Mauborgne explain how organizations reconstruct "
                        "market boundaries using the Strategy Canvas and ERRC Grid to unlock non-customers instead of fighting over shrinking market share."
                    ),
                    "file_bytes": None,
                    "mime_type": None,
                    "youtube_url": "https://www.youtube.com/results?search_query=Blue+Ocean+Strategy+Kim+Mauborgne",
                },
                {
                    "id": "MAT-201",
                    "title": "Shared Value Foundation (Porter & Kramer)",
                    "type": "Text / Reading",
                    "filename": "Porter_Kramer_CSV.txt",
                    "assigned_lessons": ["LES-02"],
                    "text": (
                        "Creating Shared Value (CSV) focuses on policies and operating practices that enhance the competitiveness "
                        "of a company while simultaneously advancing the economic and social conditions in the communities in which "
                        "it operates. Unlike CSR, which is peripheral and driven by reputation, CSV is integral to profitability."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
                {
                    "id": "MAT-202",
                    "title": "Three Pillars of Shared Value Execution",
                    "type": "Text / Reading",
                    "filename": "Three_Pillars_CSV.txt",
                    "assigned_lessons": ["LES-02"],
                    "text": (
                        "Companies can create shared value in three distinct ways: 1) Reconceiving products and markets to meet "
                        "underserved societal needs; 2) Redefining productivity in the value chain (energy use, logistics, resource efficiency); "
                        "and 3) Enabling local cluster development around the company's operational hubs."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
            ],
        },
        "CRS-02": {
            "course_name": "Organizational Transformation & Creative Governance",
            "code": "EMBA-604",
            "description": "Leading creative teams, neuroinclusive organizational design, and change management.",
            "lessons": {
                "LES-201": {
                    "title": "Lesson 1: Neuroinclusive Executive Architecture",
                    "summary": "Designing high-autonomy workflows that leverage divergent cognitive styles.",
                    "task": (
                        "Audit one recurring decision workflow in your organization and propose two structural redesigns "
                        "that eliminate working-memory bottlenecks while preserving strategic accountability."
                    ),
                },
            },
            "materials_repo": [
                {
                    "id": "MAT-301",
                    "title": "Cognitive Load & Executive Decision Architecture",
                    "type": "Text / Reading",
                    "filename": "Cognitive_Load_Governance.txt",
                    "assigned_lessons": ["LES-201"],
                    "text": (
                        "High-performing organizations reduce extraneous cognitive load by chunking complex strategic briefs "
                        "into clear milestones, multimodal summaries, and structured dialectic checkpoints."
                    ),
                    "file_bytes": None,
                    "mime_type": "text/plain",
                    "youtube_url": None,
                },
            ],
        },
    }

if "cohort_records" not in st.session_state:
    st.session_state.cohort_records = {
        "STU-ELENA": {
            "name": "Elena Vance",
            "initials": "EV",
            "course_id": "CRS-01",
            "lesson_id": "LES-01",
            "lesson_title": "Lesson 1: Value Innovation & Blue Ocean Strategy",
            "mastery_pct": 100,
            "submitted": True,
            "evaluated": False,
            "submitted_at": "Yesterday at 17:30 CET",
            "hash": "NEAM-BSCL-ELENA-4871-SHA256",
            "answer_text": (
                "Creative agencies must transition from hourly retainer gatekeeping to an internal venture incubator. "
                "By eliminating billable-hour timesheets and raising equity-aligned co-creation, firms unlock non-consuming "
                "growth startups without traditional margin erosion."
            ),
            "attachments": [],
            "voice_notes": [
                {
                    "label": "Voice Note 01 (1m 02s)",
                    "time": "Yesterday at 16:50 CET",
                    "transcript": "Large agencies fail because internal systems reward sustaining work for safe retainers. We need an autonomous unit incentivized on disruptive footholds.",
                }
            ],
            "sparring_dialogue": [
                {
                    "role": "model",
                    "time": "17:05",
                    "content": "How does your proposed venture incubator avoid cannibalizing the agency's cash-cow retainer accounts?",
                },
                {
                    "role": "user",
                    "time": "17:15",
                    "content": "It operates on asymmetric motivation: targeting non-consumers and seed-stage startups that legacy retainers reject as too small.",
                },
            ],
            "rubric": {
                "problem_clarification": 5.0,
                "theoretical_grounding": 3.4,
                "strategic_defensibility": 4.8,
                "feedback": "",
            },
        },
        "STU-MARCUS": {
            "name": "Marcus Sterling",
            "initials": "MS",
            "course_id": "CRS-01",
            "lesson_id": "LES-01",
            "lesson_title": "Lesson 1: Value Innovation & Blue Ocean Strategy",
            "mastery_pct": 65,
            "submitted": False,
            "evaluated": False,
            "submitted_at": "In Progress",
            "hash": "NEAM-BSCL-MARCUS-9104-SHA256",
            "answer_text": "Drafting initial ERRC matrix for mid-market industrial logistics...",
            "attachments": [],
            "voice_notes": [],
            "sparring_dialogue": [
                {
                    "role": "model",
                    "time": "09:40",
                    "content": "Which specific cost factor are you eliminating that competitors treat as non-negotiable?",
                }
            ],
            "rubric": {
                "problem_clarification": 3.5,
                "theoretical_grounding": 3.5,
                "strategic_defensibility": 3.5,
                "feedback": "",
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

# Per-material caches so each single material has its own dedicated Podcast & Slide Deck
if "material_podcast_cache" not in st.session_state:
    st.session_state.material_podcast_cache = {}  # {material_id: {"bytes": ..., "script": ..., "warning": ...}}

if "material_slides_cache" not in st.session_state:
    st.session_state.material_slides_cache = {}  # {material_id: list_of_slides}

# ---------------------------------------------------------
# Sidebar: Engine Gateway
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

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------
def extract_pdf_text(file_bytes: bytes) -> str:
    if not HAS_PYPDF:
        return ""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = [page.extract_text() or "" for page in reader.pages[:20]]
        return "\n".join(pages).strip()
    except Exception:
        return ""


def get_lesson_materials(course: dict, lesson_id: str) -> List[Dict]:
    mats = [m for m in course.get("materials_repo", []) if lesson_id in m.get("assigned_lessons", [])]
    return sorted(mats, key=lambda x: x["title"].lower())


def compute_lesson_mastery(course: dict, lesson_id: str) -> Tuple[int, str]:
    lesson_mats = get_lesson_materials(course, lesson_id)
    total_mats = max(len(lesson_mats), 1)
    reviewed_count = len([m for m in lesson_mats if m["id"] in st.session_state.reviewed_materials.get(lesson_id, set())])
    mat_score = (reviewed_count / total_mats) * 50.0

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
    color = "#059669" if total == 100 else ("#0284c7" if total >= 50 else "#0ea5e9")
    return total, color


def format_single_material_context(mat: dict) -> str:
    extra = f" (YouTube Link: {mat['youtube_url']})" if mat.get("youtube_url") else ""
    return f"MATERIAL TITLE: {mat['title']} ({mat.get('type', 'Reading')}){extra}\nCONTENT:\n{mat.get('text', '')}"


def cluster_lesson_materials(materials: List[Dict]) -> str:
    if not materials:
        return "No materials currently assigned to this lesson."
    blocks = []
    for idx, m in enumerate(materials, start=1):
        extra = f" (YouTube Link: {m['youtube_url']})" if m.get("youtube_url") else ""
        blocks.append(f"[Material {idx}: {m['title']} ({m['type']}){extra}]\n{m['text']}")
    return "\n\n".join(blocks)


def sync_lucas_to_cohort(course_id: str, lesson_id: str):
    course = st.session_state.courses[course_id]
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

    existing = st.session_state.cohort_records.get("STU-LUCAS", {})
    prev_rubric = existing.get(
        "rubric",
        {"problem_clarification": 4.5, "theoretical_grounding": 4.5, "strategic_defensibility": 4.5, "feedback": ""},
    )

    st.session_state.cohort_records["STU-LUCAS"] = {
        "name": st.session_state.student_profile["name"],
        "initials": "LG",
        "course_id": course_id,
        "lesson_id": lesson_id,
        "lesson_title": lesson["title"],
        "mastery_pct": pct,
        "submitted": bool(ans.get("submitted", False)),
        "evaluated": bool(ans.get("evaluated", False)),
        "submitted_at": ans.get("submitted_at", "Live Session"),
        "hash": "NEAM-BSCL-LUCAS-7729-SHA256",
        "answer_text": ans.get("text", ""),
        "attachments": ans.get("attachments", []),
        "voice_notes": [],
        "sparring_dialogue": sparring_turns,
        "rubric": prev_rubric,
    }


def generate_micro_sprints_ai(task_text: str, context_text: str, api_key: str) -> List[Dict]:
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
Context: {context_text[:1200]}
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


def generate_single_material_slides_ai(mat: dict, api_key: str) -> List[Dict]:
    """Transforms ONLY the single selected material into a scannable visual slide deck."""
    mat_context = format_single_material_context(mat)
    sentences = [s.strip() for s in mat.get("text", "").split(".") if len(s.strip()) > 12]
    fallback_slides = [
        {
            "pillar": mat.get("type", "CORE MATERIAL").upper(),
            "title": mat["title"],
            "takeaway": sentences[0] + "." if sentences else mat["title"],
            "bullets": [s + "." for s in sentences[1:3]] or ["Review the full material text or download the source file."],
            "question": f"How does '{mat['title']}' directly apply to your strategic thesis?",
        }
    ]
    if not api_key:
        return fallback_slides

    prompt = f"""
Convert ONLY this single course material into 3 high-impact, scannable executive slides.
Do not include outside topics—focus strictly on this specific document.
Return ONLY lines in this exact pipe-delimited format (one slide per line):
PILLAR | SLIDE TITLE | CORE TAKEAWAY | BULLET 1; BULLET 2 | SPARRING QUESTION

{mat_context[:2800]}
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


def generate_single_material_podcast(
    mat: dict,
    gemini_key: str,
    eleven_key: str,
    progress_fn=None,
) -> Dict:
    """Transforms ONLY the single selected material into a dual-voice podcast."""
    if progress_fn:
        progress_fn(f"Drafting dialogue exclusively from '{mat['title']}'...")

    mat_context = format_single_material_context(mat)
    script_prompt = f"""
Convert ONLY this single Steinbeis course material into a punchy 4-line executive podcast dialogue between Host_A and Host_B.
Host_A frames the practical question raised by this specific document. Host_B explains the exact insight from this document.
Keep each line under 28 words. Output ONLY 4 lines in this exact format:
Host_A | [Line 1]
Host_B | [Line 2]
Host_A | [Line 3]
Host_B | [Line 4]

{mat_context[:2600]}
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
        sentences = [s.strip() for s in mat.get("text", "").split(".") if len(s.strip()) > 12]
        script = [
            {"speaker": "Host_A", "text": f"Let's examine the core thesis of {mat['title']}."},
            {"speaker": "Host_B", "text": (sentences[0] + ".") if sentences else mat["title"]},
            {"speaker": "Host_A", "text": "And what is the practical takeaway for executive leaders?"},
            {"speaker": "Host_B", "text": (sentences[1] + ".") if len(sentences) > 1 else "Apply this framework directly to eliminate strategic friction."},
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
1. CLOSED-LOOP GROUNDING: Base every argument strictly on the lesson materials provided below.
2. ANTI-GHOSTWRITING: Never write the student's final answer or essay for them. Challenge weak assumptions, test logic against the lesson frameworks, and ask sharp dialectic questions.
3. COGNITIVE CALIBRATION: Tone = {intensity}. Keep replies concise (under 140 words) with clear bullet points or bold key concepts for executive scannability.

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
                    Autonomous cognitive calibration, single-material multimodal transformation, micro-sprints, and Socratic sparring.
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
                    Manage courses, upload PDF/Video/YouTube materials, and evaluate student Proof-of-Work dossiers.
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
    # 2A. FIRST-TIME AUTONOMOUS CALIBRATION GATE
    # -----------------------------------------------------
    if not profile["onboarded"]:
        if st.button("← Back to Landing", key="back_cal_landing"):
            st.session_state.current_role = None
            st.rerun()

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

    # -----------------------------------------------------
    # 2B. STUDENT COURSE & SYLLABUS HOME
    # -----------------------------------------------------
    elif st.session_state.selected_lesson_id is None:
        nav_back, _ = st.columns([1.4, 6])
        with nav_back:
            if st.button("← Back to Landing", key="back_stu_landing", use_container_width=True):
                st.session_state.current_role = None
                st.rerun()

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

        course_ids = list(st.session_state.courses.keys())
        selected_c_id = st.selectbox(
            "Enrolled MBA Course:",
            options=course_ids,
            index=course_ids.index(st.session_state.selected_student_course_id),
            format_func=lambda cid: f"{st.session_state.courses[cid]['code']} — {st.session_state.courses[cid]['course_name']}",
        )
        st.session_state.selected_student_course_id = selected_c_id
        course = st.session_state.courses[selected_c_id]

        st.markdown(f"<span class='badge-green'>Active MBA Syllabus</span>", unsafe_allow_html=True)
        st.markdown(f"## {course['course_name']}")
        st.caption(f"Faculty Lead: **{st.session_state.professor_profile['name']}** • Select a syllabus lesson below:")
        st.write("")

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
                        f"Closed-loop sparring locked to **{lesson['title']}**. "
                        "Inspect individual materials on the left, then test your thesis premise here before submitting."
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

        # Optional Expanded Full-Window Document/PDF/Video Reader Banner
        if st.session_state.open_full_reader_mat_id:
            open_mat = next((m for m in materials if m["id"] == st.session_state.open_full_reader_mat_id), None)
            if open_mat:
                with st.container(border=True):
                    fr_h1, fr_h2 = st.columns([5, 1])
                    with fr_h1:
                        st.markdown(f"### 📖 Full Material Viewer: {open_mat['title']}")
                        st.caption(f"Format: **{open_mat.get('type', 'Reading')}**")
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
                        pdf_iframe = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="520" type="application/pdf" style="border:1px solid #cbd5e1; border-radius:8px;"></iframe>'
                        st.components.v1.html(pdf_iframe, height=535)
                        if open_mat.get("text"):
                            with st.expander("View Extracted Text"):
                                st.write(open_mat["text"])
                    else:
                        st.markdown(
                            f"""
                            <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:20px; font-size:1rem; line-height:1.6;">
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
            st.caption("Choose **one** material below to inspect, open, download, or transform into a podcast/slide deck:")

            if not materials:
                st.info("No materials assigned to this lesson yet.")
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
                    return f"{done_mark}{t_icon} {m_obj['title']}"

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

                # Active Single Material Inspector Card
                st.markdown(
                    f"""
                    <div class="material-viewer-card">
                        <span class="badge-blue">Selected Material • {selected_mat.get('type', 'Reading')}</span>
                        <h4 style="margin:4px 0 6px 0;">{selected_mat['title']}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Preview inside card
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

                # Action Row: Open Full Window | Download | Mark Reviewed
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
                # STEP 2: TRANSFORM ONLY THIS SELECTED MATERIAL
                # -------------------------------------------------
                st.markdown("#### 2️⃣ Transform Selected Material Only")
                st.caption(f"Generates output exclusively from: **{selected_mat['title']}**")

                transform_mode = st.radio(
                    "Sensory Channel",
                    ["🎧 Dual-Voice Podcast", "📊 Visual Slide Deck"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"tmode_{l_id}",
                )

                if transform_mode == "🎧 Dual-Voice Podcast":
                    if st.button("Synthesize Podcast for This Material", type="primary", use_container_width=True, key=f"btn_pod_{chosen_mat_id}"):
                        prog = st.empty()
                        res = generate_single_material_podcast(
                            mat=selected_mat,
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
                    if st.button("Generate Slides for This Material", type="primary", use_container_width=True, key=f"btn_sld_{chosen_mat_id}"):
                        with st.spinner(f"Distilling '{selected_mat['title']}' into visual slides..."):
                            st.session_state.material_slides_cache[chosen_mat_id] = generate_single_material_slides_ai(
                                selected_mat, GOOGLE_API_KEY
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

        # -------------------------------------------------
        # RIGHT WORKSPACE: TASK + ANSWER + SPARRING
        # -------------------------------------------------
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
                        sync_lucas_to_cohort(c_id, l_id)
                        st.rerun()

            st.markdown(
                """
                <div class="workspace-box-green">
                    <span class="badge-green">2 • Lesson Answer Space & Deliverable Upload</span>
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#334155;">
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
                    <p style="margin:2px 0 0 0; font-size:0.88rem; color:#334155;">
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

        st.markdown("<span class='badge-green'>Professor Workspace</span>", unsafe_allow_html=True)
        st.markdown(f"## {prof['name']}")
        st.caption(prof["title"])
        st.divider()

        st.subheader("Courses Taught at the University")
        st.caption("Select a course to manage PDF/Video/YouTube materials or evaluate student Proof-of-Work dossiers:")
        st.write("")

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
                st.markdown("### 📘 Course's Lessons")
                st.caption("Each lesson makes all assigned PDFs, videos, YouTube links, and readings available to students:")

                for l_id, lesson in course["lessons"].items():
                    assigned_mats = get_lesson_materials(course, l_id)
                    with st.container(border=True):
                        st.markdown(f"#### {lesson['title']}")
                        st.caption(lesson["summary"])
                        st.markdown(f"**Assigned Materials ({len(assigned_mats)}):**")
                        if assigned_mats:
                            for am in assigned_mats:
                                icon = "🎬" if "Video" in am["type"] or "YouTube" in am["type"] else ("📕" if "PDF" in am["type"] else "📄")
                                st.markdown(f"- {icon} {am['title']}")
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
                hdr_m, btn_m = st.columns([3, 1.5])
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
                            "Summary / Key Notes (Used when transforming this material into Podcast or Slides)",
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

                                if up_file is not None:
                                    fbytes = up_file.getvalue()
                                    fmimetype = up_file.type or "application/octet-stream"
                                    fname = up_file.name
                                    if new_m_type == "PDF Document":
                                        pdf_txt = extract_pdf_text(fbytes)
                                        if pdf_txt:
                                            extracted_text = (extracted_text + "\n\n" + pdf_txt).strip()
                                        elif not extracted_text:
                                            extracted_text = f"PDF Document uploaded: {fname}"
                                    elif new_m_type == "Video File" and not extracted_text:
                                        extracted_text = f"Uploaded video lecture: {fname}"
                                    elif new_m_type == "Text / Reading" and not extracted_text:
                                        extracted_text = fbytes.decode("utf-8", errors="ignore")

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
                                })
                                st.success("Material uploaded & added to repository!")
                                st.rerun()

                sorted_repo = sorted(course["materials_repo"], key=lambda x: x["title"].lower())
                lesson_ids = list(course["lessons"].keys())

                for mat in sorted_repo:
                    mtype = mat.get("type", "Text / Reading")
                    icon = "🎬" if "Video" in mtype or "YouTube" in mtype else ("📕" if "PDF" in mtype else "📄")
                    with st.container(border=True):
                        st.markdown(f"**{icon} {mat['title']}** `{mtype}`")
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
            roster_col, dossier_col = st.columns([1.15, 2.35], gap="large")

            with roster_col:
                st.markdown("### 👥 Enrolled Students")
                st.caption("Sorted alphabetically (A–Z). Highlighted names have ungraded submissions:")

                cohort_list = sorted(
                    [s for s in st.session_state.cohort_records.values() if s.get("course_id") == cid],
                    key=lambda x: x["name"].lower(),
                )
                id_by_name = {v["name"]: k for k, v in st.session_state.cohort_records.items() if v.get("course_id") == cid}

                for stu in cohort_list:
                    sid = id_by_name[stu["name"]]
                    needs_eval = stu.get("submitted") and not stu.get("evaluated")
                    is_selected = st.session_state.selected_audit_student_id == sid

                    border_color = "#f59e0b" if needs_eval else ("#0284c7" if is_selected else "#e2e8f0")
                    bg_color = "#fffbeb" if needs_eval else ("#f0f9ff" if is_selected else "#ffffff")
                    bar_col = "#059669" if stu["mastery_pct"] == 100 else "#0284c7"

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
                                    <div style="width:36px; height:36px; border-radius:50%; background:#0284c7; color:white; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.85rem;">
                                        {stu['initials']}
                                    </div>
                                    <div>
                                        <div style="font-weight:700; color:#0f172a; font-size:0.95rem;">{stu['name']}</div>
                                        <div style="font-size:0.75rem; color:#475569;">Mastery: {stu['mastery_pct']}%</div>
                                    </div>
                                </div>
                                {status_badge}
                            </div>
                            <div style="width:100%; height:8px; background:#e2e8f0; border-radius:9999px; overflow:hidden; margin-top:8px;">
                                <div style="width:{stu['mastery_pct']}%; height:100%; background:{bar_col};"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button(f"Inspect {stu['name'].split()[0]}'s Dossier →", key=f"sel_stu_{sid}", use_container_width=True):
                        st.session_state.selected_audit_student_id = sid
                        st.rerun()

            with dossier_col:
                active_sid = st.session_state.selected_audit_student_id
                if active_sid not in st.session_state.cohort_records:
                    active_sid = next(iter(st.session_state.cohort_records.keys()))
                stu = st.session_state.cohort_records[active_sid]

                dossier_md = f"""# PROOF-OF-WORK VERIFICATION • {stu['hash']}
**Candidate:** {stu['name']}
**Lesson:** {stu['lesson_title']}
**Status:** {'Submitted' if stu['submitted'] else 'In Progress'} ({stu['submitted_at']})
**Lesson Mastery:** {stu['mastery_pct']}%

## 1. Student's Final Submitted Answer
{stu['answer_text'] or '_No written answer submitted yet._'}

## 2. Recorded Voice Interactions
""" + ("\n".join([f"- **{v['label']}** ({v['time']}): \"{v['transcript']}\"" for v in stu.get("voice_notes", [])]) or "_None recorded._") + """

## 3. Complete Socratic Sparring Dialogue (Anti-Ghostwriting: 100% Student Reasoning)
""" + ("\n".join([f"- **{t['role'].upper()}** [{t['time']}]: {t['content']}" for t in stu.get("sparring_dialogue", [])]) or "_No sparring turns recorded._")

                dh1, dh2 = st.columns([3.5, 1.5])
                with dh1:
                    st.caption(f"PROOF-OF-WORK VERIFICATION • `{stu['hash']}`")
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
                        <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#475569; margin-bottom:6px;">
                            <span>1. STUDENT'S FINAL SUBMITTED ANSWER</span>
                            <span>{len(stu.get('answer_text', ''))} characters</span>
                        </div>
                        <p style="margin:0; font-size:0.95rem; color:#0f172a;">{stu.get('answer_text') or 'No answer submitted yet.'}</p>
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

                v_notes = stu.get("voice_notes", [])
                st.markdown(f"**🎙️ 2. RECORDED VOICE INTERACTIONS ({len(v_notes)} AUDIO NOTES):**")
                if v_notes:
                    for vn in v_notes:
                        st.markdown(
                            f"""
                            <div class="dossier-card" style="padding:12px 16px;">
                                <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700;">
                                    <span>{vn['label']}</span>
                                    <span style="color:#64748b;">{vn['time']}</span>
                                </div>
                                <p style="margin:4px 0 0 0; font-style:italic; color:#334155;">"{vn['transcript']}"</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No voice notes recorded in this session.")

                st.markdown("**🥊 3. COMPLETE SOCRATIC SPARRING DIALOGUE (Anti-Ghostwriting: 100% Student Reasoning):**")
                dialogue = stu.get("sparring_dialogue", [])
                if dialogue:
                    for turn in dialogue:
                        if turn["role"] == "model":
                            st.markdown(
                                f"""
                                <div class="sparring-bubble-ai">
                                    <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#0369a1;">
                                        <span>NEAM AI Sparring Partner</span>
                                        <span>{turn.get('time', '')}</span>
                                    </div>
                                    <div style="font-size:0.9rem; margin-top:4px;">{turn['content']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""
                                <div class="sparring-bubble-student">
                                    <div style="display:flex; justify-content:space-between; font-size:0.78rem; font-weight:700; color:#065f46;">
                                        <span>{stu['name']}</span>
                                        <span>{turn.get('time', '')}</span>
                                    </div>
                                    <div style="font-size:0.9rem; margin-top:4px;">{turn['content']}</div>
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
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#f0fdf4; border:1px solid #bbf7d0; padding:10px 16px; border-radius:8px; margin:8px 0;">
                        <span style="font-weight:700; color:#065f46;">⚖️ FACULTY RUBRIC GRADING CONSOLE</span>
                        <span style="font-weight:800; font-size:1.1rem; color:#059669;">Composite: {composite:.2f} / 5.0</span>
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
                    if active_sid == "STU-LUCAS":
                        lid_target = stu["lesson_id"]
                        if lid_target in st.session_state.lesson_answers:
                            st.session_state.lesson_answers[lid_target]["evaluated"] = True
                    st.success(f"Evaluation saved for {stu['name']} ({composite:.2f}/5.0). Pending highlight cleared!")
                    st.rerun()
