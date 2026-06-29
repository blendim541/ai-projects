from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import requests
from bs4 import BeautifulSoup
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI(title="AI Summarization Service")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="knowledge_base")


class IngestRequest(BaseModel):
    url: str


class AskRequest(BaseModel):
    question: str
    n_results: int = 3


def fetch_and_clean(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text()
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()


def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def generate_answer(question, context_chunks):
    context = "\n\n".join(context_chunks)

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful AI assistant. 
                Answer the user's question based only on the context provided.
                If the answer is not in the context, say 'I could not find that information in the document.'
                Keep your answer clear and concise."""
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]
    )
    return response.choices[0].message.content


@app.get("/")
def root():
    return {"message": "AI Summarization Service is running"}


@app.post("/ingest")
def ingest(request: IngestRequest):
    try:
        text = fetch_and_clean(request.url)
        chunks = chunk_text(text)

        existing = collection.get()
        start_id = len(existing["ids"]) + 1
        ids = [str(start_id + i) for i in range(len(chunks))]

        collection.add(documents=chunks, ids=ids)

        return {
            "message": "URL ingested successfully",
            "url": request.url,
            "chunks_added": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask(request: AskRequest):
    try:
        results = collection.query(
            query_texts=[request.question],
            n_results=request.n_results
        )

        context_chunks = results["documents"][0]
        answer = generate_answer(request.question, context_chunks)

        return {
            "question": request.question,
            "answer": answer,
            "sources_used": len(context_chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))