import streamlit as st
import os
import json
from src.pdf_extractor import extract_text_from_pdf
from src.segmenter import segment
from src.scorer import aggregate_embeddings, score_cv, score_to_label, get_scale_feedback
from src.ai_feedback import get_self_feedback, get_example_feedback

# Page config
st.set_page_config(page_title="Parsecutioner | CV Parser & Ranking", layout="wide")

# Inject custom CSS for global styling
st.markdown(
    """
    <style>
        /* Global background */
        .stApp {
            background-color: #FFFFFF;
        }
        /* Header styling */
        h1 {
            color: #0A1F44;
        }
        /* Subheaders */
        h2, h3 {
            color: #4A90E2;
        }
        /* Buttons */
        .stButton>button {
            background-color: #4A90E2;
            color: white;
            border-radius: 8px;
            padding: 0.6em 1.2em;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #3B7BBF;
        }
        /* Sidebar header */
        .css-1d391kg {
            color: #4A90E2;
            font-size: 1.2rem;
            font-weight: 600;
        }
        /* Expander style */
        .streamlit-expanderHeader {
            background-color: #F5F8FA;
            border-radius: 4px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main header
st.markdown("""
<div style="text-align:center; margin-top:1rem;">
    <h1>🚀 Welcome to Parsecutioner: Your CV Parser & Ranker</h1>
    <p style="font-size:1.1rem; color:#555;">Upload a job description and your own CV, then choose to analyze against example datasets or upload new CVs.</p>
</div>
""", unsafe_allow_html=True)

# Sidebar options
with st.sidebar:
    st.markdown("<h2>📂 Options</h2>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["Upload New CVs", "Use Existing CVs"] )
    job_file = st.file_uploader('Job Description (TXT)', type=['txt'])
    self_cv = st.file_uploader('Your CV (PDF)', type=['pdf'])
    if mode == "Upload New CVs":
        cvs_files = st.file_uploader('Example CVs (PDF)', type=['pdf'], accept_multiple_files=True)
    else:
        role = st.selectbox("Select Role Dataset", ["Software Engineer", "Data Analyst", "Cybersecurity Specialist"] )
    analyze_button = st.button('🔎 Analyze')

# Main logic
if analyze_button:
    if not job_file or not self_cv or (mode == "Upload New CVs" and not cvs_files):
        st.error('⚠️ Please upload the required files for the selected mode.')
    else:
        # Read inputs
        jd_text = job_file.read().decode('utf-8')
        self_text = extract_text_from_pdf(self_cv)

        # Prepare example results
        example_results = []
        if mode == "Use Existing CVs":
            data = json.load(open(os.path.join('data','precomputed_results.json')))
            role_key = role.lower().replace(' ', '_')
            for item in data.get(role_key, []):
                score = item['score']
                label = score_to_label(score)
                feedback_str = f"{label}: {item['reasons']}"
                example_results.append((score, feedback_str))
        else:
            raw_texts = [extract_text_from_pdf(f) for f in cvs_files]
            jd_emb, _ = aggregate_embeddings(jd_text, {'overall': jd_text})
            for text in raw_texts:
                segs = segment(text)
                cv_texts = {'overall': text, **{k:['\n'.join(v)] for k,v in segs.items()}}
                _, cv_emb = aggregate_embeddings(jd_text, cv_texts)
                score = score_cv(jd_emb, cv_emb)
                feedback_str = get_scale_feedback(score) + "\n" + get_example_feedback(jd_text, text)
                example_results.append((score, feedback_str))
            example_results = sorted(example_results, key=lambda x: x[0], reverse=True)[:5]

        # Display example rankings
        st.header('🏆 Example CVs Ranking')
        for idx, (score, feedback_str) in enumerate(example_results, start=1):
            with st.expander(f"Example #{idx} — Score: {score:.3f} ({score_to_label(score)})"):
                st.write(feedback_str)

        # Analyze self CV
        st.header('📝 Your CV Analysis')
        cols = st.columns([1,1])
        with cols[0]:
            st.subheader('📄 Job Description')
            st.write(jd_text)
        with cols[1]:
            st.subheader('📄 Your CV')
            st.write(self_text)

        # Score and label self CV
        jd_emb, _ = aggregate_embeddings(jd_text, {'overall': jd_text})
        _, cv_emb_self = aggregate_embeddings(jd_text, {'overall': self_text})
        your_score = score_cv(jd_emb, cv_emb_self)
        your_label = score_to_label(your_score)
        your_feedback = get_scale_feedback(your_score)

        st.subheader(f"🎯 Your Score: **{your_score:.3f}** ({your_label})")
        st.write(your_feedback)

        # Personalized detailed AI feedback
        st.header('💬 Detailed AI Feedback')
        feedback = get_self_feedback(jd_text, self_text)
        for k, v in feedback.items():
            st.markdown(f"**{k.replace('_',' ').title()}**")
            st.write(v)
