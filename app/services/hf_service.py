from typing import Tuple, List, Literal
from app.config import settings
from app.enums.common import Category


PRODUCTIVE = Category.productive
UNPRODUCTIVE = Category.unproductive

try:
    from huggingface_hub import InferenceClient
except Exception:
    InferenceClient = None

_LABELS: List[str] = [PRODUCTIVE, UNPRODUCTIVE]

def _client():
    if not settings.HF_API_KEY or InferenceClient is None:
        return None
    return InferenceClient(api_key=settings.HF_API_KEY)

def classify_with_hf(text: str) -> Tuple[str, float]:
    client = _client()
    if client is None:
        raise RuntimeError("HF Inference indisponível")

    model_id = settings.HF_ZS_MODEL
    hypothesis = "Este email é {}."

    resp = client.zero_shot_classification(
        text,
        labels=_LABELS,
        multi_label=False,
        model=model_id,
        hypothesis_template=hypothesis,
    )
    labels = resp.get("labels") or []
    scores = resp.get("scores") or []
    if not labels or not scores:
        raise RuntimeError("Resposta HF vazia")

    best_idx = int(max(range(len(scores)), key=lambda i: scores[i]))
    category = labels[best_idx]
    confidence = float(scores[best_idx])

    if category.lower().startswith("produt"):
        category = PRODUCTIVE
    else:
        category = UNPRODUCTIVE

    return category, confidence

def reply_with_hf(category: Literal["Produtivo","Improdutivo"], text: str) -> str:
    client = _client()
    if client is None:
        raise RuntimeError("HF Inference indisponível")

    model_id = settings.HF_REPLY_MODEL
    prompt = (
        "Escreva uma resposta curta (1-3 frases), profissional e clara em PT-BR "
        f"para um e-mail classificado como '{category}'. "
        "Se for 'Produtivo', peça/valide dados faltantes e informe o próximo passo breve. "
        "Se for 'Improdutivo', agradeça cordialmente e encerre. "
        "Texto do e-mail:\n"
        f"---\n{text}\n---\n"
        "Resposta:"
    )

    out = client.text_generation(
        prompt,
        model=model_id,
        max_new_tokens=120,
        temperature=0.2,
        repetition_penalty=1.1,
        do_sample=True,
        return_full_text=False,
    )
    if isinstance(out, dict):
        generated = out.get("generated_text", "")
    else:
        generated = str(out)

    return (generated or "").strip()
