import streamlit as st
import datetime
import os
import glob
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

    input, textarea, [data-testid="stChatInput"] textarea {
        color: #0f172a !important;
        background-color: #f8fafc !important;
        caret-color: #059669 !important;
        font-size: 1rem !important;
    }
    
    [data-testid="stChatInput"] textarea::placeholder {
        color: #64748b !important;
    }

    .library-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
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
# DOCUMENT INGESTION ENGINE
# ---------------------------------------------------------
CURRICULUM_DIR = "curriculum"
os.makedirs(CURRICULUM_DIR, exist_ok=True)

def extract_file_content(filepath: str) -> str:
    if filepath.endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(filepath)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"
    else:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

# Default starter reading if curriculum folder is initially empty
SAMPLE_READING_NAME = "Steinbeis_Core_Creative_Leadership.txt"
sample_path = os.path.join(CURRICULUM_DIR, SAMPLE_READING_NAME)
if not os.path.exists(sample_path) and len(os.listdir(CURRICULUM_DIR)) == 0:
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(
            "Steinbeis Creative Leadership Synthesis:\n"
            "Executive leadership in non-linear environments requires balancing value innovation, "
            "cognitive empathy, and organizational defensibility. Conventional top-down management "
            "often penalizes divergent problem-solving, whereas adaptive scaffolding enables creative "
            "executives to transform strategic friction into competitive differentiation."
        )

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

if "selected_curriculum_text" not in st.session_state:
    st.session_state.selected_curriculum_text = ""

if "selected_doc_name" not in st.session_state:
    st.session_state.selected_doc_name = "None"

# ---------------------------------------------------------
# AUDIT LOG HELPER
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
**Industry Domain:** {prof['industry']}  
**Evaluator Reference:** Prof. Dr. Mario Vaupel  
**Generated:** {datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}  

---

## 1. Executive Cognitive Profile
- **Sensory Mode:** {prof['sensory_channel']}
- **Reasoning Stance:** {prof['stance']}
- **Chunking Threshold:** <{prof['working_memory_limit']} words
- **Metaphorical Anchors:** {prof['passions']}
- **Active Document Analyzed:** {st.session_state.selected_doc_name}

---

