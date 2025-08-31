import re
import unicodedata

import nltk
from nltk.corpus import stopwords

def _ensure_stopwords_pt():
    try:
        _ = stopwords.words("portuguese")
    except LookupError:
        nltk.download("stopwords")
    return set(stopwords.words("portuguese"))

STOP_PT = _ensure_stopwords_pt()

_WORD_RE = re.compile(r"\b[\w\-]+\b", flags=re.UNICODE)

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower()

def tokenize_pt(text: str) -> list[str]:
    text = normalize(text)
    tokens = _WORD_RE.findall(text)
    return [t for t in tokens if t not in STOP_PT and len(t) > 1]
