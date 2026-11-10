import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NEAM | Steinbeis Executive Co-Pilot",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling
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

# Retrieve API Key
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("👋 Welcome! Please enter your Gemini API key in the sidebar to activate the module.")
    st.stop()

client = genai.Client(api_key=api_key)

# Sidebar
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

# Voice Input Section
audio_data = st.audio_input("🎙️ Record a quick voice thought (optional)")

user_input = None
model="gemini-3.8-flash",
if audio_data is not None:
    with st.spinner("Transcribing and processing your voice note..."):
        audio_bytes = audio_data.read()
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        user_input = "Voice Note: Student spoke their thoughts via audio."
        prompt_content = [audio_part, "Please listen to this student audio, transcribe their core strategic dilemma, and respond according to the NEAM sparring instructions."]

text_prompt = st.chat_input("Speak your mind or type your rough idea here...")
if text_prompt:
    user_input = text_prompt
    prompt_content = text_prompt

# Send to Gemini
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    chat_contents = []
    for m in st.session_state.messages[:-1]:
        role = "user" if m["role"] == "user" else "model"
        chat_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
    
    if isinstance(prompt_content, list):
        chat_contents.append(types.Content(role="user", parts=prompt_content))
    else:
        chat_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=prompt_content)]))

    with st.chat_message("assistant"):
        with st.spinner("Sparring with course frameworks..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=chat_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION + f"\nCurrent selected module context: {module_choice}",
                        temperature=0.7,
                    )
                )
                reply = response.text
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"Error connecting to model: {e}")