## 2. Human Reasoning & Socratic Ledger
"""
    for entry in st.session_state.audit_log:
        md += f"### `[{entry['timestamp']}]` | {entry['actor'].upper()} ({entry['event_type']})\n"
        if entry['meta']:
            md += f"*Context: {entry['meta']}*\n\n"
        md += f"{entry['content']}\n\n---\n"
    return md

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🧠 NEAM Core Engine")
    st.markdown("<span class='metric-badge'>Socratic Protocol Active</span>", unsafe_allow_html=True)
    st.markdown("")

    with st.expander("⚙️ Cognitive Diagnostic Profile", expanded=False):
        with st.form("onboarding_form"):
            name = st.text_input("Student Name", value=st.session_state.profile["name"])
            industry = st.text_input("Leadership Domain", value=st.session_state.profile["industry"])
            passions = st.text_area("Metaphor Anchors", value=st.session_state.profile["passions"])
            stance = st.selectbox("Sparring Stance", ["Adversarial Boardroom Critic", "Supportive Executive Mentor"])
            
            if st.form_submit_button("Update Profile"):
                st.session_state.profile.update({
                    "name": name,
                    "industry": industry,
                    "passions": passions,
                    "stance": stance
                })
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
    st.download_button(
        label="📥 Download Proof-of-Work Dossier",
        data=generate_audit_markdown(),
        file_name=f"NEAM_Audit_{st.session_state.profile['name']}.md",
        mime="text/markdown"
    )

# ---------------------------------------------------------
# WORKSPACE TABS
# ---------------------------------------------------------
tab_library, tab_sparring, tab_studio = st.tabs([
    "📚 University Curriculum Library",
    "⚡ Socratic Sparring Room",
    "🎙️ Multimodal Executive Studio"
])

# ---------------------------------------------------------
# TAB 1: CURRICULUM LIBRARY
# ---------------------------------------------------------
with tab_library:
    st.markdown("### 📚 Berlin School of Creative Leadership Verified Curriculum")
    st.caption("Preloaded institutional readings, strategy papers, and module literature. Select a paper to instantly ground your Socratic sparring or generate a personalized executive podcast.")

    all_files = sorted(glob.glob(os.path.join(CURRICULUM_DIR, "*.*")))
    file_map = {os.path.basename(f): f for f in all_files}

    col_lib_a, col_lib_b = st.columns([1, 1])

    with col_lib_a:
        st.markdown("#### 🏛️ Select Verified Module Literature")
        if file_map:
            selected_file_name = st.selectbox("Preloaded Institutional Materials", list(file_map.keys()))
            selected_path = file_map[selected_file_name]
            
            with open(selected_path, "rb") as f_bytes:
                st.download_button(
                    label=f"📥 Download Original Document ({selected_file_name})",
                    data=f_bytes,
                    file_name=selected_file_name,
                    mime="application/pdf" if selected_file_name.endswith(".pdf") else "text/plain"
                )

            if st.button("🚀 Load into Active Workspace & Multimodal Studio", use_container_width=True):
                loaded_text = extract_file_content(selected_path)
                st.session_state.selected_curriculum_text = loaded_text
                st.session_state.selected_doc_name = selected_file_name
                log_audit_entry("LIBRARY_DOC_SELECTED", "Student", f"Loaded curriculum: {selected_file_name}")
                st.success(f"Loaded '{selected_file_name}' as active grounded source!")
        else:
            st.info("No curriculum files detected in `curriculum/` folder.")

    with col_lib_b:
        st.markdown("#### 📤 Upload External / Additional Paper")
        uploaded_doc = st.file_uploader("Bring custom case study or syllabus (PDF / TXT)", type=["pdf", "txt", "md"])
        if uploaded_doc is not None:
            # Save uploaded document into curriculum folder
            saved_dest = os.path.join(CURRICULUM_DIR, uploaded_doc.name)
            with open(saved_dest, "wb") as f_out:
                f_out.write(uploaded_doc.getbuffer())
            st.success(f"Added '{uploaded_doc.name}' to institutional repository!")
            st.session_state.selected_curriculum_text = extract_file_content(saved_dest)
            st.session_state.selected_doc_name = uploaded_doc.name
            st.rerun()

    st.markdown("---")
    st.markdown(f"**Currently Active Grounded Material:** `{st.session_state.selected_doc_name}`")
    if st.session_state.selected_curriculum_text:
        with st.expander("Preview Extracted Source Material Snippet"):
            st.text(st.session_state.selected_curriculum_text[:1200] + "...")

# ---------------------------------------------------------
# TAB 2: SOCRATIC SPARRING ROOM
# ---------------------------------------------------------
with tab_sparring:
    prof = st.session_state.profile
    st.markdown(f"### Socratic Sparring Partner: Step {st.session_state.current_sprint_step}/3")
    st.caption(f"Profile: **{prof['name']}** | Grounded Material: **{st.session_state.selected_doc_name}** | Ceiling: **{prof['working_memory_limit']} words**")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    audio_val = st.audio_input("Record audio note to bypass initiation friction")
    user_prompt = st.chat_input("State your thesis or critique...")

    final_input_text = None
    input_source = "Text"

    if audio_val is not None and ("last_audio" not in st.session_state or st.session_state.last_audio != audio_val):
        st.session_state.last_audio = audio_val
        input_source = "Voice Transcription"
        with st.spinner("Transcribing voice note..."):
            audio_bytes = audio_val.read()
            mime = getattr(audio_val, "type", "audio/wav") or "audio/wav"
            try:
                audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime)
                transcription = safe_generate_content(
                    prompt_text="Transcribe this audio recording verbatim without preamble.",
                    audio_part=audio_part
                )
                final_input_text = transcription.strip()
                st.info(f"🎤 **Transcribed:** *\"{final_input_text}\"*")
            except Exception as e:
                st.error(f"Voice note error: {e}")

    elif user_prompt:
        final_input_text = user_prompt
        input_source = "Direct Chat"

    if final_input_text:
        st.session_state.messages.append({"role": "user", "content": final_input_text})
        log_audit_entry("STUDENT_SPARRING_THESIS", prof['name'], final_input_text, meta=f"Source: {input_source}")

        with st.chat_message("user"):
            st.markdown(final_input_text)

        socratic_system = f"""
You are the Socratic sparring partner inside NEAM, working with executive student {prof['name']}.
Audience: Executive MBA at Berlin School of Creative Leadership (Steinbeis), evaluated by Prof. Dr. Mario Vaupel.

GROUNDING MATERIAL ({st.session_state.selected_doc_name}):
\"\"\"
{st.session_state.selected_curriculum_text[:6000]}
\"\"\"

