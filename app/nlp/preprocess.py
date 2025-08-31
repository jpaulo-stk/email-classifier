# app/nlp/preprocess.py
import re
from typing import List
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

_PT_STOPWORDS = set(stopwords.words("portuguese"))
_STEMMER = SnowballStemmer("portuguese")

_TOKEN_RE = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+")

def tokenize_pt(text: str) -> List[str]:
    if not text:
        return []
    text = text.lower()
    tokens = _TOKEN_RE.findall(text)
    filtered = []
    for tok in tokens:
        if tok in _PT_STOPWORDS:
            continue
        stem = _STEMMER.stem(tok)
        filtered.append(stem)
    return filtered
