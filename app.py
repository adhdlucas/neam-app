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

    /* Force high-contrast text visibility inside all inputs */
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
# GEMINI CLIENT INITIALIZATION (MULTI-KEY RESILIENT)
# ---------------------------------------------------------
raw_keys = st.secrets.get("GEMINI_API_KEY", "")
api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not api_keys:
    st.error("⚠️ GEMINI_API_KEY missing. Please configure it in your Streamlit Cloud Secrets.")
    st.stop()

def safe_generate_content(prompt_text: str, system_instr: str = None, audio_part=None):
    models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
    
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.7
    ) if system_instr else None

    contents = []
    if audio_part:
        contents.append(audio_part)
    contents.append(prompt_text)

    last_err = None
    for key in api_keys:
        client = genai.Client(api_key=key)
        for m in models_to_try:
            try:
                resp = client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=config
                )
                return resp.text
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                    break
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
*The entries below verify authentic human critical reasoning and thesis defense. No ghostwritten content was introduced.*

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
    st.caption(f"Profile: **{prof['name']}** | Stance: **{prof['stance']}** | Word Ceiling: **{prof['working_memory_limit']} words**")

    # Render conversation history
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
                    prompt_text="Transcribe this audio recording verbatim. Return ONLY the plain transcription text without any commentary.",
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
1. ANTI-GHOSTWRITING: Never write assignments or give direct lecture answers. When the student expresses confusion or asks about a framework, do NOT give a generic textbook summary. Instead, frame the concept using a sharp contrast drawn from {prof['industry']} or {prof['passions']}, and ask ONE direct, provocative question to force them to test the boundary of the concept themselves.
2. COGNITIVE CHUNKING: Enforce a hard ceiling strictly under {prof['working_memory_limit']} words. No walls of text.
3. STANCE: {prof['stance']}. Incisive, concise, intellectually demanding.
4. Sprint Milestone: Currently on Step {st.session_state.current_sprint_step}/3.
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
# TAB 2: MULTIMODAL EXECUTIVE STUDIO (MATERIAL-GROUNDED)
# ---------------------------------------------------------
with tab_studio:
    prof = st.session_state.profile
    st.markdown("### 🎙️ Grounded Multimodal Strategy Translation Engine")
    st.caption("Upload course literature or module readings. NEAM synthesizes personalized executive audio scripts and slide blueprints grounded directly in your material.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📄 1. Source Material Ingestion")
        uploaded_file = st.file_uploader(
            "Upload Module Reading / PDF / Notes",
            type=["pdf", "txt", "md"],
            help="Upload your Steinbeis module paper, case study, or academic chapter."
        )

        extracted_text = ""
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".pdf"):
                try:
                    import pypdf
                    reader = pypdf.PdfReader(uploaded_file)
                    for page in reader.pages:
                        extracted_text += (page.extract_text() or "") + "\n"
                    st.success(f"✅ Loaded: {uploaded_file.name} ({len(reader.pages)} pages parsed)")
                except Exception as e:
                    st.error(f"Error reading PDF: {e}")
            else:
                extracted_text = uploaded_file.read().decode("utf-8")
                st.success(f"✅ Loaded text file: {uploaded_file.name}")

            st.session_state["uploaded_material_snippet"] = extracted_text[:10000]

        st.markdown("#### 🎧 2. Executive Deep-Dive Podcast Engine")
        focus_angle = st.text_input(
            "Discussion Focus / Thesis Angle (Optional)",
            placeholder="e.g., Focus on value innovation and eliminating traditional overhead"
        )
        
        generate_podcast_btn = st.button("Generate Material-Grounded Podcast Script", use_container_width=True)

        if generate_podcast_btn:
            context_material = extracted_text[:12000] if extracted_text else st.session_state.get("uploaded_material_snippet", "")
            if not context_material:
                st.warning("⚠️ Please upload a reading or paper first so the script is grounded in verified course material.")
            else:
                podcast_prompt = f"""
You are the Executive Audio Synthesizer inside NEAM.
Generate an executive briefing podcast script between two hosts:
- Host A (Analytical Socratic Inquirer)
- Host B (Strategic Practitioner)

STRICT GROUNDING SOURCE MATERIAL:
\"\"\"
{context_material}
\"\"\"

TARGET EXECUTIVE LISTENER:
- Name: {prof['name']}
- Industry Domain: {prof['industry']}
- Creative Metaphor Anchors: {prof['passions']}
- Custom Focus: {focus_angle if focus_angle else 'Core theoretical models and strategic takeaways'}

SCRIPT RULES:
1. 100% CLOSED-LOOP GROUNDING: Draw all definitions, empirical models, and arguments directly from the provided source material.
2. DYNAMIC ATTENTION ANCHORS: Directly address {prof['name']} by name 2 to 3 times to refocus attention (e.g., "Now {prof['name']}, notice how this model breaks...").
3. EXECUTIVE METAPHORS: Demystify the dense concepts from the reading using analogies from {prof['passions']} and {prof['industry']}.
4. ADHD COGNITIVE REASSURANCE: Include one natural mid-script validation marker acknowledging non-linear strategic synthesis.
5. LENGTH: 500-650 words. Format cleanly as Host A: / Host B: dialogue.
"""
                with st.spinner("Synthesizing personalized podcast script from uploaded material..."):
                    try:
                        script_text = safe_generate_content(prompt_text=podcast_prompt)
                        st.session_state.generated_script = script_text
                        log_audit_entry(
                            "MATERIAL_PODCAST_GENERATED",
                            "NEAM Studio",
                            f"Synthesized script from {uploaded_file.name if uploaded_file else 'cached material'}"
                        )
                    except Exception as e:
                        st.error(f"Generation error: {e}")

        if "generated_script" in st.session_state:
            st.text_area("Personalized Executive Podcast Script", st.session_state.generated_script, height=350)
            st.download_button(
                "📥 Download Podcast Script (.txt)",
                data=st.session_state.generated_script,
                file_name=f"NEAM_Podcast_{prof['name']}.txt",
                mime="text/plain"
            )

    with col2:
        st.markdown("#### 📊 Visual Executive Strategy Deck")
        st.markdown("Converts the uploaded literature into a 6-to-8 slide executive architecture.")

        deck_focus = st.text_input(
            "Slide Deck Core Objective",
            placeholder="e.g., Boardroom briefing on the paper's framework"
        )

        generate_deck_btn = st.button("Generate Slide Deck Architecture", use_container_width=True)

        if generate_deck_btn:
            context_material = extracted_text[:12000] if extracted_text else st.session_state.get("uploaded_material_snippet", "")
            if not context_material:
                st.warning("⚠️ Please upload your module reading in Column 1 first.")
            else:
                deck_prompt = f"""
Generate an 8-slide executive briefing deck blueprint for {prof['name']} strictly derived from this source material:
\"\"\"
{context_material}
\"\"\"

Context: {prof['industry']} | Metaphor Anchors: {prof['passions']} | Focus: {deck_focus}

For each slide, specify:
- Slide Title
- Visual Archetype (e.g., 2x2 Matrix, Value Curve, Process Flow)
- 3 Core Takeaways (Strictly max 15 words each, directly from the text)
- Metaphorical Translation Note
"""
                with st.spinner("Distilling uploaded literature into visual slide blueprints..."):
                    try:
                        deck_text = safe_generate_content(prompt_text=deck_prompt)
                        st.session_state.generated_deck = deck_text
                        log_audit_entry("MATERIAL_DECK_GENERATED", "NEAM Studio", "Synthesized visual deck from uploaded material")
                    except Exception as e:
                        st.error(f"Generation error: {e}")

        if "generated_deck" in st.session_state:
            st.markdown(st.session_state.generated_deck)