RULES:
1. ANTI-GHOSTWRITING: Never draft essays or provide summary answers. Demand authentic reasoning.
2. COGNITIVE CHUNKING: Strictly under {prof['working_memory_limit']} words.
3. PERSONALIZATION: Use metaphors from {prof['passions']} and {prof['industry']}.
4. STANCE: {prof['stance']}. Incisive, direct, intellectually demanding.
"""
        with st.chat_message("assistant"):
            with st.spinner("Analyzing thesis against course material..."):
                try:
                    assistant_reply = safe_generate_content(
                        prompt_text=f"Student thesis: {final_input_text}",
                        system_instr=socratic_system
                    )
                    st.markdown(assistant_reply)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    log_audit_entry("SOCRATIC_CHALLENGE", "NEAM AI", assistant_reply)
                except Exception as e:
                    st.error(f"Endpoint error: {e}")

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Advance Sprint Milestone ➡️"):
                if st.session_state.current_sprint_step < 3:
                    st.session_state.current_sprint_step += 1
                    st.rerun()

# ---------------------------------------------------------
# TAB 3: MULTIMODAL EXECUTIVE STUDIO
# ---------------------------------------------------------
with tab_studio:
    prof = st.session_state.profile
    st.markdown("### 🎙️ Grounded Multimodal Strategy Translation Engine")
    st.caption(f"Currently Grounded In: **{st.session_state.selected_doc_name}**")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎧 Executive Deep-Dive Podcast Script")
        focus_angle = st.text_input(
            "Discussion Focus (Optional)",
            placeholder="e.g., Focus on eliminate-reduce trade-offs"
        )
        
        if st.button("Generate Podcast Script from Active Material", use_container_width=True):
            material = st.session_state.selected_curriculum_text[:12000]
            if not material:
                st.warning("⚠️ Please select a reading in the Curriculum Library tab first.")
            else:
                podcast_prompt = f"""
Generate an executive briefing script between Host A (Analytical Socratic Inquirer) and Host B (Practical Strategist).
Topic / Focus: {focus_angle if focus_angle else 'Core theoretical frameworks'}

GROUNDING MATERIAL ({st.session_state.selected_doc_name}):
\"\"\"
{material}
\"\"\"

TARGET EXECUTIVE:
- Name: {prof['name']}
- Industry: {prof['industry']}
- Metaphor Anchors: {prof['passions']}

REQUIREMENTS:
1. Ground arguments strictly in the provided material.
2. Address {prof['name']} directly by name 2 to 3 times with attention anchors.
3. Demystify frameworks using analogies from {prof['passions']}.
4. Format as Host A: / Host B: dialogue (under 600 words).
"""
                with st.spinner("Synthesizing script from library material..."):
                    try:
                        st.session_state.generated_script = safe_generate_content(prompt_text=podcast_prompt)
                        log_audit_entry("PODCAST_SYNTHESIZED", "NEAM Studio", f"Grounding doc: {st.session_state.selected_doc_name}")
                    except Exception as e:
                        st.error(f"Generation error: {e}")

        if "generated_script" in st.session_state:
            st.text_area("Podcast Script Output", st.session_state.generated_script, height=350)
            st.download_button(
                "📥 Download Podcast Script (.txt)",
                data=st.session_state.generated_script,
                file_name=f"NEAM_Podcast_{st.session_state.selected_doc_name}.txt",
                mime="text/plain"
            )

    with col2:
        st.markdown("#### 📊 Visual Strategy Blueprint")
        deck_focus = st.text_input("Slide Deck Objective", placeholder="e.g., Executive Boardroom Synthesis")

        if st.button("Generate Slide Deck Architecture", use_container_width=True):
            material = st.session_state.selected_curriculum_text[:12000]
            if not material:
                st.warning("⚠️ Please select a reading in the Curriculum Library tab first.")
            else:
                deck_prompt = f"""
Generate an 8-slide executive briefing deck blueprint for {prof['name']} strictly grounded in:
\"\"\"
{material}
\"\"\"

Context: {prof['industry']} | Metaphors: {prof['passions']} | Focus: {deck_focus}

For each slide, specify:
- Slide Title
- Visual Archetype (e.g., 2x2 Matrix, ERRC Grid, Flow)
- 3 Core Bullets (max 15 words each, directly from the source)
"""
                with st.spinner("Distilling slide architecture..."):
                    try:
                        st.session_state.generated_deck = safe_generate_content(prompt_text=deck_prompt)
                        log_audit_entry("DECK_SYNTHESIZED", "NEAM Studio", f"Grounding doc: {st.session_state.selected_doc_name}")
                    except Exception as e:
                        st.error(f"Generation error: {e}")

        if "generated_deck" in st.session_state:
            st.markdown(st.session_state.generated_deck)
