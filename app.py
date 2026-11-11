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

def get_client(key: str):
    return genai.Client(api_key=key)

ACTIVE_MODEL = "gemini-3.8-flash"

# Single-attempt streaming function (conserves calls & shows text immediately)
def stream_socratic_response(prompt_text: str, system_instr: str):
    config = types.GenerateContentConfig(
        system_instruction=system_instr,
        temperature=0.7
    )
    for key in api_keys:
        try:
            client = get_client(key)
            response_stream = client.models.generate_content_stream(
                model=ACTIVE_MODEL,
                contents=[prompt_text],
                config=config
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
            return
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "quota" in err or "resource_exhausted" in err:
                continue
            raise e

# Single-attempt text generation for studio
def generate_studio_text(prompt_text: str):
    config = types.GenerateContentConfig(temperature=0.7)
    for key in api_keys:
        try:
            client = get_client(key)
            resp = client.models.generate_content(
                model=ACTIVE_MODEL,
                contents=[prompt_text],
                config=config
            )
            return resp.text
        except Exception as e:
            err = str(e).lower()
            if "429" in err or "quota" in err or "resource_exhausted" in err:
                continue
            raise e
    raise RuntimeError("All configured API keys have exceeded their current quota.")

# ---------------------------------------------------------
# CURRICULUM DIRECTORY & INGESTION
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

# Fallback starter file if directory is empty
sample_path = os.path.join(CURRICULUM_DIR, "Steinbeis_Core_Creative_Leadership.txt")
if not os.path.exists(sample_path) and len(os.listdir(CURRICULUM_DIR)) == 0:
    with open(sample_path, "w", encoding="utf-8") as f:
        f.write(
            "Steinbeis Creative Leadership Synthesis:\n"
            "Executive leadership in non-linear environments requires balancing value innovation, "
            "cognitive empathy, and organizational defensibility. Conventional management "
            "often penalizes divergent problem-solving, whereas adaptive scaffolding enables creative "
            "executives to transform strategic friction into competitive differentiation."
        )

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
if "profile" not in st.session_state:
    st.session_state.profile = {
        "name": "Lucas",
        "industry": "Creative Direction / Retail Management",
        "passions": "Cinema Production, Industrial Design, Mid-Century Architecture",
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
    st.session_state.selected_doc_name = "Steinbeis_Core_Creative_Leadership.txt"
    st.session_state.selected_curriculum_text = extract_file_content(sample_path)

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
- **Active Document Analyzed:** {st.session_state.selected_doc_name}
- **Reasoning Stance:** {prof['stance']}
- **Chunking Threshold:** <{prof['working_memory_limit']} words
- **Metaphorical Anchors:** {prof['passions']}

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
    st.caption(f"Engine: `{ACTIVE_MODEL}`")
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
    st.caption("Preloaded institutional readings and frameworks. Select a paper to instantly ground your Socratic sparring and podcast generator.")

    all_files = sorted(glob.glob(os.path.join(CURRICULUM_DIR, "*.*")))
    file_map = {os.path.basename(f): f for f in all_files}

    col_lib_a, col_lib_b = st.columns([1, 1])

    with col_lib_a:
        st.markdown("#### 🏛️ Preloaded Module Literature")
        if file_map:
            selected_file_name = st.selectbox("Curriculum Library", list(file_map.keys()))
            selected_path = file_map[selected_file_name]
            
            with open(selected_path, "rb") as f_bytes:
                st.download_button(
                    label=f"📥 Download Original Document ({selected_file_name})",
                    data=f_bytes,
                    file_name=selected_file_name,
                    mime="application/pdf" if selected_file_name.endswith(".pdf") else "text/plain"
                )

            if st.button("🚀 Load into Active Workspace & Studio", use_container_width=True):
                loaded_text = extract_file_content(selected_path)
                st.session_state.selected_curriculum_text = loaded_text
                st.session_state.selected_doc_name = selected_file_name
                log_audit_entry("LIBRARY_DOC_SELECTED", "Student", f"Loaded curriculum: {selected_file_name}")
                st.success(f"Loaded '{selected_file_name}' as active grounded source!")
        else:
            st.info("No curriculum files detected in `curriculum/` folder.")

    with col_lib_b:
        st.markdown("#### 📤 Upload External Literature")
        uploaded_doc = st.file_uploader("Upload custom PDF or TXT", type=["pdf", "txt", "md"])
        if uploaded_doc is not None:
            saved_dest = os.path.join(CURRICULUM_DIR, uploaded_doc.name)
            with open(saved_dest, "wb") as f_out:
                f_out.write(uploaded_doc.getbuffer())
            st.success(f"Saved '{uploaded_doc.name}' to library!")
            st.session_state.selected_curriculum_text = extract_file_content(saved_dest)
            st.session_state.selected_doc_name = uploaded_doc.name
            st.rerun()

    st.markdown("---")
    st.markdown(f"**Currently Active Grounded Material:** `{st.session_state.selected_doc_name}`")
    if st.session_state.selected_curriculum_text:
        with st.expander("Preview Extracted Source Material Snippet"):
            st.text(st.session_state.selected_curriculum_text[:1200] + "...")

# ---------------------------------------------------------
# TAB 2: SOCRATIC SPARRING ROOM (STREAMING FAST, ZERO ERRORS)
# ---------------------------------------------------------
with tab_sparring:
    prof = st.session_state.profile
    st.markdown(f"### Socratic Sparring Partner: Step {st.session_state.current_sprint_step}/3")
    st.caption(f"Profile: **{prof['name']}** | Grounded In: **{st.session_state.selected_doc_name}** | Ceiling: **{prof['working_memory_limit']} words**")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("State your thesis or critique...")

    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        log_audit_entry("STUDENT_SPARRING_THESIS", prof['name'], user_prompt, meta="Direct Chat")

        with st.chat_message("user"):
            st.markdown(user_prompt)

        socratic_system = f"""
You are the Socratic sparring partner inside NEAM, working with executive student {prof['name']}.
Evaluator: Prof. Dr. Mario Vaupel (Berlin School of Creative Leadership / Steinbeis).

GROUNDING MATERIAL ({st.session_state.selected_doc_name}):
\"\"\"
{st.session_state.selected_curriculum_text[:5000]}
\"\"\"

RULES:
1. ANTI-GHOSTWRITING: Never draft answers or give textbook summaries. Dissect assumptions and demand justification.
2. COGNITIVE CHUNKING: Strictly under {prof['working_memory_limit']} words.
3. PERSONALIZATION: Use metaphors from {prof['passions']} and {prof['industry']}.
4. STANCE: {prof['stance']}. Incisive and direct.
"""
        with st.chat_message("assistant"):
            try:
                response_stream = stream_socratic_response(
                    prompt_text=f"Student inquiry: {user_prompt}",
                    system_instr=socratic_system
                )
                assistant_reply = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                log_audit_entry("SOCRATIC_CHALLENGE", "NEAM AI", assistant_reply)
            except Exception as e:
                st.error(f"Error during sparring: {e}")

        col_a, col_b = st.columns([3, 1])
        with col_b:
            if st.button("Advance Sprint Milestone ➡️"):
                if st.session_state.current_sprint_step < 3:
                    st.session_state.current_sprint_step += 1
                    st.rerun()

# ---------------------------------------------------------
# TAB 3: MULTIMODAL EXECUTIVE STUDIO (NOTEBOOKLM SCRIPT + ZERO-COST AUDIO)
# ---------------------------------------------------------
with tab_studio:
    prof = st.session_state.profile
    st.markdown("### 🎙️ Grounded Multimodal Strategy Translation Engine")
    st.caption(f"Currently Grounded In: **{st.session_state.selected_doc_name}**")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 🎧 Executive Deep-Dive Podcast")
        focus_angle = st.text_input(
            "Discussion Angle (Optional)",
            placeholder="e.g., Focus on eliminate-reduce trade-offs and value curves"
        )
        
        generate_audio_btn = st.button("🎙️ Generate Deep-Dive Executive Podcast", use_container_width=True)

        if generate_audio_btn:
            material = st.session_state.selected_curriculum_text[:8000]
            if not material:
                st.warning("⚠️ Please select a reading in the Curriculum Library tab first.")
            else:
                podcast_script_prompt = f"""
You are the Executive Audio Synthesizer inside NEAM.
Generate an executive briefing podcast script between two hosts:
- Host A (Analytical Socratic Inquirer)
- Host B (Practical Strategist)

Topic / Angle: {focus_angle if focus_angle else 'Core theoretical frameworks'}

GROUNDING MATERIAL:
\"\"\"
{material}
\"\"\"

TARGET EXECUTIVE:
- Name: {prof['name']}
- Industry: {prof['industry']}
- Metaphors: {prof['passions']}

REQUIREMENTS:
1. Ground arguments 100% in the source material.
2. Address {prof['name']} directly by name 2 to 3 times to refocus attention.
3. Translate theoretical frameworks using concrete analogies from {prof['passions']}.
4. Length: 400-500 words. Format cleanly as Host A: / Host B: lines.
"""
                with st.spinner("Synthesizing grounded executive podcast script..."):
                    try:
                        script_text = generate_studio_text(prompt_text=podcast_script_prompt)
                        st.session_state.generated_script = script_text
                        log_audit_entry("PODCAST_SYNTHESIZED", "NEAM Studio", f"Grounding: {st.session_state.selected_doc_name}")
                    except Exception as e:
                        st.error(f"Generation notice: {e}")

        if "generated_script" in st.session_state and st.session_state.generated_script:
            st.success("✅ Deep-Dive Podcast Script Ready!")
            
            # Zero-Quota Browser Audio Player (Plays aloud right in the app)
            escaped_script = st.session_state.generated_script.replace("`", "'").replace("\n", " ")
            tts_html = f"""
            <div style="background-color: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 12px;">
                <p style="color: #10b981; font-weight: bold; margin-bottom: 8px;">🔊 Play Spoken Dialogue (Zero API Cost):</p>
                <button onclick="window.speechSynthesis.cancel(); let msg = new SpeechSynthesisUtterance(`{escaped_script[:1500]}`); msg.rate = 1.0; window.speechSynthesis.speak(msg);" style="background-color: #10b981; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-right: 8px;">▶️ Play Episode</button>
                <button onclick="window.speechSynthesis.cancel();" style="background-color: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: bold;">⏹️ Stop</button>
            </div>
            """
            st.components.v1.html(tts_html, height=90)

            st.text_area("Full Dialogue Script", st.session_state.generated_script, height=300)
            st.download_button(
                "📥 Download Episode Script (.txt)",
                data=st.session_state.generated_script,
                file_name=f"NEAM_Podcast_{prof['name']}.txt",
                mime="text/plain"
            )

    with col2:
        st.markdown("#### 📊 Visual Strategy Blueprint")
        deck_focus = st.text_input("Slide Deck Objective", placeholder="e.g., Executive Boardroom Synthesis")

        if st.button("Generate Slide Deck Architecture", use_container_width=True):
            material = st.session_state.selected_curriculum_text[:8000]
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
- Visual Archetype (e.g., 2x2 Matrix, ERRC Grid)
- 3 Core Bullets (max 15 words each, directly from the source)
"""
                with st.spinner("Distilling slide architecture..."):
                    try:
                        st.session_state.generated_deck = generate_studio_text(prompt_text=deck_prompt)
                        log_audit_entry("DECK_SYNTHESIZED", "NEAM Studio", f"Grounding: {st.session_state.selected_doc_name}")
                    except Exception as e:
                        st.error(f"Generation error: {e}")

        if "generated_deck" in st.session_state:
            st.markdown(st.session_state.generated_deck)
