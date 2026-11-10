import time
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="NEAM | Steinbeis Executive Co-Pilot",
    page_icon="🧠",
    layout="wide"
)

# Custom Styling: Executive Clean Green Palette
st.markdown("""
<style>
    .main { background-color: #f9fafb; }
    
    /* ADHD Pacing Aid card with emerald green border */
    .sprint-card {
        padding: 14px 18px;
        background: #ffffff;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        margin-bottom: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    
    /* User chat bubble styling */
    div[data-testid="stChatMessage"]:nth-child(even) {
        border-left: 3px solid #10b981;
        background-color: #f0fdf4;
        border-radius: 8px;
        padding: 8px;
    }

    /* Primary buttons */
    button[kind="primary"], .stDownloadButton>button {
        background-color: #10b981 !important;
        border-color: #059669 !important;
        color: white !important;
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
        <b style="color: #065f46;">ADHD Pacing Aid:</b><br>
        • Micro-Sprint 1: Problem Clarification<br>
        • Micro-Sprint 2: Theoretical Grounding<br>
        • Micro-Sprint 3: Strategy Defensibility
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

user_prompt = st.chat_input("Speak your mind or type your rough idea here...")

if user_prompt:
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    full_prompt = f"Module Focus: {module_choice}\n\n"
    for m in st.session_state.messages[:-1]:
        role = "Student" if m["role"] == "user" else "Sparring Partner"
        full_prompt += f"{role}: {m['content']}\n\n"
    full_prompt += f"Student: {user_prompt}\nSparring Partner:"

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Primary: gemini-2.0-flash-lite, Fallback: gemini-1.5-flash
        for target_model in ["gemini-3.8-flash"]:
            try:
                response_stream = client.models.generate_content_stream(
                    model=target_model,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                break
            except Exception as e:
                err_text = str(e)
                if target_model == "gemini-1.5-flash":
                    message_placeholder.error(f"Error: {e}")
                else:
                    time.sleep(1)
                    continue
