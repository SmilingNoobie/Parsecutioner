from src.preprocess import normalize_text, tokenize

def test_normalize_and_tokenize():
    text = 'Hello, World!'
    norm = normalize_text(text)
    tokens = tokenize(norm)
    assert 'hello' in tokens and 'world' in tokens