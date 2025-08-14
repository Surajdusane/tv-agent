from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

# Initialize Groq LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)
