import os
import requests
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEAM | Executive Sparring Portal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { border-radius: 6px; font-weight: 600; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Environment & API Setup
# ---------------------------------------------------------
GOOGLE_API_KEY = st.sidebar.text_input(
    "Google GenAI API Key",
    value=os.getenv("GEMINI_API_KEY", ""),
    type="password",
    help="Starts with 'AQ...'",
)
ELEVENLABS_API_KEY = st.sidebar.text_input(
    "ElevenLabs API Key",
    value=os.getenv("ELEVENLABS_API_KEY", ""),
    type="password",
)

# ---------------------------------------------------------
# Session State Defaults
# ---------------------------------------------------------
if "sparring_chat" not in st.session_state:
    st.session_state.sparring_chat = [
        {
            "role": "model",
            "content": (
                "Welcome to the Socratic Sparring Chamber, Lucas. "
                "State your strategic hypothesis, core constraint, or creative leadership premise to begin."
            ),
        }
    ]

if "curriculum_modules" not in st.session_state:
    st.session_state.curriculum_modules = [
        {"id": "MOD-01", "name": "Creative Leadership & Systems Strategy", "status": "Active"},
        {"id": "MOD-02", "name": "Cognitive Scaffolding & Dialectical Sparring", "status": "Active"},
        {"id": "MOD-03", "name": "Advanced Physical-Digital Retail Architectures", "status": "Draft"},
    ]

if "proof_ledger" not in st.session_state:
    st.session_state.proof_ledger = [
        {
            "student": "Lucas Giraldo",
            "milestone": "Thesis Defense - Cognitive Ergonomics in Executive Sparring",
            "score": 96,
            "evaluator": "Dr. Mario Vaupel",
            "verified": True,
        }
    ]

# ---------------------------------------------------------
# API Helper Functions
# ---------------------------------------------------------
def call_gemini_flash(prompt: str, conversation_history: list, api_key: str) -> str:
    """Calls gemini-3.8-flash via the direct v1beta Generative Language REST endpoint."""
    if not api_key:
        return "Error: Missing Google AI Studio API Key."

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key,
    }

    # Format history into Gemini Contents structure
    contents = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    # Append the new user prompt
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 2048,
        },
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "You are NEAM, an executive cognitive scaffolding sparring partner for Steinbeis University's "
                        "MBA in Creative Leadership. Engage directly, challenge weak assumptions, utilize first-principles "
                        "reasoning, and avoid diplomatic fluff."
                    )
                }
            ]
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"
    except (KeyError, IndexError):
        return f"Unexpected Response Payload: {response.text}"


def trigger_elevenlabs_dual_voice(dialogue_script: str, api_key: str):
    """Stub for invoking ElevenLabs dual-voice synthesis endpoint."""
    if not api_key:
        st.warning("ElevenLabs API Key required for dual-voice synthesis.")
        return None
    # Dual-voice stitching / API request workflow
    st.info("Triggering dual-voice audio pipeline with ElevenLabs...")
    return None

# ---------------------------------------------------------
# Navigation & View Routing
# ---------------------------------------------------------
st.sidebar.title("NEAM Navigation")
role = st.sidebar.radio(
    "Select Operating Role:",
    ["Student (Lucas)", "Faculty / Evaluator (Dr. Mario Vaupel)", "Admin (Curriculum)"],
)

