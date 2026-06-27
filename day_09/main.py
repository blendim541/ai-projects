from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = FastAPI()

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="knowledge_base")


class IngestRequest(BaseModel):
    url: str


class SearchRequest(BaseModel):
    query: str
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


@app.get("/")
def root():
    return {"message": "AI Knowledge Base API is running"}


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


@app.post("/search")
def search(request: SearchRequest):
    try:
        results = collection.query(
            query_texts=[request.query],
            n_results=request.n_results
        )

        chunks = results["documents"][0]

        return {
            "query": request.query,
            "results": [{"rank": i + 1, "text": chunk[:300]} for i, chunk in enumerate(chunks)]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))