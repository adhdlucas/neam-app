import streamlit as st
import datetime
import json
from google import genai
from google.genai import types

# ---------------------------------------------------------
# PAGE CONFIGURATION & EMERALD EXECUTIVE THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="NEAM | Neurodivergent Executive AI Module",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    :root {
        --primary: #10b981;
        --primary-hover: #059669;
        --bg-surface: #0f172a;
        --card-bg: #1e293b;
        --text-main: #f8fafc;
        --text-muted: #94a3b8;
        --border-color: #334155;
    }
    
    .stApp {
        background-color: var(--bg-surface);
        color: var(--text-main);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    /* Executive Emerald Badges & Cards */
    .neam-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }
    
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        background-color: rgba(16, 185, 129, 0.15);
        color: var(--primary);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    /* Micro-Sprint Cards */
    .sprint-card {
        border-left: 3px solid var(--primary);
        padding-left: 14px;
        margin: 10px 0;
    }

    /* Custom Input Styling */
    div[data-testid="stChatInput"] textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 1px var(--primary) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# GEMINI CLIENT INITIALIZATION
# ---------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("⚠️ GEMINI_API_KEY missing. Please configure it in your Streamlit Cloud Secrets.")
    st.stop()

@st.cache_resource
def get_client(key: str):
    return genai.Client(api_key=key)

client = get_client(api_key)

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "completed": False,
        "name": "Lucas",
        "industry": "Creative Direction / Retail Management",
        "passions": "Cinema Production, Industrial Design, Mid-Century Architecture",
        "sensory_channel": "Auditory Podcast",
        "working_memory_limit": 150,
        "stance": "Adversarial Boardroom Critic"
    }

if "messages" not in st.session_state:
    st.session_state.messages = []

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

if "current_sprint_step" not in st.session_state:
    st.session_state.current_sprint_step = 1

# ---------------------------------------------------------
# HELPER: AUDIT LOG LEDGER
# ---------------------------------------------------------
def log_audit_entry(event_type: str, actor: str, content: str, meta: str = ""):
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.session_state.audit_log.append({
        "timestamp": timestamp,
        "event_type": event_type,
        "actor": actor,
        "content": content,
        "meta": meta
    })

def generate_audit_markdown() -> str:
    prof = st.session_state.profile
    md = f"""# NEAM: Faculty Proof-of-Work Academic Audit Dossier
**Institution:** Berlin School of Creative Leadership / Steinbeis University  
**Student Founder:** {prof['name']}  
**Industry Context:** {prof['industry']}  
**Pedagogical Protocol:** Strict Anti-Ghostwriting & Socratic Grounding  
**Evaluator Reference:** Prof. Dr. Mario Vaupel  
**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  

---

## 1. Executive Cognitive Diagnostic Profile
- **Primary Sensory Channel:** {prof['sensory_channel']}
- **Reasoning Stance:** {prof['stance']}
- **Chunking Threshold:** <{prof['working_memory_limit']} words
- **Metaphorical Anchors:** {prof['passions']}

---

## 2. Chronological Socratic Reasoning Ledger
*The entries below verify authentic, human-driven critical inquiry and iterative conceptual defense. NEAM acts as an intellectual challenger; no ghostwritten content is introduced.*

"""
    for entry in st.session_state.audit_log:
        md += f"### `[{entry['timestamp']}]` | {entry['actor'].upper()} ({entry['event_type']})\n"
        if entry['meta']:
            md += f"*Context: {entry['meta']}*\n\n"
        md += f"{entry['content']}\n\n---\n"
    
    return md

