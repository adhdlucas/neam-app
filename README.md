# NEAM | Neurodivergent Executive AI Module

> Closed-loop cognitive scaffolding and Socratic AI co-pilot designed for creative leaders, startup founders, and neurodivergent professionals (ADHD, dyslexia, non-linear cognitive profiles).

---

## 🎯 Academic & Institutional Context
- **Candidate:** Lucas Giraldo Mejia
- **Program:** Executive MBA in Creative Leadership
- **Institution:** Berlin School of Creative Leadership / Steinbeis University (Schools of Next Practices)
- **Faculty / Evaluator:** Prof. Dr. Mario Vaupel

---

## ⚡ Core Architecture & Pedagogical Pillars

1. **Anti-Ghostwriting Protocol**
   - Strictly refuses to draft essays, answers, or assignments.
   - Operates as a Socratic sparring partner, challenging assumptions and demanding authentic justification.

2. **Cognitive Load Chunking**
   - Enforces a strict working-memory threshold (<150 words per Socratic turn) to prevent executive overwhelm.
   - Integrates dual-modality input (direct voice recording via `st.audio_input` alongside text chat) to dismantle task-initiation friction.

3. **Hyper-Personalized Multimodal Studio**
   - Generates two-host executive podcast scripts embedding real-time dynamic attention anchors ("Hey Lucas...") and custom domain metaphors.
   - Compiles visual 8-slide strategy blueprints based on framework literature.

4. **Faculty Proof-of-Work Audit Trail**
   - Maintains an in-memory chronological ledger of student hypotheses, voice inputs, and conceptual revisions.
   - Produces a downloadable, timestamped Markdown audit dossier verifying critical human reasoning for academic grading.

---

## 🛠️ Tech Stack & Deployment
- **Interface:** Streamlit Community Cloud (`neam-app.streamlit.app`)
- **Model Engine:** Google GenAI SDK (`google-genai`), Gemini 2.5 Flash
- **Secrets:** Streamlit Cloud Secrets (`GEMINI_API_KEY`)
