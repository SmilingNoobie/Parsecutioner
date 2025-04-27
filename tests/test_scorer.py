from src.scorer import cosine_sim, score_cv, aggregate_embeddings

def test_scoring():
    jd='python'
    cv='python'
    jd_emb,cv_emb=aggregate_embeddings(jd,{'overall':cv})
    assert score_cv(jd_emb,cv_emb)>0.9