# ---------------------------------------------------------
# SIDEBAR: DIAGNOSTIC ONBOARDING & MICRO-SPRINT TRACKER
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 NEAM Core Engine")
    st.markdown("<span class='metric-badge'>Socratic Protocol Active</span>", unsafe_allow_html=True)
    st.markdown("")

    with st.expander("⚙️ Cognitive Diagnostic Profile", expanded=not st.session_state.profile["completed"]):
        with st.form("onboarding_form"):
            name = st.text_input("Student Name", value=st.session_state.profile["name"])
            industry = st.text_input("Leadership / Industry Domain", value=st.session_state.profile["industry"])
            passions = st.text_area("Metaphor Anchors (Passions / Creative Tropes)", value=st.session_state.profile["passions"])
            
            sensory = st.selectbox(
                "Primary Sensory Absorption",
                ["Auditory Podcast", "Visual Slide Deck", "Live Socratic Sparring"],
                index=0
            )
            
            stance = st.selectbox(
                "Sparring Adversary Stance",
                ["Adversarial Boardroom Critic", "Supportive Executive Mentor"],
                index=0
            )
            
            submitted = st.form_submit_button("Lock Cognitive Profile")
            if submitted:
                st.session_state.profile.update({
                    "completed": True,
                    "name": name,
                    "industry": industry,
                    "passions": passions,
                    "sensory_channel": sensory,
                    "stance": stance
                })
                log_audit_entry("DIAGNOSTIC_CALIBRATION", "Student", f"Profile locked for {name}. Focus: {industry}")
                st.success("Cognitive frame initialized.")

    st.markdown("---")
    st.markdown("#### 🎯 Socratic Sprint Progress")
    steps = [
        "1. Problem Definition & Boundary Test",
        "2. Theoretical Grounding & Stress-Test",
        "3. Defensibility & Strategic Synthesis"
    ]
    for idx, s in enumerate(steps, 1):
        if idx == st.session_state.current_sprint_step:
            st.markdown(f"**🟢 {s}** *(Active Focus)*")
        elif idx < st.session_state.current_sprint_step:
            st.markdown(f"✅ ~~{s}~~")
        else:
            st.markdown(f"⚪ {s}")

    st.markdown("---")
    
    # Audit Dossier Export
    audit_md = generate_audit_markdown()
    st.download_button(
        label="📥 Download Proof-of-Work Dossier",
        data=audit_md,
        file_name=f"NEAM_Audit_Proof_of_Work_{st.session_state.profile['name']}.md",
        mime="text/markdown"
    )

# ---------------------------------------------------------
# MAIN WORKSPACE TABS
# ---------------------------------------------------------
tab_sparring, tab_studio = st.tabs(["⚡ Socratic Sparring Room", "🎙️ Multimodal Executive Studio"])

# ---------------------------------------------------------
# TAB 1: SOCRATIC SPARRING ROOM
# ---------------------------------------------------------
with tab_sparring:
    prof = st.session_state.profile

    st.markdown(f"### Socratic Sparring Partner: Step {st.session_state.current_sprint_step}/3")
    st.caption(f"Profile: **{prof['name']}** | Stance: **{prof['stance']}** | Strict Word Ceiling: **{prof['working_memory_limit']} words**")

    # Render previous exchanges
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Dual Input Modality: Audio voice note or text
    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 2px;'>Beat task initiation friction with a quick voice note:</p>", unsafe_allow_html=True)
    audio_val = st.audio_input("Record audio note")
    user_prompt = st.chat_input("State your strategic thesis or challenge...")

    final_input_text = None
    input_source = "Text"

    if audio_val is not None and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_val):
        st.session_state.last_audio = audio_val
        input_source = "Voice Transcription"
        
        # Audio transcription via Gemini 2.0 Flash
        with st.spinner("Transcribing voice thesis..."):
            audio_bytes = audio_val.read()
            mime = getattr(audio_val, "type", "audio/wav") or "audio/wav"
            
            try:
                audio_part = types.Part.from_bytes(
                    data=audio_bytes,
                    mime_type=mime
                )
                transcription_resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[audio_part, "Transcribe this student note verbatim. Return strictly the transcription without preamble."]
                )
                final_input_text = transcription_resp.text.strip()
                st.info(f"🎤 **Transcribed:** *\"{final_input_text}\"*")
            except Exception as e:
                st.error(f"Transcription error: {e}")
                final_input_text = None

    elif user_prompt:
        final_input_text = user_prompt
        input_source = "Direct Chat"

    # Process prompt against Socratic engine
    if final_input_text:
        st.session_state.messages.append({"role": "user", "content": final_input_text})
        log_audit_entry("STUDENT_SPARRING_THESIS", prof['name'], final_input_text, meta=f"Source: {input_source}")

        with st.chat_message("user"):
            st.markdown(final_input_text)

        # Build Socratic System Prompt
        system_instruction = f"""
You are the Socratic Co-Pilot inside NEAM (Neurodivergent Executive AI Module), serving student founder {prof['name']}.
Audience: Executive MBA at Berlin School of Creative Leadership (Steinbeis), evaluated by Prof. Dr. Mario Vaupel.

CRITICAL OPERATIONAL RULES:
1. ANTI-GHOSTWRITING ABSOLUTE: Never draft essays, solutions, or executive assignments. Refuse any direct request to "write this for me." Instead, dissect the user's premise, identify logical blindspots, and demand justification.
2. CHUNKED COGNITIVE LOAD: Enforce hard working-memory limits. Keep your output under {prof['working_memory_limit']} words. No walls of text. Use sharp, bulleted questions.
3. PERSONALIZED PEDAGOGY: Use metaphors rooted in {prof['passions']} and the leadership reality of {prof['industry']}.
4. STANCE: Act as a {prof['stance']}. Call out weak empirical grounding or superficial corporate jargon.
5. SPRINT ADVANCEMENT: The student is on Sprint Stage {st.session_state.current_sprint_step}/3. Once their reasoning on this step is sound, explicitly instruct them to advance to the next milestone.
"""

        with st.chat_message("assistant"):
            with st.spinner("Deconstructing thesis..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[
                        types.Content(
                            role="user",
                            parts=[types.Part.from_text(text=f"System Instruction:\n{system_instruction}\n\nStudent Input:\n{final_input_text}")]
                        )
                    ]
                )
                assistant_reply = response.text
                st.markdown(assistant_reply)

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        log_audit_entry("SOCRATIC_CHALLENGE", "NEAM AI", assistant_reply, meta=f"Stance: {prof['stance']}")

        # Interactive Stage Progression Trigger
        col_sprint_a, col_sprint_b = st.columns([3, 1])
        with col_sprint_b:
            if st.button("Mark Step Complete ➡️"):
                if st.session_state.current_sprint_step < 3:
                    st.session_state.current_sprint_step += 1
                    log_audit_entry("SPRINT_PROGRESSION", "System", f"Advanced to Sprint Step {st.session_state.current_sprint_step}")
                    st.rerun()

