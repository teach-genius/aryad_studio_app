from dotenv import load_dotenv
from bytez import Bytez
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
import re
import os    

load_dotenv()

API_KEY = os.getenv("BYTEZ_API_KEY")
sdk = Bytez(API_KEY)
model = sdk.model("Qwen/Qwen3-4B-Instruct-2507")


SERVICE_UNAVAILABLE_MESSAGE = (
    "Notre assistant intelligent est temporairement indisponible. "
    "Merci de nous contacter — nous reviendrons vers vous rapidement."
)

def chatAryadResponse(messages: str) -> str:
    try:
        results = model.run(messages)
        cleaned = re.sub(r'<think>.*?</think>\s*', '',results.output['content'], flags=re.DOTALL)
        try:
            return cleaned
        except (AttributeError, IndexError, TypeError):
            return SERVICE_UNAVAILABLE_MESSAGE

    except Exception as e:
        print(f'error :{e}')
        return SERVICE_UNAVAILABLE_MESSAGE

#creation reactAgent
def createReactAgent(llm,prompt_system:str,liste_tools: list=[]):
    return create_agent(
    model=llm,
    tools=liste_tools,
    system_prompt=prompt_system)

#Inférence ReactAgent
def call_ReactAgent(agent,message):
    result = agent.invoke({
    "messages": [
        HumanMessage(
            content=message
            )
        ]
    })
    last_message = result["messages"][-1].content
    if isinstance(last_message, list):
        return last_message[0]["text"]
    else:
        return last_message