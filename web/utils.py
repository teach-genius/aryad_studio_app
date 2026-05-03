from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
import re
import os

load_dotenv()

llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    temperature=0.7
)

SERVICE_UNAVAILABLE_MESSAGE = (
    "Notre assistant intelligent est temporairement indisponible. "
    "Merci de nous contacter — nous reviendrons vers vous rapidement."
)

def chatAryadResponse(messages: list) -> str:
    try:
        response = llm.invoke(messages)
        cleaned = re.sub(r'<tool_call>.*?</tool_call>\s*', '', response.content, flags=re.DOTALL)
        return cleaned
    except Exception as e:
        print(f'error : {e}')
        return SERVICE_UNAVAILABLE_MESSAGE