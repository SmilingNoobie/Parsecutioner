from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def embed(texts: list):
    model = get_model()
    return model.encode(texts, convert_to_tensor=True)
