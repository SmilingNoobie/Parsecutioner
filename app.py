import streamlit as st
import os, json
from io import BytesIO
from fpdf import FPDF

from src.pdf_extractor import extract_text_from_pdf
from src.segmenter     import segment
from src.scorer        import (
    aggregate_embeddings, score_cv,
    score_to_label, get_scale_feedback
)
from src.ai_feedback   import (
    get_self_feedback, get_example_feedback, get_revised_cv
)

# ─── Page Config & Theme ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Parsecutioner: CV Parser & Ranker",
    page_icon="⚔️📄",
    layout="centered"
)

st.markdown("""
<style>
  .stApp {background:#f0f4f8; font-family:Arial,sans-serif;}
  .main-header {text-align:center; margin-top:2rem; font-size:2.75rem; color:#2f4f85;}
  .sub-header  {text-align:center; margin-bottom:1rem; font-size:1.1rem; font-style:italic; color:#4a6f8f;}
  .section     {max-width:800px; margin:1rem auto; padding:1.5rem; background:white;
                 border-radius:10px; box-shadow:0 2px 8px rgba(0,0,0,0.1);}
  button[data-baseweb="base-button"], select {cursor:pointer !important;}
  button[data-baseweb="base-button"] {
    background:#4A90E2!important; color:#fff!important; font-weight:600!important;
    padding:0.6rem 1.2rem!important; border-radius:5px!important;
    transition:background 0.3s!important;
  }
  button[data-baseweb="base-button"]:hover {background:#357ab7!important;}
  .stFileUploader>div>div {border:2px dashed #4A90E2!important; border-radius:8px!important;}
  .streamlit-expanderHeader {background:#F5F8FA!important; border-radius:4px!important;}
  .result-card {background:#f9f9f9; padding:1.2rem; margin-bottom:1rem; border-radius:8px;
                box-shadow:0 1px 5px rgba(0,0,0,0.1);}
  .result-card h3 {margin-bottom:0.5rem; color:#2f4f85;}
  .feedback-section {border:2px solid #4A90E2; padding:1rem; border-radius:10px;}
  .feedback-section h3 {font-size:1.5rem; color:#2f4f85;}
  .feedback-section p {font-size:1.1rem;}
</style>
""", unsafe_allow_html=True)

# ─── Header & Description ────────────────────────────────────────────────────
st.markdown('<div class="main-header">Parsecutioner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Parse, rank, and refine your CV against any job description—'
    'with ML/AI-driven feedback and an instant “Revise My CV” feature.</div>',
    unsafe_allow_html=True
)

# ─── Inputs (centered) ─────────────────────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)

mode = st.radio(
    "Mode:", ["Use Existing CV Dataset", "Upload & Analyze New CVs"], index=1
)
job_file = st.file_uploader("📄 Job Description (.txt)", type="txt")
self_cv   = st.file_uploader("👤 Your CV (.pdf)", type="pdf")

if mode == "Use Existing CV Dataset":
    role = st.selectbox(
        "Select Role Dataset:",
        ["Software Engineer", "Data Analyst", "Cybersecurity Specialist"]
    )
else:
    cvs = st.file_uploader(
        "📂 Example CVs (.pdf)", type="pdf", accept_multiple_files=True
    )

if st.button("🗡️ Analyze"):
    st.session_state.analyzed = True

st.markdown('</div>', unsafe_allow_html=True)

