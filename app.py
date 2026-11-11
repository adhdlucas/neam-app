import streamlit as st
import datetime
import json
from google import genai
from google.genai import types

# ---------------------------------------------------------
# PAGE CONFIGURATION & THEME
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

    /* FIX: Force high-contrast text visibility inside all inputs */
    input, textarea, [data-testid="stChatInput"] textarea {
        color: #0f172a !important;
        background-color: #f8fafc !important;
        caret-color: #059669 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
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

# Fallback helper to safely call Gemini across supported model IDs
def safe_generate_content(prompt_text: str, system_instr: str = None, audio_part=None):
    # Try preferred flash models in sequence
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.0-flash-exp"]
    
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.7
    ) if system_instr else None

    contents = []
    if audio_part:
        contents.append(audio_part)
    contents.append(prompt_text)

    last_err = None
    for m in models_to_try:
        try:
            resp = client.models.generate_content(
                model=m,
                contents=contents,
                config=config
            )
            return resp.text
        except Exception as e:
            last_err = e
            continue
    raise last_err

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "completed": True,
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
"""
    for entry in st.session_state.audit_log:
        md += f"### `[{entry['timestamp']}]` | {entry['actor'].upper()} ({entry['event_type']})\n"
        if entry['meta']:
            md += f"*Context: {entry['meta']}*\n\n"
        md += f"{entry['content']}\n\n---\n"
    
    return md

# ---------------------------------------------------------
# SIDEBAR: DIAGNOSTIC & SPRINTS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 NEAM Core Engine")
    st.markdown("<span class='metric-badge'>Socratic Protocol Active</span>", unsafe_allow_html=True)
    st.markdown("")

    with st.expander("⚙️ Cognitive Diagnostic Profile", expanded=False):
        with st.form("onboarding_form"):
            name = st.text_input("Student Name", value=st.session_state.profile["name"])
            industry = st.text_input("Leadership / Industry Domain", value=st.session_state.profile["industry"])
            passions = st.text_area("Metaphor Anchors", value=st.session_state.profile["passions"])
            
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
            
            submitted = st.form_submit_button("Update Profile")
            if submitted:
                st.session_state.profile.update({
                    "name": name,
                    "industry": industry,
                    "passions": passions,
                    "sensory_channel": sensory,
                    "stance": stance
                })
                log_audit_entry("DIAGNOSTIC_CALIBRATION", "Student", f"Profile set for {name}")
                st.success("Profile saved.")

    st.markdown("---")
    st.markdown("#### 🎯 Socratic Sprint Progress")
    steps = [
        "1. Problem Definition & Boundary Test",
        "2. Theoretical Grounding & Stress-Test",
        "3. Defensibility & Strategic Synthesis"
    ]
    for idx, s in enumerate(steps, 1):
        if idx == st.session_state.current_sprint_step:
            st.markdown(f"**🟢 {s}** *(Active)*")
        elif idx < st.session_state.current_sprint_step:
            st.markdown(f"✅ ~~{s}~~")
        else:
            st.markdown(f"⚪ {s}")

    st.markdown("---")
    audit_md = generate_audit_markdown()
    st.download_button(
        label="📥 Download Proof-of-Work Dossier",
        data=audit_md,
        file_name=f"NEAM_Audit_{st.session_state.profile['name']}.md",
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

    # Render history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 2px;'>Beat task initiation friction with a quick voice note:</p>", unsafe_allow_html=True)
    audio_val = st.audio_input("Record audio note")
    user_prompt = st.chat_input("Type your thesis or doubt here (e.g. 'I don't understand Blue Ocean Strategy')...")

    final_input_text = None
    input_source = "Text"

    # Audio input handling
    if audio_val is not None and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_val):
        st.session_state.last_audio = audio_val
        input_source = "Voice Transcription"
        
        with st.spinner("Transcribing voice note..."):
            audio_bytes = audio_val.read()
            mime = getattr(audio_val, "type", "audio/wav") or "audio/wav"
            
            try:
                audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime)
                transcription = safe_generate_content(
                    prompt_text="Transcribe this audio recording verbatim. Return ONLY the plain transcription text.",
                    audio_part=audio_part
                )
                final_input_text = transcription.strip()
                st.info(f"🎤 **Transcribed:** *\"{final_input_text}\"*")
            except Exception as e:
                st.error(f"Voice transcription note: {e}")
                final_input_text = None

    elif user_prompt:
        final_input_text = user_prompt
        input_source = "Direct Chat"

    # Socratic reasoning execution
    if final_input_text:
        st.session_state.messages.append({"role": "user", "content": final_input_text})
        log_audit_entry("STUDENT_SPARRING_THESIS", prof['name'], final_input_text, meta=f"Source: {input_source}")

        with st.chat_message("user"):
            st.markdown(final_input_text)

        socratic_system = f"""
