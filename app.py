import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NEAM | Steinbeis Executive Co-Pilot",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling for Reduced Cognitive Clutter
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .sprint-card {
        padding: 12px 16px;
        background: #ffffff;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

SYSTEM_INSTRUCTION = """
# ROLE & IDENTITY
You are the "Steinbeis Creative MBA AI Sparring Partner" (NEAM). 
Your mission is to help executive MBA students—specifically creative leaders with ADHD and executive function challenges—process course materials, clarify their thinking, and structure their assignments.

You are NOT a ghostwriter. You are an intellectual sounding board, cognitive scaffold, and executive coach.

# CORE RULES:
1. NEVER WRITE WALLS OF TEXT. Keep responses punchy, formatted with clear bold headers, short bullet points, and clean line breaks.
2. COMBAT TASK PARALYSIS: Break complex challenges into manageable micro-steps. Focus on one step at a time.
3. SOCRATIC SPARRING: Refuse to write complete answers for the student. Challenge assumptions, ask clarifying questions, and help them articulate their own logic.
4. CLOSED-LOOP PEDAGOGY: Ground your prompts in strategic frameworks (Christensen's Disruption, Kim & Mauborgne's Blue Ocean Strategy, Porter's Shared Value, and Kaplan & Norton's Strategy Maps).
5. ALWAYS end your turn with ONE concrete, low-friction question or action prompt.
"""

# Retrieve API Key from Secrets or Sidebar
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("👋 Welcome! Please enter your Gemini API key in the sidebar to activate the module.")
    st.stop()

# Initialize Client
client = genai.Client(api_key=api_key)

# Sidebar: Controls & Audit Trail
with st.sidebar:
    st.title("🧠 NEAM Co-Pilot")
    st.caption("Steinbeis / Berlin School of Creative Leadership")
    st.divider()
    module_choice = st.selectbox(
        "Course Framework:",
        [
            "Blue Ocean Strategy & ERRC Grid",
            "Disruptive Innovation & Incumbent Dilemma",
            "Creating Shared Value (CSV)",
            "Strategic Alignment & Implementation Matrix"
        ]
    )
    
    st.markdown("""
    <div class="sprint-card">
        <b>ADHD Pacing Aid:</b><br>
        Micro-Sprint 1: Problem Clarification<br>
        Micro-Sprint 2: Theoretical Grounding<br>
        Micro-Sprint 3: Strategy Defensibility
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📋 Faculty Audit Trail")
    if st.button("Generate Proof-of-Work Log"):
        if "messages" in st.session_state and len(st.session_state.messages) > 1:
            log_content = f"# Learning Inquiry & Sparring Log\nModule: {module_choice}\n\n"
            for msg in st.session_state.messages:
                log_content += f"**{msg['role'].upper()}:** {msg['content']}\n\n"
            st.download_button(
                label="📥 Download Log for Evaluator",
                data=log_content,
                file_name="NEAM_Proof_of_Work_Log.md",
                mime="text/markdown"
            )
        else:
            st.warning("Start a sparring session first to generate an audit log.")

# Workspace Header
st.header("Executive Strategy Sparring Workspace")
st.caption(f"Currently grounded in: **{module_choice}** | Socratic Scaffolding Active")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! I'm your strategic sparring partner. Bring me your raw, messy thoughts or voice notes—we'll unpack them into structured leadership insights together.\n\n**Where is your head at right now with this module?**"
        }
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Voice Input
audio_data = st.audio_input("🎙️ Record a quick voice thought (optional)")

user_text = st.chat_input("Speak your mind or type your rough idea here...")

user_prompt = None
audio_bytes = None

if audio_data is not None:
    audio_bytes = audio_data.read()
    user_prompt = "🎙️ [Student submitted a voice note]"

if user_text:
    user_prompt = user_text

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Format history cleanly as strings for the API
    full_prompt_text = f"Context Module: {module_choice}\n\n"
    for m in st.session_state.messages[:-1]:
        prefix = "Student" if m["role"] == "user" else "Sparring Partner"
        full_prompt_text += f"{prefix}: {m['content']}\n\n"
    
    full_prompt_text += f"Student: {user_prompt}\nSparring Partner:"

    with st.chat_message("assistant"):
        with st.spinner("Sparring with course frameworks..."):
            try:
                # Prepare contents
                if audio_bytes:
                    contents = [
                        types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                        full_prompt_text
                    ]
                else:
                    contents = full_prompt_text

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"API Error Details: {e}")
