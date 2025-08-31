from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
from joblib import load
from typing import List
import app.services.hf_service as hf_service
from app.config import settings
from app.schemas.classify import ClassifyIn, ClassifyOut, BatchIn
from app.schemas.file_out import FileClassifyOut
from app.helpers.suggest_reply import suggest_reply
import pdfplumber
import io

router = APIRouter()

MODEL_PATH: Path = settings.MODEL_PATH
if not MODEL_PATH.exists():
    raise RuntimeError(f"Modelo não encontrado em {MODEL_PATH}. Rode: python scripts/train.py")
model = load(MODEL_PATH)

def _safe_decode_txt(raw: bytes) -> str:
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(enc)
        except Exception:
            continue
    return raw.decode("utf-8", errors="ignore")

def _extract_text_from_pdf(raw: bytes) -> str:
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        return "\n".join([(p.extract_text() or "") for p in pdf.pages]).strip()

@router.post("/classify", response_model=ClassifyOut)
def classify_email(payload: ClassifyIn):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Texto vazio.")
    try:
        if settings.USE_HF_CLASSIFIER:
            try:
                pred, confidence = hf_service.classify_with_hf(text)
            except Exception:
                proba_vec = model.predict_proba([text])[0]
                pred = model.predict([text])[0]
                confidence = float(max(proba_vec))
        else:
            proba_vec = model.predict_proba([text])[0]
            pred = model.predict([text])[0]
            confidence = float(max(proba_vec))

        if settings.USE_HF_REPLY:
            try:
                reply = hf_service.reply_with_hf(pred, text)
            except Exception:
                reply = suggest_reply(pred, text)
        else:
            reply = suggest_reply(pred, text)

        return {
            "category": pred,
            "confidence": round(confidence, 3),
            "suggestedReply": reply,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao classificar: {e}")

@router.post("/classify/batch", response_model=List[ClassifyOut])
def classify_batch(payload: BatchIn):
    texts = [t.strip() for t in payload.texts if t and t.strip()]
    if not texts:
        raise HTTPException(status_code=400, detail="Nenhum texto válido.")

    if settings.USE_HF_CLASSIFIER:
        results: List[ClassifyOut] = []
        for text in texts:
            try:
                pred, confidence = hf_service.classify_with_hf(text)
            except Exception:
                proba_vec = model.predict_proba([text])[0]
                pred = model.predict([text])[0]
                confidence = float(max(proba_vec))

            if settings.USE_HF_REPLY:
                try:
                    reply = hf_service.reply_with_hf(pred, text)
                except Exception:
                    reply = suggest_reply(pred, text)
            else:
                reply = suggest_reply(pred, text)

            results.append({
                "category": pred,
                "confidence": round(confidence, 3),
                "suggestedReply": reply,
            })
        return results

    probas = model.predict_proba(texts)
    preds = model.predict(texts)
    results: List[ClassifyOut] = []
    for text, pred, proba_vec in zip(texts, preds, probas):
        confidence = float(max(proba_vec))
        if settings.USE_HF_REPLY:
            try:
                reply = hf_service.reply_with_hf(pred, text)
            except Exception:
                reply = suggest_reply(pred, text)
        else:
            reply = suggest_reply(pred, text)

        results.append({
            "category": pred,
            "confidence": round(confidence, 3),
            "suggestedReply": reply,
        })
    return results

@router.post("/classify/upload", response_model=ClassifyOut)
async def classify_upload(file: UploadFile = File(...)):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")
    if len(raw) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo muito grande.")

    filename = (file.filename or "").lower()
    ctype = (file.content_type or "").lower()

    try:
        if filename.endswith(".txt") or "text/plain" in ctype:
            text = _safe_decode_txt(raw)
        elif filename.endswith(".pdf") or "application/pdf" in ctype:
            text = _extract_text_from_pdf(raw)
        else:
            raise HTTPException(status_code=415, detail="Tipo não suportado. Envie .txt ou .pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao ler arquivo: {e}")

    text = (text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Nenhum texto legível encontrado.")

    try:
        if settings.USE_HF_CLASSIFIER:
            try:
                pred, confidence = hf_service.classify_with_hf(text)
            except Exception:
                proba_vec = model.predict_proba([text])[0]
                pred = model.predict([text])[0]
                confidence = float(max(proba_vec))
        else:
            proba_vec = model.predict_proba([text])[0]
            pred = model.predict([text])[0]
            confidence = float(max(proba_vec))

        if settings.USE_HF_REPLY:
            try:
                reply = hf_service.reply_with_hf(pred, text)
            except Exception:
                reply = suggest_reply(pred, text)
        else:
            reply = suggest_reply(pred, text)

        return {
            "category": pred,
            "confidence": round(confidence, 3),
            "suggestedReply": reply,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao classificar: {e}")

@router.post("/classify/uploads", response_model=List[FileClassifyOut])
async def classify_multiple_uploads(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado.")

    results: List[FileClassifyOut] = []

    for f in files:
        filename = (f.filename or "arquivo")
        try:
            raw = await f.read()
            if not raw:
                results.append(FileClassifyOut(filename=filename, error="Arquivo vazio."))
                continue
            if len(raw) > settings.MAX_UPLOAD_BYTES:
                results.append(FileClassifyOut(filename=filename, error="Arquivo muito grande."))
                continue

            ctype = (f.content_type or "").lower()
            if filename.lower().endswith(".txt") or "text/plain" in ctype:
                text = _safe_decode_txt(raw)
            elif filename.lower().endswith(".pdf") or "application/pdf" in ctype:
                text = _extract_text_from_pdf(raw)
            else:
                results.append(FileClassifyOut(filename=filename, error="Tipo não suportado. Envie .txt ou .pdf"))
                continue

            text = (text or "").strip()
            if not text:
                results.append(FileClassifyOut(filename=filename, error="Nenhum texto legível encontrado."))
                continue

            if settings.USE_HF_CLASSIFIER:
                try:
                    pred, confidence = hf_service.classify_with_hf(text)
                except Exception:
                    proba_vec = model.predict_proba([text])[0]
                    pred = model.predict([text])[0]
                    confidence = float(max(proba_vec))
            else:
                proba_vec = model.predict_proba([text])[0]
                pred = model.predict([text])[0]
                confidence = float(max(proba_vec))

            if settings.USE_HF_REPLY:
                try:
                    reply = hf_service.reply_with_hf(pred, text)
                except Exception:
                    reply = suggest_reply(pred, text)
            else:
                reply = suggest_reply(pred, text)

            results.append(FileClassifyOut(
                filename=filename,
                category=pred,
                confidence=round(confidence, 3),
                suggestedReply=reply
            ))

        except Exception as e:
            results.append(FileClassifyOut(filename=filename, error=f"Falha ao processar: {e}"))

    return results
