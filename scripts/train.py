from pathlib import Path
import sys

import pandas as pd
from sklearn.model_selection import cross_val_score, train_test_split, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump
from app.nlp.preprocess import tokenize_pt

DATA_PATH = Path("data") 
CSV_PATH = DATA_PATH / "emails.csv" 
MODELS_DIR  = Path("app") / "models"
MODEL_PATH = MODELS_DIR / "model.joblib" 

def main():
    if not CSV_PATH.exists():
        sys.exit(f"[ERRO] Não encontrei o {CSV_PATH}."
                 "Crei a pasta 'data/' e o arquivo 'emails.csv' com as colunas text,label."
                 )
        
    try:
        df = pd.read_csv(CSV_PATH, encoding='utf-8')
    except Exception as e:
        sys.exit(f"[ERRO] Não consegui ler o {CSV_PATH}. Veja o erro: {e}\n"
                 "Verifique se a primeira linha é 'text,label' e se não há vírgulas sobrando no final."
                 )
    if "text" not in df.columns or "label" not in df.columns:
        sys.exit(f"[ERRO] O CSV precisa ter as colunas extamente: text,label")


    if df.empty:
        sys.exit(f"[ERRO] O CSV está vazio. Adicione dados para exemplo de treino no {CSV_PATH}")

    x = df["text"].astype(str)  
    y = df["label"].astype(str) 

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline(steps=[
            ("tfidf", TfidfVectorizer(
            lowercase=True,
            strip_accents='unicode', 
            ngram_range=(1,1),
            token_pattern=None,
            min_df=1,
            tokenizer=tokenize_pt,
        )),
        ("clf", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"))
    ])

    pipeline.fit(x_train, y_train)

    y_pred = pipeline.predict(x_test)

    cv = StratifiedKFold(n_splits=min(5, len(y)), shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, x, y, cv=cv, scoring="f1_macro")
    print(f"CV F1_macro (média ± desvio): {scores.mean():.3f} ± {scores.std():.3f}")

    print("\n=== Relatório de Classificação (TESTE) ===")
    print(classification_report(y_test, y_pred, digits=3, zero_division=0))

    print("=== Matriz de Confusão (linhas=verdade, colunas=previsto) ===")
    print(confusion_matrix(y_test, y_pred))

    MODELS_DIR.mkdir(parents=True, exist_ok=True) 
    dump(pipeline, MODEL_PATH, compress=3)
    print(f"\n[OK] Modelo treinado salvo em: {MODEL_PATH}")

    exemplo = "Poderiam me informar o status do chamado #123?"
    pred = pipeline.predict([exemplo])[0]
    proba = pipeline.predict_proba([exemplo]).max() 
    print(f"\nExemplo de previsão: => {exemplo}")
    print(f"Predição: {pred} | Confiança: {proba:.3f} ")

if __name__ == "__main__":
    main()
