import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Veridian Corp IT Support Agent"
    VERSION: str = "2.0.0"
    COMPANY_NAME: str = "Veridian Corp"
    EXERCISE_WEEK: str = "Mon 21 Sep 2026 – Fri 25 Sep 2026"
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "hybrid_deterministic")  # "hybrid_deterministic", "claude", "gemini", "openai"
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

settings = Settings()
