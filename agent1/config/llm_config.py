import os
from dotenv import load_dotenv
from crewai import LLM
env_path = os.path.join(os.path.dirname(__file__),".env")
load_dotenv(env_path)
llm = LLM(
    model="gemini/gemini-flash-latest",
    api_key=os.getenv("GEMINI_API_KEY")
)