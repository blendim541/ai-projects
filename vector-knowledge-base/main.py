import chromadb
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))


def load_chunks(json_file):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["chunks"]


def build_knowledge_base(chunks):
    print("Building knowledge base...")
    client = chromadb.Client()

    collection = client.create_collection(name="knowledge_base")

    documents = [chunk["text"] for chunk in chunks]
    ids = [str(chunk["id"]) for chunk in chunks]

    collection.add(
        documents=documents,
        ids=ids
    )

    print(f"Added {len(documents)} chunks to the knowledge base.")
    return collection


def search(collection, query, n_results=3):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0]


json_file = os.path.join(os.path.dirname(__file__), '..', 'web-scraper-etl', 'output.json')
chunks = load_chunks(json_file)
collection = build_knowledge_base(chunks)

print()
print("Knowledge Base ready! Ask anything about the document.")
print("-" * 40)

while True:
    query = input("Search (or 'quit' to exit): ")

    if query.lower() == "quit":
        print("Goodbye!")
        break

    results = search(collection, query)
    print()
    print("Most relevant chunks:")
    print("-" * 40)
    for i, result in enumerate(results):
        print(f"{i + 1}. {result[:200]}...")
        print()