import requests
from bs4 import BeautifulSoup
import os
import json
import re


def fetch_page(url):
    print(f"Fetching: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    return response.text


def clean_text(html):
    print("Cleaning text...")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text()
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    text = text.strip()

    return text


def chunk_text(text, chunk_size=500):
    print("Chunking text...")
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += 1

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def save_chunks(chunks, output_file):
    print(f"Saving {len(chunks)} chunks...")
    data = {
        "total_chunks": len(chunks),
        "chunks": [{"id": i + 1, "text": chunk} for i, chunk in enumerate(chunks)]
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved to {output_file}")


def run_pipeline(url):
    html = fetch_page(url)
    text = clean_text(html)
    chunks = chunk_text(text)

    output_file = os.path.join(os.path.dirname(__file__), "output.json")
    save_chunks(chunks, output_file)

    print()
    print(f"Pipeline complete!")
    print(f"Total characters: {len(text)}")
    print(f"Total chunks: {len(chunks)}")
    print()
    print("Preview of first chunk:")
    print("-" * 40)
    print(chunks[0])


url = input("Enter a URL to process: ")
run_pipeline(url)