import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="deepseek-r1-distill-llama-70b",
    temperature=0,
    max_tokens=None,
    reasoning_format="parsed",
    timeout=None,
    max_retries=2,
    api_key=groq_api_key,
    
    # other params...
)

message = "how are you?"

response = llm.invoke(message)

print(f"Response: {response}")