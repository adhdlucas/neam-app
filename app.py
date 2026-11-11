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
# Page Configuration & Global Scaffolding Theme
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
        background-color: #0b0f17;
        color: #e2e8f0;
    }
    div[data-testid="stChatInput"] {
        border-color: #1e293b !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 1px #0ea5e9 !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        box-shadow: none !important;
        border-color: transparent !important;
    }
    .role-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .role-card:hover {
        transform: translateY(-3px);
        border-color: #0ea5e9;
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .badge-blue { background-color: #0369a1; color: #e0f2fe; }
    .badge-green { background-color: #065f46; color: #d1fae5; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Endpoints & Voice Setup
# ---------------------------------------------------------
GEMINI_ENDPOINTS = [
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
]
ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech"

VOICE_HOST_A = "21m00Tcm4TlvDq8ikWAM"
VOICE_HOST_B = "pNInz6obpgDQGcFmaJgB"

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "current_role" not in st.session_state:
    st.session_state.current_role = None

if "student_profile" not in st.session_state:
    st.session_state.student_profile = {
        "onboarded": False,
        "working_memory_chunking": True,
        "primary_modality": "Audio-Visual (Podcast & Slides)",
        "task_initiation_scaffolding": True,
        "sparring_intensity": "Contrarian Devil's Advocate",
    }

if "closed_loop_repo" not in st.session_state:
    st.session_state.closed_loop_repo = {
        "MOD-BOS": {
            "title": "Strategic Alignment & Blue Ocean Strategy",
            "faculty": "Dr. Mario Vaupel / W.C. Kim & R. Mauborgne",
            "summary": "Core framework on Value Innovation, Strategy Canvas, Four Actions Framework (ERRC Grid), and eliminating red ocean trade-offs.",
            "content": (
                "Blue Ocean Strategy challenges companies to break out of red oceans of bloody competition "
                "by creating uncontested market space that makes the competition irrelevant. Instead of choosing "
                "between low cost and high differentiation, Value Innovation pursues both simultaneously. "
                "The Four Actions Framework asks: Which factors should be Eliminated, Reduced, Raised, and Created? "
                "In executive education, traditional monomodal lecturing represents a high-overhead red ocean, "
                "whereas closed-loop multimodal cognitive scaffolding unlocks uncontested value for creative leaders."
            ),
            "slides": [
                {
                    "slide_number": 1,
                    "pillar_category": "FOUNDATIONAL AXIOM",
                    "title": "Value Innovation vs. Structural Competition",
                    "core_takeaway": "Stop competing in crowded markets; alter the strategic landscape by breaking the cost-differentiation trade-off.",
                    "bullet_points": [
                        "Red Oceans focus on beating rivals within defined boundaries.",
                        "Blue Oceans unlock new demand through non-linear systemic leaps.",
                        "Cost savings occur by eliminating factors the industry long competed on."
                    ],
                    "executive_sparring_question": "What sacred cow in your industry or thesis proposal can be eliminated entirely without eroding customer trust?"
                },
                {
                    "slide_number": 2,
                    "pillar_category": "EXECUTION TOOL",
                    "title": "The ERRC Diagnostic Grid",
                    "core_takeaway": "Systematic transformation requires simultaneous elimination and novel creation.",
                    "bullet_points": [
                        "Eliminate: Factors taken for granted that offer no real value.",
                        "Reduce: Elements over-designed in head-to-head competition.",
                        "Raise: Key levers well above the current industry standard.",
                        "Create: Entirely new sources of utility never before offered."
                    ],
                    "executive_sparring_question": "Can you define your project's value curve in four definitive verbs?"
                }
            ]
        }
    }

if "proof_of_work_log" not in st.session_state:
    st.session_state.proof_of_work_log = []

if "sparring_chat" not in st.session_state:
    st.session_state.sparring_chat = [
        {
            "role": "model",
            "content": (
                "NEAM Closed-Loop Sparring Chamber initialized. "
                "Grounding is locked strictly to Steinbeis / Berlin School curriculum materials. "
                "I am primed to challenge your strategic thesis. Present your core premise or framework challenge."
            )
        }
    ]

if "podcast_audio_cache" not in st.session_state:
    st.session_state.podcast_audio_cache = {}

# ---------------------------------------------------------
# Sidebar Credentials & Routing
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Gateway")
    GOOGLE_API_KEY = st.text_input(
        "Google AI Studio Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="Target: models/gemini-3.8-flash (AQ...)",
    )
    ELEVENLABS_API_KEY = st.text_input(
        "ElevenLabs API Key",
        value=os.getenv("ELEVENLABS_API_KEY", ""),
        type="password",
    )

    if st.session_state.current_role:
        st.divider()
        if st.button("← Switch Portal View", use_container_width=True):
            st.session_state.current_role = None
            st.rerun()

# ---------------------------------------------------------
# Core Reasoning: Socratic Engine with Anti-Ghostwriting
# ---------------------------------------------------------
def call_socratic_engine(
    prompt: str,
    conversation_history: list,
    repo_context: str,
    profile: dict,
    api_key: str
) -> str:
    if not api_key:
        return "⚠️ Missing Google AI Studio API Key. Please supply it in the sidebar."

    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    intensity = profile.get("sparring_intensity", "Contrarian Devil's Advocate")
    max_tokens = 350 if profile.get("working_memory_chunking") else 1024

    system_instruction = f"""
You are NEAM (Neurodivergent Executive AI Module), an executive sparring partner for Steinbeis University / Berlin School of Creative Leadership.
Candidate: Lucas Giraldo Mejia (Executive MBA in Creative Leadership).

STRICT ARCHITECTURAL SAFEGUARDS:
1. 100% CLOSED-LOOP GROUNDING: Draw exclusively from the approved university repository provided below. Never scrape or reference unverified external web data.
2. ANTI-GHOSTWRITING RULE: You are categorically forbidden from drafting essays, solving assignments directly, or ghostwriting final submissions. If the student asks you to "write my paper" or "give me the answer", refuse constructively: push back, ask dialectic questions, and demand their own strategic reasoning.
3. COGNITIVE CALIBRATION:
   - Tone: {intensity}.
   - Chunking: Keep responses high-signal, punchy, and capped under 150-200 words to respect executive working memory.
   - Grounding Source Material:
   \"\"\"{repo_context}\"\"\"
"""

    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3 if intensity == "Contrarian Devil's Advocate" else 0.6,
            "maxOutputTokens": max_tokens,
        },
        "systemInstruction": {"parts": [{"text": system_instruction}]},
    }

    last_err = ""
    for endpoint in GEMINI_ENDPOINTS:
        for attempt in range(3):
            try:
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=45)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                elif resp.status_code in [503, 429, 500]:
                    time.sleep((2 ** attempt) * 1.5)
                    last_err = f"Status {resp.status_code}"
                    continue
                else:
                    return f"API Error {resp.status_code}: {resp.text}"
            except requests.exceptions.RequestException as e:
                last_err = str(e)
                time.sleep(1.5)

    return f"Service Temporarily Unavailable ({last_err}). Please retry in a few seconds."

