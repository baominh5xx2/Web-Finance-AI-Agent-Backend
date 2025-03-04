import sys
import os
from pathlib import Path

# Add the project root directory to Python path
root_dir = str(Path(__file__).parent)
sys.path.insert(0, root_dir)

from fastapi import FastAPI
from app.api.v1.Chatbot.main import initialize_bot, flask_app, run_flask
import threading
import uvicorn
from dotenv import load_dotenv

# Import router for Market Indices
from app.api.v1.MarketIndices.router import router as market_indices_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="ChatBot Finance Backend")

# Register the router
app.include_router(market_indices_router, prefix="/api/v1")

# Initialize telegram bot and get app instances
telegram_app, flask_app = initialize_bot()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "ChatBot Finance Backend is running"}

@app.get("/chatbot")
def chatbot_status():
    return {"status": "ok", "message": "Telegram Bot is running"}

def start_telegram_bot():
    """Start the Telegram bot in a separate thread"""
    print("🚀 Khởi động Telegram Bot...")
    telegram_app.run_polling()

if __name__ == "__main__":
    # Check if webhook mode is enabled
    use_webhook = os.getenv("USE_WEBHOOK", "False").lower() == "true"
    
    # Start Telegram bot in a separate thread
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()
    
    # Start webhook server if needed
    if use_webhook:
        webhook_thread = threading.Thread(target=run_flask, daemon=True)
        webhook_thread.start()
    
    # Start the FastAPI application
    port = int(os.getenv("PORT", 8000))
    print(f"✅ Starting FastAPI server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)