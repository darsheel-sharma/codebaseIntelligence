import os
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Codebase Intelligence API"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

settings = Settings()