# ---------------------------------------------------------
# TAB 2: MULTIMODAL EXECUTIVE STUDIO
# ---------------------------------------------------------
with tab_studio:
    prof = st.session_state.profile
    st.markdown("### 🎙️ Multimodal Strategy Translation Engine")
    st.caption("Converts dense theoretical literature and strategy frameworks into tailored cognitive formats.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎧 Executive Deep-Dive Podcast Script")
        st.markdown("Generates a two-host dialectic breakdown featuring real-time attention anchors and domain metaphors.")

        module_topic = st.text_input(
            "Strategy Framework / Reading Topic",
            placeholder="e.g., Kim & Mauborgne's ERRC Grid applied to Omnichannel Retail"
        )
        
        generate_podcast_btn = st.button("Generate Tailored Audio Script", use_container_width=True)

        if generate_podcast_btn and module_topic:
            podcast_prompt = f"""
Generate an executive briefing podcast script between two hosts: Host A (Analytical Socratic Inquirer) and Host B (Practical Strategist).
Topic: {module_topic}

TARGET EXECUTIVE:
- Name: {prof['name']}
- Domain: {prof['industry']}
- Creative Tropes & Anchors: {prof['passions']}

SCRIPT REQUIREMENTS:
1. Dynamic Attention Anchors: Explicitly call out {prof['name']} by name 2-3 times to refocus attention (e.g., 'Now Lucas, notice the inflection point here...').
2. Personalized Metaphor Translation: Demystify the theoretical framework using clear analogies from {prof['passions']}.
3. Reassurance & Cognitive Validation: Include one short mid-script check-in validating non-linear executive thinking.
4. Total runtime should read in under 4 minutes (approx. 500-600 words).
Format as Host A: / Host B: dialogue.
"""
            with st.spinner("Synthesizing script with dynamic cognitive anchors..."):
                script_resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=podcast_prompt
                )
                script_text = script_resp.text
                st.session_state.generated_script = script_text
                log_audit_entry("PODCAST_SCRIPT_GENERATED", "NEAM Studio", f"Generated personalized script for topic: {module_topic}")

        if "generated_script" in st.session_state:
            st.text_area("Podcast Script Output", st.session_state.generated_script, height=350)

    with col2:
        st.markdown("#### 📊 Visual Strategy Briefing Deck")
        st.markdown("Transforms dense readings into an 8-slide structured strategic breakdown.")

        deck_topic = st.text_input(
            "Executive Topic for Slide Blueprint",
            placeholder="e.g., Christensen's Disruptive Innovation in Premium Consumer Experiences"
        )

        generate_deck_btn = st.button("Generate Slide Deck Architecture", use_container_width=True)

        if generate_deck_btn and deck_topic:
            deck_prompt = f"""
Generate an 8-slide executive briefing deck blueprint for {prof['name']}.
Topic: {deck_topic}
Domain Context: {prof['industry']}

For each slide, specify:
- Slide Title
- Visual Matrix / Layout Archetype (e.g., 2x2 Matrix, ERRC Grid, Value Chain Flow)
- 3 Core Bullet Points (Max 15 words each)
- Metaphorical Anchor drawn from {prof['passions']}

Format with clear Markdown headers for Slide 1 through Slide 8.
"""
            with st.spinner("Synthesizing executive visual deck..."):
                deck_resp = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=deck_prompt
                )
                deck_text = deck_resp.text
                st.session_state.generated_deck = deck_text
                log_audit_entry("VISUAL_DECK_GENERATED", "NEAM Studio", f"Generated visual deck for topic: {deck_topic}")

        if "generated_deck" in st.session_state:
            st.markdown(st.session_state.generated_deck)
