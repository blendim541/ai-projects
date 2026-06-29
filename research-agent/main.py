from groq import Groq
from dotenv import load_dotenv
import os
import wikipediaapi

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
wiki = wikipediaapi.Wikipedia(language='en', user_agent='research-agent/1.0')


def search_wikipedia(topic):
    print(f"  → Searching Wikipedia for: {topic}")
    page = wiki.page(topic)
    if not page.exists():
        return None
    return page.text[:3000]


def decide_next_action(topic, gathered_info):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a research agent. You decide what action to take next.\nAvailable actions:\n- SEARCH: search Wikipedia for more information\n- SUMMARIZE: you have enough information, create a final summary\n\nIMPORTANT: When searching, use short exact Wikipedia page titles like 'Artificial intelligence' or 'Machine learning' not long sentences.\n\nRespond in exactly this format:\nACTION: SEARCH or SUMMARIZE\nQUERY: the search term if action is SEARCH, or NONE if SUMMARIZE"
            },
            {
                "role": "user",
                "content": f"Research topic: {topic}\n\nInformation gathered so far:\n{gathered_info if gathered_info else 'Nothing yet'}"
            }
        ]
    )
    return response.choices[0].message.content


def create_summary(topic, gathered_info):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a research assistant.\nCreate a clear, structured research summary from the information provided.\nFormat it with these sections:\n- Overview\n- Key Facts\n- Important Details\n- Conclusion"
            },
            {
                "role": "user",
                "content": f"Topic: {topic}\n\nResearch gathered:\n{gathered_info}"
            }
        ]
    )
    return response.choices[0].message.content


def parse_action(response_text):
    lines = response_text.strip().split('\n')
    action = ""
    query = ""
    for line in lines:
        if line.startswith("ACTION:"):
            action = line.replace("ACTION:", "").strip()
        if line.startswith("QUERY:"):
            query = line.replace("QUERY:", "").strip()
    return action, query


def run_agent(topic):
    print(f"\nResearch Agent starting on: {topic}")
    print("-" * 40)

    gathered_info = ""
    max_steps = 3
    step = 0

    while step < max_steps:
        step += 1
        print(f"\nStep {step}:")

        decision = decide_next_action(topic, gathered_info)
        action, query = parse_action(decision)

        print(f"  → Agent decided: {action}")

        if action == "SEARCH":
            info = search_wikipedia(query)
            if info:
                gathered_info += f"\n\nFrom Wikipedia ({query}):\n{info}"
                print(f"  → Got {len(info)} characters of information")
            else:
                print(f"  → Nothing found for: {query}")

        elif action == "SUMMARIZE":
            print(f"  → Creating final summary...")
            summary = create_summary(topic, gathered_info)
            return summary

    print("\n  → Max steps reached, summarizing...")
    return create_summary(topic, gathered_info)


print("AI Research Agent")
print("=" * 40)

while True:
    topic = input("\nEnter a research topic (or 'quit' to exit): ")

    if topic.lower() == "quit":
        print("Goodbye!")
        break

    result = run_agent(topic)
    print("\n" + "=" * 40)
    print("RESEARCH SUMMARY")
    print("=" * 40)
    print(result)