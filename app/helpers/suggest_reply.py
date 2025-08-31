from app.enums.common import Category

PRODUCTIVE = Category.productive

def suggest_reply(category: Category, text: str) -> str:
    t = text.lower()
    if category == PRODUCTIVE:
        if any(k in t for k in ["status", "andamento", "progresso", "chamado", "ticket"]):
            return ("Olá! Recebemos sua solicitação de status. "
                    "Estamos verificando e retornamos em breve. "
                    "Se possível, informe o número do chamado/caso.")
        if any(k in t for k in ["relatório", "anexo", "arquivo"]):
            return ("Olá! Obrigado pelo envio. Confirmamos o recebimento do documento. "
                    "Vamos analisar e retornamos até o próximo dia útil.")
        if any(k in t for k in ["senha", "acesso", "login"]):
            return ("Olá! Para resetar sua senha, confirme o e-mail cadastrado e o ID interno (se houver).")
        if any(k in t for k in ["computador", "máquina", "pc", "notebook"]):
            return ("Olá! Para ajudar no diagnóstico do computador, informe modelo, mensagem de erro e se já reiniciou.")
        return ("Olá! Sua solicitação foi recebida. Poderia detalhar um pouco mais o pedido?")
    if any(k in t for k in ["parabéns", "feliz", "agrade", "obrigado", "obrigada"]):
        return ("Muito obrigado pela mensagem! Ficamos à disposição. Ótimo dia!")
    return ("Agradecemos sua mensagem. Caso necessite de suporte, estamos à disposição!")
