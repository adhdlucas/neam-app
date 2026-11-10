import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NEAM | Steinbeis Executive Co-Pilot",
    page_icon="🧠",
    layout="wide"
)

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

if prompt := st.chat_input("Speak your mind or type your rough idea here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    chat_contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        chat_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))

    with st.chat_message("assistant"):
        with st.spinner("Reflecting on course frameworks..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION + f"\nCurrent selected module context: {module_choice}",
                    temperature=0.7,
                )
            )
            reply = response.text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
