import streamlit as st
from google import genai

st.set_page_config(
    page_title="NEAM | Steinbeis Executive Co-Pilot",
    page_icon="🧠",
    layout="wide"
)

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

SYSTEM_INSTRUCTION = """# ROLE & IDENTITY
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

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if not api_key:
    st.info("👋 Welcome! Please enter your Gemini API key in the sidebar to activate the module.")
    st.stop()

client = genai.Client(api_key=api_key)

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

st.header("Executive Strategy Sparring Workspace")
st.caption(f"Currently grounded in: **{module_choice}** | Socratic Scaffolding Active")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Welcome! I'm your strategic sparring partner. Bring me your raw, messy thoughts or notes—we'll unpack them into structured leadership insights together.\n\n**Where is your head at right now with this module?**"
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

audio_data = st.audio_input("🎙️ Record a quick voice thought (optional)")
user_text = st.chat_input("Speak your mind or type your rough idea here...")

user_prompt = None
if audio_data is not None:
    user_prompt = "🎙️ [Student submitted an audio query. Please help me unpack my strategic thoughts.]"

if user_text:
    user_prompt = user_text

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    full_conversation = f"Active Course Framework: {module_choice}\n\n"
    for m in st.session_state.messages[:-1]:
        sender = "Student" if m["role"] == "user" else "Sparring Partner"
        full_conversation += f"{sender}: {m['content']}\n\n"
    full_conversation += f"Student: {user_prompt}\nSparring Partner:"

    with st.chat_message("assistant"):
        with st.spinner("Reflecting on course frameworks..."):
            try:
                # Interactions API for Gemini 3.8
                interaction = client.interactions.create(
                    model="models/gemini-3.8-flash",
                    input=full_conversation,
                    system_instruction=SYSTEM_INSTRUCTION
                )
                
                # Extract text output
                reply = ""
                if hasattr(interaction, "outputs") and interaction.outputs:
                    for out in interaction.outputs:
                        if hasattr(out, "text"):
                            reply += out.text
                        elif isinstance(out, dict) and "text" in out:
                            reply += out["text"]
                elif hasattr(interaction, "text"):
                    reply = interaction.text
                else:
                    reply = str(interaction)
                    
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                # Fallback to standard generate_content if interactions call differs
                try:
                    res = client.models.generate_content(
                        model="models/gemini-3.8-flash",
                        contents=full_conversation,
                        config={"system_instruction": SYSTEM_INSTRUCTION}
                    )
                    reply = res.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                except Exception as inner_e:
                    st.error(f"Error: {inner_e}")
