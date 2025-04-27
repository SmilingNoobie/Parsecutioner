import streamlit as st
import os
import json
from src.pdf_extractor import extract_text_from_pdf
from src.segmenter import segment
from src.scorer import (
    aggregate_embeddings, score_cv,
    score_to_label, get_scale_feedback
)
from src.ai_feedback import get_self_feedback, get_example_feedback

# ─── Page Config & Theme ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Parsecutioner: CV Parser & Ranker",
    page_icon="🗡️📄",
    layout="centered"
)

# Inject custom CSS for global styling
st.markdown("""
<style>
  /* Background & font */
  .stApp { background-color: #f0f4f8; font-family: Arial, sans-serif; }

  /* Main header & sub-header */
  .main-header { text-align:center; margin-top:2rem; font-size:2.75rem; color:#2f4f85; }
  .sub-header  { text-align:center; margin-bottom:2rem; font-size:1.25rem; color:#4a6f8f; }

  /* Centered card/style container */
  .section {
    max-width:800px; margin:1rem auto 2rem; padding:2rem;
    background:white; border-radius:10px;
    box-shadow:0 2px 10px rgba(0,0,0,0.1);
  }

  /* Pointer cursor on buttons and selects */
  button[data-baseweb="base-button"], select, .stRadio>label { cursor: pointer !important; }

  /* Button styling */
  button[data-baseweb="base-button"] {
    background-color:#4A90E2 !important; color:white !important;
    border-radius:5px !important; padding:0.6rem 1.5rem !important;
    font-size:1rem !important; font-weight:600 !important;
    transition:background-color .3s ease !important;
  }
  button[data-baseweb="base-button"]:hover { background-color:#357ab7 !important; }

  /* File uploader style overrides */
  .stFileUploader>div>div { border: 2px dashed #4A90E2 !important; border-radius:8px !important; }

  /* Expander / result-card styling */
  .streamlit-expanderHeader { background:#F5F8FA !important; border-radius:4px !important; }
  .result-card {
    background:#f9f9f9; border-radius:8px; margin-bottom:1rem; padding:1.5rem;
    box-shadow:0 1px 5px rgba(0,0,0,0.1);
  }
  .result-card h3 { font-size:1.3rem; color:#2f4f85; margin-bottom:0.5rem; }
  .result-card p  { font-size:1.1rem; color:#5a6a74; }
</style>
""", unsafe_allow_html=True)

# ─── Page Title ───────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">Parsecutioner</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Choose your mode and upload files below</div>', unsafe_allow_html=True)

# ─── Mode Selector & Inputs ───────────────────────────────────────────────────
st.markdown('<div class="section">', unsafe_allow_html=True)

mode = st.radio(
    "How would you like to proceed?",
    ["Use Existing CV Dataset", "Upload & Analyze New CVs"],
    index=1
)

# Always need job desc + your CV
jd_file = st.file_uploader("📄 Job Description (TXT)", type=["txt"])
self_cv = st.file_uploader("👤 Your CV (PDF)", type=["pdf"])

# Conditional inputs
if mode == "Use Existing CV Dataset":
    role = st.selectbox(
        "🔎 Select a Role Dataset",
        ["Software Engineer", "Data Analyst", "Cybersecurity Specialist"]
    )
else:
    cvs = st.file_uploader(
        "📂 Example CVs (PDF)", type=["pdf"], accept_multiple_files=True
    )

analyze = st.button("🗡️ Analyze", help="Click to run the analysis")

st.markdown('</div>', unsafe_allow_html=True)

# ─── Analysis Logic ───────────────────────────────────────────────────────────
if analyze:
    # Validation
    if not jd_file or not self_cv or (mode=="Upload & Analyze New CVs" and not cvs):
        st.error("⚠️ Please upload all required files for the selected mode.")
    else:
        # Read JD & your CV
        jd_text  = jd_file.read().decode("utf-8")
        self_txt = extract_text_from_pdf(self_cv)

        # Prepare example results
        example_results = []
        if mode == "Use Existing CV Dataset":
            # Load precomputed JSON
            data = json.load(open(os.path.join("data","precomputed_results.json")))
            key = role.lower().replace(" ","_")
            for entry in data.get(key, []):
                scr = entry["score"]
                label = score_to_label(scr)
                reasons = entry["reasons"]
                example_results.append((scr, f"{reasons}"))
        else:
            # Dynamically compute example results
            jd_emb, _ = aggregate_embeddings(jd_text, {"overall": jd_text})
            for pdf_file in cvs:
                txt = extract_text_from_pdf(pdf_file)
                segs = segment(txt)
                cv_texts = {"overall":txt, **{k:["\n".join(v)] for k,v in segs.items()}}
                _, cv_emb = aggregate_embeddings(jd_text, cv_texts)
                scr = score_cv(jd_emb, cv_emb)
                # combine scale feedback + AI reasons
                scale_fb = get_scale_feedback(scr)
                reasons  = get_example_feedback(jd_text, txt)
                example_results.append((scr, f"{scale_fb}\n\n{reasons}"))
            # top-5 by score
            example_results = sorted(example_results, key=lambda x: x[0], reverse=True)[:5]

        # ─ Display Example Rankings ──────────────────────────────────────────────
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.header("🏆 Example CVs Ranking")
        for i,(scr,fb) in enumerate(example_results, start=1):
            lbl = score_to_label(scr)
            with st.expander(f"{i}. Score: {scr:.3f} — {lbl}"):
                st.write(fb)
        st.markdown('</div>', unsafe_allow_html=True)

        # ─ Your CV Analysis ─────────────────────────────────────────────────────
        st.markdown('<div class="section">', unsafe_allow_html=True)
        st.header("📝 Your CV Analysis")

        cols = st.columns(2)
        with cols[0]:
            st.subheader("Job Description")
            st.write(jd_text)
        with cols[1]:
            st.subheader("Your CV")
            st.write(self_txt)

        # Compute your score + label + scale feedback
        jd_emb, _      = aggregate_embeddings(jd_text, {"overall":jd_text})
        _, cv_emb_self = aggregate_embeddings(jd_text, {"overall":self_txt})
        your_score     = score_cv(jd_emb, cv_emb_self)
        your_label     = score_to_label(your_score)
        your_scale_fb  = get_scale_feedback(your_score)

        st.subheader(f"🎯 Your Score: {your_score:.3f} — {your_label}")
        st.write(your_scale_fb)

        # Detailed AI feedback
        st.header("💬 Detailed Personalized Feedback")
        self_fb = get_self_feedback(jd_text, self_txt)
        for k,v in self_fb.items():
            st.markdown(f"**{k.replace('_',' ').title()}**")
            st.write(v)

        st.markdown('</div>', unsafe_allow_html=True)
