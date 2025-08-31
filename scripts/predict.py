from pathlib import Path
from joblib import load
import sys
from app.enums.common import Category

MODEL_PATH = Path("app") / "models" / "model.joblib"

PRODUCTIVE = Category.productive

def suggest_reply(category: Category, text: str) -> str:
    t = text.lower()

    if category == PRODUCTIVE:
        if any(k in t for k in ["status", "andamento", "progresso", "chamado", "ticket"]):
            return ("Olá! Recebemos sua solicitação de status. "
                    "Estamos verificando e retornamos com uma atualização em breve. "
                    "Se possível, informe o número do chamado/caso para agilizar.")
        if any(k in t for k in ["relatório", "anexo", "arquivo"]):
            return ("Olá! Obrigado pelo envio. Confirmamos o recebimento do documento. "
                    "Vamos analisar e retornamos até o próximo dia útil. Precisa de algo específico no relatório?")
        if any(k in t for k in ["senha", "acesso", "login"]):
            return ("Olá! Para resetar sua senha, confirme: e-mail cadastrado e ID interno (se houver). "
                    "Assim que recebermos, envio o procedimento de redefinição com segurança.")
        if any(k in t for k in ["computador", "máquina", "pc", "notebook"]):
            return ("Olá! Para ajudar no diagnóstico do computador, informe: modelo, mensagem de erro exibida, "
                    "e se já tentou reiniciar/atualizar. Podemos agendar suporte remoto.")
        return ("Olá! Sua solicitação foi recebida. Poderia detalhar um pouco mais o pedido "
                "(número do caso, contexto e objetivo)? Assim agilizamos o retorno.")
    
    if any(k in t for k in ["parabéns", "feliz", "agrade", "obrigado", "obrigada"]):
        return ("Muito obrigado pela mensagem! Ficamos à disposição sempre que precisar. Tenha um ótimo dia!")
    return ("Agradecemos sua mensagem. Caso necessite de suporte ou tenha alguma demanda, "
            "é só nos informar. Estamos à disposição!")

def load_model():
    if not MODEL_PATH.exists():
        sys.exit(f"[ERRO] Modelo não encontrado em {MODEL_PATH}. Rode antes: python scripts/train.py")
    return load(MODEL_PATH)

def predict_texts(model, texts):
    probas = model.predict_proba(texts)
    preds = model.predict(texts)

    results = []
    for text, pred, proba_vec  in zip(texts, preds, probas):
        confidence = float(max(proba_vec))
        results.append({
            "text": text,
            "category": pred,
            "confidence": round(confidence, 3),
            "suggestedReply": suggest_reply(pred, text),
        })
    return results

def main():
    model = load_model()

    examples = [
        "Feliz natal a todos, obrigado!",
        "Poderiam me atualizar o status do meu chamado?",
        "Segue anexo o relatório mensal, confirmem recebimento por favor.",
        "Parabéns pela promoção!",
        "Ajuda com o computador: não está ligando.",
    ]

    results = predict_texts(model, examples)

    print("\n=== Previsões ===")
    for r in results:
        print(f"- Texto: {r['text']}")
        print(f"  Categoria: {r['category']} | Confiança: {r['confidence']}")
        print(f"  Sugestão: {r['suggestedReply']}")
        print()


if __name__ == "__main__":
    main()