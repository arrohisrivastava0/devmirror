from dotenv import load_dotenv
import os

load_dotenv()
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is missing from your .env file")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from your .env file")