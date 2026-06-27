from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

conversation_history = [
    SystemMessage(content="You are a helpful research assistant. Answer questions clearly and remember the context of our conversation.")
]

def chat(user_message):
    conversation_history.append(HumanMessage(content=user_message))
    response = llm.invoke(conversation_history)
    conversation_history.append(AIMessage(content=response.content))
    return response.content

print("Research Assistant")
print("I remember our entire conversation.")
print("-" * 40)

while True:
    user_input = input("You: ")

    if user_input.lower() == "quit":
        print("Goodbye!")
        break

    response = chat(user_input)
    print(f"Assistant: {response}")
    print()