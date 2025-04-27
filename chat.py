from fastapi import FastAPI, Request
from pydantic import BaseModel
from rapidfuzz import fuzz, process
from starlette.middleware.base import BaseHTTPMiddleware

# Middleware, żeby naprawić problem 411
class ChunkedMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if "transfer-encoding" in request.headers and request.headers["transfer-encoding"] == "chunked":
            request._receive = self._get_chunked_body(request)
        response = await call_next(request)
        return response

    async def _get_chunked_body(self, request):
        body = await request.body()
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}
        return receive

# --- FastAPI app ---
app = FastAPI()
app.add_middleware(ChunkedMiddleware)

# Model zapytania
class Query(BaseModel):
    question: str

# Twoja wiedza:
path_to_file = 'wiedza.txt'
def wczytaj_wiedze(path):
    qna = {}
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    question = None
    answer = None
    for line in lines:
        line = line.strip()
        if line.lower().startswith('question:'):
            question = line[len('question:'):].strip()
        elif line.lower().startswith('answer:'):
            answer = line[len('answer:'):].strip()
        if question and answer:
            qna[question] = answer
            question = None
            answer = None
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
