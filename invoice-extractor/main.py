from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_invoice_data(raw_text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """"You are a job application data extractors. 
                Extract the following fields from the text the user provides:
                - Candidate Name
                - Position Applied For
                - Years Of Experience
                - Email

                Always respond in exactly this format:
                Candidate Name: ...
                Position Applied For: ...
                Years Of Experience: ...
                Email: ...

                If a field is not found, write N/A for that field."""
            },
            {
                "role": "user",
                "content": raw_text
            }
        ]
    )
    return response.choices[0].message.content


print("Invoice Data Extractor")
print("-" * 40)

while True:
    print("Paste your invoice text below and press Enter twice when done (or type 'quit' to exit):")
    print()

    lines = []
    while True:
        line = input()
        if line == "":
            break
        if line.lower() == "quit":
            print("Goodbye!")
            exit()
        lines.append(line)

    raw_text = "\n".join(lines)

    print()
    print("Extracted Data:")
    print("-" * 40)
    result = extract_invoice_data(raw_text)
    print(result)
    print()