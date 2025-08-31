# Email Classifier

Classificador de e-mails (Produtivo/Improdutivo) com **sugestão de resposta automática**.  
Frontend estático (Vercel) + API em **FastAPI** (Render). Modelo baseline treinado com **TF-IDF + Regressão Logística** e opção de usar **Hugging Face** para zero-shot e geração de resposta.

- **App online (frontend):** https://email-classifier-rose.vercel.app  
- **API online (backend):** https://email-classifier-ysyc.onrender.com

---

## 👀 Visão Geral

- **Objetivo:** automatizar leitura/classificação de e-mails e sugerir respostas, liberando time de operação.
- **Categorias**
  - **Produtivo:** exige ação (status de chamado, reembolso, senha, etc.)
  - **Improdutivo:** mensagens de cortesia (felicitações, agradecimentos etc.)
- **Entradas suportadas:** texto colado, **.txt**, **.pdf** (upload único ou múltiplos).
- **Saída:** categoria, confiança (%), **resposta sugerida** (com botão “copiar”).

---

## 🧱 Arquitetura & Tecnologias

- **Backend**: FastAPI + Uvicorn/Gunicorn
  - Pipeline de treino: **TF-IDF + LogisticRegression**
  - Pré-processamento: stopwords, normalização, tokenização PT-BR
  - Rotas:
    - `POST /classify` (texto único)
    - `POST /classify/upload` (arquivo único .txt/.pdf)
    - `POST /classify/uploads` (múltiplos arquivos)
    - `GET /health` (status)
  - **Hugging Face** (opcional): zero-shot classification (XNLI) e geração de resposta (T5), com **fallback** para regras locais.
- **Frontend**: HTML + CSS + JS Vanilla (Vercel)
  - UI dark, toasts, barra de confiança, resultado em lote
  - **Mutuamente exclusivo**: se digitar texto, limpa arquivos; se anexar arquivos, limpa o texto.
- **Deploy**
  - **Frontend:** Vercel (estático)
  - **Backend:** Render (Web Service Python)

---

## 📁 Estrutura do Projeto

```
.
├── api/
│   └── index.py
├── app/
│   ├── main.py
│   ├── routes/
│   │   └── classify.py
│   ├── services/
│   │   ├── model_service.py
│   │   └── hf_service.py
│   ├── nlp/
│   │   └── preprocess.py
│   ├── models/
│   │   └── model.joblib
│   ├── config.py
│   └── tests/
├── scripts/
│   ├── train.py
│   └── predict.py
├── data/
│   └── emails.csv
├── index.html
├── style.css
├── main.js
├── requirements.txt
└── README.md
```

---

## ⚙️ Como rodar **localmente**

> Requisitos: **Python 3.11+**, **pip**

1) Clone e instale

```bash
git clone https://github.com/<seu-usuario>/email-classifier.git
cd email-classifier

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/Mac

pip install -r requirements.txt
```

2) Configure `.env`

```env
USE_HF_CLASSIFIER=false
USE_HF_REPLY=false
MODEL_PATH=app/models/model.joblib
MAX_UPLOAD_BYTES=3000000
APP_NAME=Email Classifier API
APP_ENV=local
```

3) Treine o modelo

```bash
python -m scripts.train
```

4) Suba a API

```bash
uvicorn app.main:app --reload
```

5) Abra o **frontend** (`index.html`) localmente.

---

## 🧪 Testes

```bash
pytest -q
```

---

## 🛣️ Endpoints

### `POST /classify`
Body:
```json
{ "text": "conteúdo do email..." }
```

Resposta:
```json
{
  "category": "Produtivo",
  "confidence": 0.82,
  "suggestedReply": "Olá! Obrigado pelo envio..."
}
```

### `POST /classify/upload`
- **Form-Data**: `file=@exemplo.pdf`

### `POST /classify/uploads`
- **Form-Data**: `files=@a.pdf`, `files=@b.txt`

### `GET /health`
```json
{ "status": "ok", "app_env": "local" }
```

---

## 🧠 Funcionamento Técnico

1. **Treino**: `scripts/train.py` → TF-IDF + LogisticRegression.
2. **Inferência**: API usa `predict` e `predict_proba`.
3. **Sugestão de Resposta**: via Hugging Face (opcional) ou heurísticas locais.

---

## 🌐 Deploy

- **Frontend:** Vercel (https://email-classifier-rose.vercel.app)
- **Backend:** Render (https://email-classifier-ysyc.onrender.com)

---

## 🎬 Vídeo (a ser gravado)

- 3–5 min mostrando UI, uploads, classificação e explicação técnica.

---

## 🧾 Licença
MIT — use livremente com créditos.
