from fastapi import FastAPI
from pydantic import BaseModel
from rapidfuzz import fuzz, process
import os

# Twoje API FastAPI
app = FastAPI()

# Model zapytania
class Query(BaseModel):
    question: str

# Pytanie i odpowiedzi
path_to_file = 'wiedza_wygenerowana.txt'

def wczytaj_wiedze(path):
    # ... (Twoja logika wczytywania danych)
    return qna

wiedza = wczytaj_wiedze(path_to_file)
pytania_lista = list(wiedza.keys())

# Endpoint /ask
@app.post("/ask")
async def ask_question(query: Query):
    user_question = query.question.lower()
    odpowiedzi = []
    slowa_kluczowe = user_question.replace(",", "").split()
    for slowo in slowa_kluczowe:
        if len(slowo) < 3:
            continue
        wyniki = process.extract(slowo, pytania_lista, scorer=fuzz.partial_ratio, limit=2)
        for pytanie, score, _ in wyniki:
            if score >= 70:
                odpowiedzi.append(wiedza[pytanie])
    odpowiedzi = list(set(odpowiedzi))
    if odpowiedzi:
        return {"answer": odpowiedzi}
    else:
        return {"answer": "Brak odpowiedzi w danych."}