# ─── Only show results once “Analyze” is clicked ──────────────────────────────
if st.session_state.get("analyzed", False):
    # Load inputs
    jd_text  = job_file.read().decode() if job_file else ""
    self_txt = extract_text_from_pdf(self_cv) if self_cv else ""

    # Prepare example results list
    example_results = []
    if mode == "Use Existing CV Dataset":
        data = json.load(open("data/precomputed_results.json"))
        key = role.lower().replace(" ", "_")
        for e in data.get(key, []):
            scr = e["score"]
            example_results.append((scr, e["reasons"]))
    else:
        jd_emb, _ = aggregate_embeddings(jd_text, {"overall": jd_text})
        for pdf in cvs:
            txt = extract_text_from_pdf(pdf)
            segs = segment(txt)
            cv_texts = {"overall":txt, **{k:[ "\n".join(v) ] for k,v in segs.items()}}
            _, cv_emb = aggregate_embeddings(jd_text, cv_texts)
            scr = score_cv(jd_emb, cv_emb)
            feedback_txt = f"{get_scale_feedback(scr)}\n\n{get_example_feedback(jd_text, txt)}"
            example_results.append((scr, feedback_txt))
        example_results.sort(key=lambda x: x[0], reverse=True)
        example_results = example_results[:5]

    # ─── Display Example Rankings ────────────────────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("🏆 Example CV Rankings")
    for i, (scr, fb) in enumerate(example_results, start=1):
        label = score_to_label(scr)
        with st.expander(f"Rank {i} - Score {scr:.3f} — {label}"):
            st.markdown(f'<div class="result-card"><p>{fb}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─── Your CV Analysis (hidden until toggled) ─────────────────────────────────
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("📝 Your CV Analysis")

    if st.button("Show Job Description"):
        st.write(jd_text)
    if st.button("Show My Original CV"):
        st.write(self_txt)

    # Score & label
    jd_emb, _      = aggregate_embeddings(jd_text, {"overall": jd_text})
    _, cv_emb_self = aggregate_embeddings(jd_text, {"overall": self_txt})
    your_score     = score_cv(jd_emb, cv_emb_self)
    your_label     = score_to_label(your_score)
    your_scale_fb  = get_scale_feedback(your_score)

    st.subheader(f"🎯 Your Score: {your_score:.3f} — {your_label}")
    st.write(your_scale_fb)

    # Detailed AI Feedback
    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
    st.header("💬 Detailed Feedback")
    self_fb = get_self_feedback(jd_text, self_txt)
    for k, v in self_fb.items():
        st.markdown(f"**{k.replace('_',' ').title()}**")
        st.write(v)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─── Revise My CV (No PDF button) ────────────────────────────────────────────
    st.markdown('<hr>', unsafe_allow_html=True)
    revised = get_revised_cv(jd_text, self_txt)

    # Display revised CV with a border
    st.markdown('<div class="result-card" style="border: 2px solid #4A90E2;">', unsafe_allow_html=True)
    st.header("🖊️ Revised CV")
    st.write(revised)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Marketing Section ─────────────────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)

# Marketing Section Header
st.header("Why Choose Parsecutioner?")
st.write("""
    **Transform Your CV. Maximize Your Career Opportunities.**

    🚀 **Benchmark Against Industry Leaders:**  
    Upload your job description and compare your CV to those of high-performing candidates using our pre-trained datasets. See how your CV measures up and receive actionable feedback to improve it.

    📈 **Get Tailored Feedback for Your Dream Job:**  
    Planning to apply for a specific role? Upload your dataset of professional CVs for that job, and let us optimize your resume with personalized feedback. Our advanced algorithms analyze and rank your CV to provide insights that directly enhance your chances for success.

    📥 **Download Your Optimized Resume:**  
    After receiving feedback and revisions, easily download your updated CV in a clean, professional PDF format to share with potential employers.

    Parsecutioner is your ultimate tool to bridge the gap between job seekers and industry professionals with optimized resumes designed to pass ATS and attract hiring managers.

    💼 Whether you're starting your career or advancing to the next level, Parsecutioner provides the tools you need to **stand out in the competitive job market**.
""")

# Marketing Call to Action
st.markdown('---', unsafe_allow_html=True)
st.markdown("""
    Ready to take your career to the next level?  
    Upload your CV, analyze it, and let Parsecutioner help you build the perfect resume tailored for the job you want.

    **Start Now and Secure Your Future!**
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
