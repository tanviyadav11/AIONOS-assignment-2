"""
One-Command Runner for Veridian Corp IT Support Agent.
Starts the FastAPI application and displays accessible local URLs.
"""

import sys
import uvicorn
from app.config import settings

def main():
    print("=" * 70)
    print("Starting Veridian Corp IT Support Agent (AIONOS Assignment 2)")
    print(f"Company: {settings.COMPANY_NAME}")
    print(f"Active Timeframe: {settings.EXERCISE_WEEK}")
    print(f"Server URL: http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs:   http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 70)
    print("Press CTRL+C to stop the server.\n")

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
