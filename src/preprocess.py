import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# ensure NLTK data downloaded
nltk.download('punkt')
nltk.download('stopwords')

STOP_WORDS = set(stopwords.words('english'))

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def tokenize(text: str) -> list:
    tokens = word_tokenize(text)
    return [tok for tok in tokens if tok not in STOP_WORDS]


def preprocess(text: str) -> list:
    norm = normalize_text(text)
    tokens = tokenize(norm)
    return tokens