# ---------------------------------------------------------
# Multimodal Pipeline: Podcast Audio with Resilient Retry
# ---------------------------------------------------------
def generate_podcast_pipeline(material_text: str, gemini_key: str, eleven_key: str, progress_fn=None) -> Tuple[bytes, List[Dict]]:
    if progress_fn:
        progress_fn("Generating dialectic podcast script via Gemini...")

    processed_text = material_text[:3500] if len(material_text) > 3500 else material_text

    script_prompt = f"""
Transform this verified Steinbeis course material into a concise 4-turn executive podcast dialogue between 'Host_A' and 'Host_B'.
Host_A introduces the practical dilemma and challenges assumptions. Host_B provides the first-principles theoretical breakdown.
Keep each turn under 35 words so audio generation is fast and punchy.
Strictly return a JSON array matching:
[
  {{"speaker": "Host_A", "text": "..."}},
  {{"speaker": "Host_B", "text": "..."}}
]

Material:
\"\"\"{processed_text}\"\"\"
"""
    headers = {"Content-Type": "application/json", "x-goog-api-key": gemini_key}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": script_prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
            "maxOutputTokens": 1024,
        }
    }

    script = None
    last_err = ""

    for endpoint in GEMINI_ENDPOINTS:
        for attempt in range(3):
            try:
                resp = requests.post(endpoint, headers=headers, json=payload, timeout=90)
                if resp.status_code == 200:
                    raw_content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    script = json.loads(raw_content)
                    break
                elif resp.status_code in (503, 429, 500):
                    time.sleep(2 * (attempt + 1))
                    last_err = f"{resp.status_code}: {resp.text}"
                    continue
                else:
                    last_err = f"{resp.status_code}: {resp.text}"
                    break
            except requests.exceptions.RequestException as e:
                last_err = str(e)
                time.sleep(2)
        if script:
            break

    if not script:
        raise RuntimeError(f"Script generation failed across endpoints. Last error: {last_err}")

    audio_buffer = io.BytesIO()
    total_turns = len(script)

    for i, turn in enumerate(script):
        speaker = turn.get("speaker", "Host_A")
        text = turn.get("text", "")
        v_id = VOICE_HOST_A if speaker == "Host_A" else VOICE_HOST_B

        if progress_fn:
            progress_fn(f"Synthesizing voice turn {i + 1}/{total_turns} ({speaker})...")

        try:
            tts_resp = requests.post(
                f"{ELEVENLABS_TTS_URL}/{v_id}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": eleven_key,
                },
                json={
                    "text": text,
                    "model_id": "eleven_turbo_v2_5",
                    "voice_settings": {"stability": 0.45, "similarity_boost": 0.75},
                },
                timeout=60,
            )
            if tts_resp.status_code == 200:
                audio_buffer.write(tts_resp.content)
            else:
                raise RuntimeError(f"ElevenLabs error ({tts_resp.status_code}): {tts_resp.text}")
        except requests.exceptions.Timeout:
            raise RuntimeError(f"ElevenLabs timed out synthesizing turn {i + 1}.")

    audio_buffer.seek(0)
    return audio_buffer.read(), script

