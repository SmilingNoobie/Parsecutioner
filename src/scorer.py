# ==================== src/scorer.py ====================
import torch
import torch.nn.functional as F

# Section weights
WEIGHTS = {
    'overall': 0.2,
    'skills': 0.5,
    'experience': 0.3,
    'education': 0.0,
}

# Creative rating scale: thresholds and labels
SCALE = [
    (0.00, 0.60, "Matchmaker Needed"),
    (0.60, 0.75, "Rising Star"),
    (0.75, 0.85, "Solid Contender"),
    (0.85, 0.95, "Top Performer"),
    (0.95, 1.01, "Perfect Fit")
]

# Feedback messages for each label
FEEDBACK_MESSAGES = {
    "Matchmaker Needed": "This CV requires significant improvements to align with the job requirements.",
    "Rising Star": "The candidate shows potential but needs to bridge some skill gaps.",
    "Solid Contender": "A strong candidate with most key skills; consider for interview.",
    "Top Performer": "An excellent match; likely to excel in the role.",
    "Perfect Fit": "Outstanding candidate; meets and exceeds all requirements."
}

def cosine_sim(a, b):
    return F.cosine_similarity(a, b, dim=0)


def score_cv(jd_emb, cv_embs: dict) -> float:
    total = WEIGHTS['overall'] * cosine_sim(jd_emb['overall'], cv_embs['overall']).item()
    for sec in ['skills', 'experience', 'education']:
        if sec in jd_emb and sec in cv_embs:
            total += WEIGHTS.get(sec, 0) * cosine_sim(jd_emb[sec], cv_embs[sec]).item()
    # clamp between 0 and 1
    return max(0.0, min(total, 1.0))


def score_to_label(score: float) -> str:
    for low, high, label in SCALE:
        if low <= score < high:
            return label
    return SCALE[-1][2]


def get_scale_feedback(score: float) -> str:
    label = score_to_label(score)
    return f"{label}: {FEEDBACK_MESSAGES[label]}"


def aggregate_embeddings(jd_text: str, cv_texts: dict):
    from src.encoder import embed
    jd_overall = embed([jd_text])[0]
    cv_overall = embed([cv_texts.get('overall','')])[0]
    jd_emb, cv_emb = {'overall': jd_overall}, {'overall': cv_overall}
    for sec, texts in cv_texts.items():
        if sec != 'overall':
            if isinstance(texts, str): texts = [texts]
            emb_list = embed(texts)
            if isinstance(emb_list, torch.Tensor): emb_list = [emb_list]
            cv_emb[sec] = torch.mean(torch.stack(tuple(emb_list)), dim=0)
    return jd_emb, cv_emb