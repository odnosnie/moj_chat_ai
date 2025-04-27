from fastapi import FastAPI
from pydantic import BaseModel
from rapidfuzz import fuzz, process

# Funkcja wczytująca wiedzę z pliku
def wczytaj_wiedze(path):
    qna = {}  # Inicjujemy pusty słownik na pytania i odpowiedzi
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Wczytujemy wszystkie linie z pliku
    question = None
    answer = None
    for line in lines:
        line = line.strip()  # Usuwamy zbędne białe znaki
        if line.lower().startswith('question:'):  # Sprawdzamy, czy to pytanie
            question = line[len('question:'):].strip()  # Pobieramy pytanie
        elif line.lower().startswith('answer:'):  # Sprawdzamy, czy to odpowiedź
            answer = line[len('answer:'):].strip()  # Pobieramy odpowiedź
        if question and answer:  # Jeśli mamy pytanie i odpowiedź
            qna[question] = answer  # Dodajemy do słownika
            question = None  # Resetujemy zmienne na kolejny wpis
            answer = None
    return qna  # Zwracamy wczytaną wiedzę

# Inicjalizujemy FastAPI
app = FastAPI()

# Ładujemy wiedzę (ścieżka do pliku)
path_to_file = 'wiedza.txt'
wiedza = wczytaj_wiedze(path_to_file)  # Wczytujemy dane

# Pytania wczytane z pliku
pytania_lista = list(wiedza.keys())

# Model zapytania
class Query(BaseModel):
    question: str

# Endpoint /ask
@app.post("/ask")
async def ask_question(query: Query):
    user_question = query.question.lower()
    odpowiedzi = []
    slowa_kluczowe = user_question.replace(",", "").split()  # Rozdzielamy pytanie na słowa
    for slowo in slowa_kluczowe:
        if len(slowo) < 3:
            continue  # Pomijamy zbyt krótkie słowa
        wyniki = process.extract(slowo, pytania_lista, scorer=fuzz.partial_ratio, limit=2)  # Wyszukiwanie w pytaniach
        for pytanie, score, _ in wyniki:
            if score >= 70:  # Tylko odpowiedzi o wysokim dopasowaniu
                odpowiedzi.append(wiedza[pytanie])
    odpowiedzi = list(set(odpowiedzi))  # Usuwamy duplikaty
    if odpowiedzi:
        return {"answer": odpowiedzi}
    else:
        return {"answer": "Brak odpowiedzi w danych."}