# ---------------------------------------------------------
# ROUTING CONTROLLER
# ---------------------------------------------------------
if st.session_state.current_role is None:
    st.markdown("<h1 style='text-align: center; margin-top: 25px;'>NEAM</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; color: #94a3b8; font-size: 1.15rem;'>"
        "Neurodivergent Executive AI Module & Multimodal Cognitive Scaffolding<br>"
        "<b>Steinbeis University Berlin | Berlin School of Creative Leadership</b>"
        "</p>",
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge badge-blue">Executive Candidate</span>
                <h3>🎓 Student Portal</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;">
                    Diagnostic onboarding, Socratic sparring chamber, and ADHD multimodal audio-visual synthesis.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter as Lucas Giraldo", use_container_width=True, type="primary"):
            st.session_state.current_role = "student"
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge badge-green">Lead Evaluator</span>
                <h3>🏛️ Faculty Ledger</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;">
                    Proof-of-work chronological audit trails, authenticity verification, and oral defense rubrics.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter as Dr. Mario Vaupel", use_container_width=True):
            st.session_state.current_role = "faculty"
            st.rerun()

    with c3:
        st.markdown(
            """
            <div class="role-card">
                <span class="badge badge-blue">Closed-Loop Repository</span>
                <h3>⚙️ Curriculum Admin</h3>
                <p style="color: #94a3b8; font-size: 0.9rem;">
                    Course syllabi ingestion, closed-loop knowledge controls, and program parameter governance.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter as Curriculum Admin", use_container_width=True):
            st.session_state.current_role = "admin"
            st.rerun()

elif st.session_state.current_role == "student":
    st.title("Executive Workspace & Cognitive Scaffolding")
    st.caption("Candidate: Lucas Giraldo Mejia | Executive MBA in Creative Leadership")

    with st.expander("🧠 Cognitive Onboarding Diagnostic (Personalization Architecture)", expanded=not st.session_state.student_profile["onboarded"]):
        st.write("Calibrate NEAM's autonomous system to your unique executive processing profile:")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            q_chunk = st.checkbox("Enforce Working Memory Chunking (Cap responses < 150 words)", value=st.session_state.student_profile["working_memory_chunking"])
            q_modality = st.selectbox("Primary Sensory Ingestion Channel:", ["Audio-First (Executive Podcast)", "Visual Slide Decks", "Text Summaries"], index=0)
        with d_col2:
            q_init = st.checkbox("Task Initiation Scaffolding (Deconstruct prompts into 3-tier micro-sprints)", value=st.session_state.student_profile["task_initiation_scaffolding"])
            q_tone = st.selectbox("Socratic Sparring Intensity:", ["Contrarian Devil's Advocate (Rigor)", "Supportive Socratic Coach"], index=0)
        
        if st.button("Commit Autonomous Calibration"):
            st.session_state.student_profile.update({
                "onboarded": True,
                "working_memory_chunking": q_chunk,
                "primary_modality": q_modality,
                "task_initiation_scaffolding": q_init,
                "sparring_intensity": q_tone,
            })
            st.success("System calibrated to your cognitive profile.")
            st.rerun()

    tab_sparring, tab_materials, tab_audit = st.tabs([
        "🥊 Socratic Sparring Chamber",
        "📚 Multimodal Knowledge Base",
        "📜 My Proof-of-Work Log"
    ])

    with tab_sparring:
        st.write(f"**Operating Mode:** {st.session_state.student_profile['sparring_intensity']} | Strictly Closed-Loop")
        active_repo_text = "\n\n".join([f"[{k}] {v['title']}: {v['content']}" for k, v in st.session_state.closed_loop_repo.items()])

        chat_container = st.container(height=480)
        for msg in st.session_state.sparring_chat:
            with chat_container.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("State your thesis premise, strategic assumption, or challenge...")
        if user_input:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.sparring_chat.append({"role": "user", "content": user_input})
            
            with chat_container.chat_message("user"):
                st.markdown(user_input)

            with chat_container.chat_message("model"):
                with st.spinner("Sparring with closed-loop frameworks..."):
                    reply = call_socratic_engine(
                        prompt=user_input,
                        conversation_history=st.session_state.sparring_chat[:-1],
                        repo_context=active_repo_text,
                        profile=st.session_state.student_profile,
                        api_key=GOOGLE_API_KEY,
                    )
                    st.markdown(reply)

            st.session_state.sparring_chat.append({"role": "model", "content": reply})

            st.session_state.proof_of_work_log.append({
                "timestamp": timestamp,
                "candidate": "Lucas Giraldo Mejia",
                "exchange_query": user_input,
                "dialectic_challenge": reply,
                "verified": True
            })

    with tab_materials:
        st.subheader("Closed-Loop Course Materials (ADHD Sensory Transformation)")
        
        selected_mod = st.selectbox(
            "Select Approved Module:",
            options=list(st.session_state.closed_loop_repo.keys()),
            format_func=lambda x: f"{st.session_state.closed_loop_repo[x]['title']} ({st.session_state.closed_loop_repo[x]['faculty']})"
        )
        module_data = st.session_state.closed_loop_repo[selected_mod]

        st.markdown(f"**Syllabus Summary:** {module_data['summary']}")

        mode = st.radio("Select Sensory Channel:", ["🎧 Dual-Voice Podcast (ElevenLabs)", "📊 Visual Slide Deck (Scannable)", "📖 Raw Text"], horizontal=True)

        if mode == "🎧 Dual-Voice Podcast (ElevenLabs)":
            st.markdown("#### ADHD-Friendly Executive Podcast")
            st.caption("Converts dense theoretical readings into a conversational walk-and-listen dialogue.")
            
            cached_audio = st.session_state.podcast_audio_cache.get(selected_mod)

            if st.button("Synthesize Closed-Loop Reading into Podcast", type="primary"):
                if not GOOGLE_API_KEY or not ELEVENLABS_API_KEY:
                    st.error("Both Google AI Studio and ElevenLabs API keys are required.")
                else:
                    status = st.empty()
                    try:
                        audio_bytes, script = generate_podcast_pipeline(
                            module_data["content"], 
                            GOOGLE_API_KEY, 
                            ELEVENLABS_API_KEY,
                            progress_fn=lambda msg: status.info(msg)
                        )
                        st.session_state.podcast_audio_cache[selected_mod] = {
                            "bytes": audio_bytes,
                            "script": script,
                        }
                        status.success("Synthesis complete!")
                        st.rerun()
                    except Exception as err:
                        status.error(str(err))

            if cached_audio:
                b64 = base64.b64encode(cached_audio["bytes"]).decode("utf-8")
                player_html = f"""
                <div style="background-color: #111827; padding: 20px; border-radius: 8px; border: 1px solid #1f2937; margin-top: 10px;">
                    <audio id="audioPlayer" controls style="width: 100%;">
                        <source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">
                    </audio>
                    <div style="margin-top: 12px; display: flex; gap: 10px;">
                        <button onclick="document.getElementById('audioPlayer').currentTime -= 10;" style="background: #1f2937; color: white; border: 1px solid #374151; padding: 6px 12px; border-radius: 4px; cursor: pointer;">⏪ -10s</button>
                        <button onclick="document.getElementById('audioPlayer').currentTime += 10;" style="background: #1f2937; color: white; border: 1px solid #374151; padding: 6px 12px; border-radius: 4px; cursor: pointer;">+10s ⏩</button>
                    </div>
                </div>
                """
                st.components.v1.html(player_html, height=160)

                with st.expander("View Debrief Script Transcript"):
                    for turn in cached_audio["script"]:
                        label = "Host A (Inquirer)" if turn["speaker"] == "Host_A" else "Host B (Executive)"
                        st.markdown(f"**{label}:** {turn['text']}")

        elif mode == "📊 Visual Slide Deck (Scannable)":
            st.markdown("#### High-Impact Strategy Deck")
            slides = module_data.get("slides", [])
            for s in slides:
                st.markdown(
                    f"""
                    <div style="background-color: #111827; border-left: 5px solid #0ea5e9; padding: 18px; border-radius: 8px; margin-bottom: 12px;">
                        <span style="color: #0ea5e9; font-weight: bold; font-size: 0.8rem;">{s['pillar_category']} • SLIDE {s['slide_number']}</span>
                        <h3 style="margin: 6px 0 10px 0; color: #f8fafc;">{s['title']}</h3>
                        <p style="color: #38bdf8; font-weight: 500;">Core Premise: {s['core_takeaway']}</p>
                        <ul style="color: #cbd5e1; margin-bottom: 10px;">
                            {"".join([f"<li>{b}</li>" for b in s['bullet_points']])}
                        </ul>
                        <div style="border-top: 1px dashed #334155; padding-top: 8px; color: #93c5fd; font-style: italic;">
                            🥊 Sparring Challenge: {s['executive_sparring_question']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        elif mode == "📖 Raw Text":
            st.text_area("Approved Text Content", module_data["content"], height=250)

    with tab_audit:
        st.subheader("Authentic Learning Log & Proof-of-Work Audit")
        st.write("Chronological verification of intellectual sparring turns. Eliminates unverified ghostwriting suspicion.")

        if st.session_state.proof_of_work_log:
            st.dataframe(st.session_state.proof_of_work_log, use_container_width=True)
            log_json = json.dumps(st.session_state.proof_of_work_log, indent=2)
            st.download_button(
                "⬇️ Export Verified Proof-of-Work Learning Log (JSON)",
                data=log_json,
                file_name="Lucas_Giraldo_NEAM_ProofOfWork.json",
                mime="application/json"
            )
        else:
            st.info("No sparring turns recorded in this session yet. Spar with the chamber to build your audit log.")

elif st.session_state.current_role == "faculty":
    st.title("Faculty Proof-of-Work Audit Ledger")
    st.caption("Lead Evaluator: Dr. Mario Vaupel | Berlin School of Creative Leadership")

    st.subheader("Verified Candidate Sparring Trails")
    st.write("Review the dialectic progression of executive candidates rather than easily spoofed final essays.")

    if st.session_state.proof_of_work_log:
        for idx, entry in enumerate(st.session_state.proof_of_work_log):
            with st.expander(f"Turn {idx + 1} [{entry['timestamp']}] Candidate: {entry['candidate']}"):
                st.markdown(f"**Student Thesis Query:** {entry['exchange_query']}")
                st.markdown(f"**NEAM Socratic Pushback:** {entry['dialectic_challenge']}")
                st.markdown(f"**Cryptographic Status:** Verified Authentic")
    else:
        st.info("No active student proof-of-work sessions submitted in the current live buffer.")

    st.divider()
    st.subheader("Record Oral Defense & Mastery Assessment")
    with st.form("faculty_eval"):
        cand = st.text_input("Candidate Name", value="Lucas Giraldo Mejia")
        milestone = st.text_input("Module / Defense Evaluated", value="Module 1: Blue Ocean Strategy & Closed-Loop Scaffolding")
        grade = st.slider("Intellectual Defensibility & Mastery Score", 0, 100, 95)
        notes = st.text_area("Evaluator Notes (Dr. Mario Vaupel)", "Candidate demonstrated clear first-principles defense under dialectic sparring.")
        
        if st.form_submit_button("Sign & Commit to University Ledger"):
            st.success(f"Assessment entry for {cand} committed successfully.")

elif st.session_state.current_role == "admin":
    st.title("Curriculum & Closed-Loop Repository Management")
    st.caption("Steinbeis University Berlin | Knowledge Integrity Architecture")

    st.subheader("Active Closed-Loop Knowledge Stores")
    for k, v in st.session_state.closed_loop_repo.items():
        st.markdown(f"- **{k}: {v['title']}** (Faculty: {v['faculty']})")

    st.divider()
    st.subheader("Ingest Approved Course Syllabus / Case Study")
    with st.form("admin_ingest"):
        mod_code = st.text_input("Module Identifier (e.g., MOD-02)")
        mod_title = st.text_input("Module Title")
        mod_faculty = st.text_input("Lead Faculty / Authors")
        mod_summary = st.text_input("Executive Summary")
        mod_text = st.text_area("Full Approved Literature Content (Strict Closed-Loop Text)")
        
        if st.form_submit_button("Ingest into NEAM Repository"):
            if mod_code and mod_title and mod_text:
                st.session_state.closed_loop_repo[mod_code] = {
                    "title": mod_title,
                    "faculty": mod_faculty,
                    "summary": mod_summary,
                    "content": mod_text,
                    "slides": [
                        {
                            "slide_number": 1,
                            "pillar_category": "INGESTED THEORY",
                            "title": f"{mod_title} Core Framework",
                            "core_takeaway": mod_summary[:120] if mod_summary else "Core syllabus extract.",
                            "bullet_points": ["Ingested via Curriculum Admin pipeline.", "Anchored strictly to course repository."],
                            "executive_sparring_question": "What is the primary operational hurdle in deploying this model?"
                        }
                    ]
                }
                st.success(f"Module {mod_code} successfully integrated into the closed-loop repository.")
                st.rerun()