# ---------------------------------------------------------
# 1. Student View: Sparring Chamber & Media Player
# ---------------------------------------------------------
if role == "Student (Lucas)":
    st.title("Socratic Sparring Chamber")
    st.caption("Steinbeis University | Executive MBA Creative Leadership")

    col_chat, col_media = st.columns([3, 2], gap="large")

    with col_chat:
        st.subheader("Executive Sparring Dialogue")
        
        chat_container = st.container(height=520)
        for msg in st.session_state.sparring_chat:
            with chat_container.chat_message(msg["role"]):
                st.markdown(msg["content"])

        user_input = st.chat_input("Challenge an operational thesis or propose a strategic move...")
        if user_input:
            st.session_state.sparring_chat.append({"role": "user", "content": user_input})
            with chat_container.chat_message("user"):
                st.markdown(user_input)

            with chat_container.chat_message("model"):
                with st.spinner("Analyzing dialectic premises..."):
                    reply = call_gemini_flash(
                        prompt=user_input,
                        conversation_history=st.session_state.sparring_chat[:-1],
                        api_key=GOOGLE_API_KEY,
                    )
                    st.markdown(reply)
            st.session_state.sparring_chat.append({"role": "model", "content": reply})

    with col_media:
        st.subheader("Executive Podcast Synthesis")
        st.write("Dual-voice dialectic debrief generated via ElevenLabs.")

        # Interactive Media Player with seeking controls via embedded HTML5
        player_html = """
        <div style="background-color: #161b22; padding: 20px; border-radius: 8px; border: 1px solid #30363d;">
            <p style="font-weight: 600; color: #58a6ff; margin-bottom: 8px;">Debrief Session: Strategy & Cognition</p>
            <audio id="audioPlayer" controls style="width: 100%; outline: none;">
                <source src="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
            <div style="display: flex; gap: 10px; margin-top: 15px;">
                <button onclick="document.getElementById('audioPlayer').currentTime -= 10;" 
                        style="background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 14px; border-radius: 4px; cursor: pointer;">
                    ⏪ -10s
                </button>
                <button onclick="document.getElementById('audioPlayer').currentTime += 10;" 
                        style="background: #21262d; color: #c9d1d9; border: 1px solid #30363d; padding: 6px 14px; border-radius: 4px; cursor: pointer;">
                    +10s ⏩
                </button>
            </div>
        </div>
        """
        st.components.v1.html(player_html, height=180)

        st.divider()
        st.subheader("Generate Synthesis")
        if st.button("Synthesize Current Dialogue into Podcast"):
            last_exchanges = "\n".join(
                [f"{m['role']}: {m['content']}" for m in st.session_state.sparring_chat[-4:]]
            )
            trigger_elevenlabs_dual_voice(last_exchanges, ELEVENLABS_API_KEY)

# ---------------------------------------------------------
# 2. Faculty / Evaluator View: Dr. Mario Vaupel Ledger
# ---------------------------------------------------------
elif role == "Faculty / Evaluator (Dr. Mario Vaupel)":
    st.title("Faculty Proof-of-Work Evaluation Ledger")
    st.caption("Lead Evaluator: Dr. Mario Vaupel | Berlin School of Creative Leadership")

    st.subheader("Verified Academic Milestones")
    st.dataframe(
        st.session_state.proof_ledger,
        use_container_width=True,
        column_config={
            "score": st.column_config.ProgressColumn("Grade / Mastery", min_value=0, max_value=100),
            "verified": st.column_config.CheckboxColumn("Cryptographic Audit Verification"),
        },
    )

    st.divider()
    st.subheader("Append Milestone Assessment")
    with st.form("eval_form"):
        f_student = st.text_input("Candidate Name", value="Lucas Giraldo")
        f_milestone = st.text_input("Deliverable / Sparring Session Title")
        f_score = st.slider("Mastery Score", 0, 100, 85)
        submitted = st.form_submit_button("Record Grade to Ledger")
        
        if submitted and f_milestone:
            st.session_state.proof_ledger.append({
                "student": f_student,
                "milestone": f_milestone,
                "score": f_score,
                "evaluator": "Dr. Mario Vaupel",
                "verified": True,
            })
            st.success("Milestone committed to evaluation ledger.")
            st.rerun()

# ---------------------------------------------------------
# 3. Admin View: Curriculum Management
# ---------------------------------------------------------
elif role == "Admin (Curriculum)":
    st.title("Steinbeis Curriculum Architecture")
    st.caption("Module Lifecycle & Core Program Configurations")

    st.subheader("Active Modules")
    st.table(st.session_state.curriculum_modules)

    with st.expander("Add New Academic Module"):
        mod_id = st.text_input("Module ID (e.g., MOD-04)")
        mod_name = st.text_input("Module Title")
        mod_status = st.selectbox("Status", ["Active", "Draft", "Archived"])
        
        if st.button("Commit Module"):
            if mod_id and mod_name:
                st.session_state.curriculum_modules.append(
                    {"id": mod_id, "name": mod_name, "status": mod_status}
                )
                st.success(f"Module {mod_id} created.")
                st.rerun()
