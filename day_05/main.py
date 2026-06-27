from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

notes = [
    "Cristiano Ronaldo scored 50 goals this season",
    "Python is a great programming language for beginners",
    "Muay Thai training improves footwork and striking power",
    "Machine learning models learn patterns from data",
    "BJJ focuses on ground fighting and submissions",
    "Real Madrid won the Champions League last year",
    "Neural networks are inspired by the human brain",
    "Kickboxing combines punches and kicks for full contact fighting",
    "Messi is considered one of the greatest footballers of all time",
    "Deep learning is a subset of machine learning",
]


def find_similar_notes(query, top_n=3):
    notes_formatted = "\n".join([f"{i + 1}. {note}" for i, note in enumerate(notes)])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are a semantic search engine. 
                The user will give you a search query and a list of notes.
                Return the numbers of the top most semantically similar notes to the query.
                Only return the numbers separated by commas, nothing else.
                Example: 1, 4, 7"""
            },
            {
                "role": "user",
                "content": f"Query: {query}\n\nNotes:\n{notes_formatted}\n\nReturn the top {top_n} most relevant note numbers."
            }
        ]
    )

    result = response.choices[0].message.content.strip()
    indices = [int(x.strip()) - 1 for x in result.split(",")]

    return [notes[i] for i in indices]


print("Personal Note Searcher")
print("-" * 40)

while True:
    query = input("Search (or 'quit' to exit): ")

    if query.lower() == "quit":
        print("Goodbye!")
        break

    results = find_similar_notes(query)
    print()
    print("Most relevant notes:")
    for i, note in enumerate(results):
        print(f"{i + 1}. {note}")
    print()