You are the Socratic sparring partner inside NEAM (Neurodivergent Executive AI Module), working with executive student {prof['name']}.
Academic Evaluator: Prof. Dr. Mario Vaupel (Berlin School of Creative Leadership / Steinbeis).

PEDAGOGICAL RULES:
1. ANTI-GHOSTWRITING: Never write assignments or give full summary answers. When the student says "I don't understand X", do not lecture them. Instead, break the concept into an intuitive contrast using their domain ({prof['industry']}) or passion ({prof['passions']}) and ask them ONE sharp reflective question to test their understanding.
2. COGNITIVE CHUNKING: Strictly under {prof['working_memory_limit']} words.
3. STANCE: {prof['stance']}. Direct, incisive, non-patronizing.
4. Current Sprint Stage: Step {st.session_state.current_sprint_step} of 3.
"""

        with st.chat_message("assistant"):
            with st.spinner("Analyzing reasoning..."):
                try:
                    assistant_reply = safe_generate_content(
                        prompt_text=f"Student inquiry: {final_input_text}",
                        system_instr=socratic_system
                    )
                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    log_audit_entry("SOCRATIC_CHALLENGE", "NEAM AI", assistant_reply)
                except Exception as e:
                    st.error(f"Could not reach model endpoint: {e}")

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Advance Sprint Milestone ➡️"):
                if st.session_state.current_sprint_step < 3:
                    st.session_state.current_sprint_step += 1
                    st.rerun()

# ---------------------------------------------------------
# TAB 2: MULTIMODAL EXECUTIVE STUDIO
# ---------------------------------------------------------
with tab_studio:
    prof = st.session_state.profile
    st.markdown("### 🎙️ Multimodal Strategy Translation Engine")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎧 Executive Deep-Dive Podcast Script")
        module_topic = st.text_input("Strategy Framework / Reading Topic", placeholder="e.g., Blue Ocean Strategy vs. Traditional Retailing")
        
        if st.button("Generate Audio Script", use_container_width=True) and module_topic:
            p_prompt = f"""
Generate an executive briefing script between Host A (Analytical Socratic Inquirer) and Host B (Practical Strategist).
Topic: {module_topic}
Student: {prof['name']}
Industry: {prof['industry']}
Metaphors: {prof['passions']}

Requirements:
1. Dynamic Attention Anchors: Address {prof['name']} directly 2-3 times.
2. Concrete analogies from {prof['passions']}.
3. Maximum 500 words. Format as Host A: / Host B:.
"""
            with st.spinner("Synthesizing script..."):
                try:
                    script_text = safe_generate_content(prompt_text=p_prompt)
                    st.session_state.generated_script = script_text
                except Exception as e:
                    st.error(f"Generation error: {e}")

        if "generated_script" in st.session_state:
            st.text_area("Podcast Script Output", st.session_state.generated_script, height=350)

    with col2:
        st.markdown("#### 📊 Visual Strategy Briefing Deck")
        deck_topic = st.text_input("Topic for Slide Blueprint", placeholder="e.g., Value Innovation Canvas")

        if st.button("Generate Slide Deck Architecture", use_container_width=True) and deck_topic:
            d_prompt = f"""
Generate a 6-slide executive briefing deck blueprint for {prof['name']}.
Topic: {deck_topic}
Context: {prof['industry']}
Metaphors: {prof['passions']}

For each slide, specify:
- Slide Title
- Visual Archetype (e.g. 2x2 Matrix, ERRC Grid)
- 3 Core Bullets (max 15 words each)
"""
            with st.spinner("Synthesizing deck..."):
                try:
                    deck_text = safe_generate_content(prompt_text=d_prompt)
                    st.session_state.generated_deck = deck_text
                except Exception as e:
                    st.error(f"Generation error: {e}")

        if "generated_deck" in st.session_state:
            st.markdown(st.session_state.generated_deck)
