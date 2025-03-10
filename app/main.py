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

# Import MongoDB class for database connection
from app.database.mongodb import MongoDB

# Import market indices router
from app.api.v1.MarketIndices.router import router as market_router
# Import treemap router
from app.api.v1.treemap.router import router as treemap_router
# Import treemap_color router
from app.api.v1.treemap_color.router import router as treemap_color_router
# import market indices adjust day
from app.api.v1.marketindices_adjustday.router import router as marketindices_adjustday_router
# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="ChatBot Finance Backend")

# Initialize telegram bot and get app instances
telegram_app, flask_app = initialize_bot()

# Include market indices router
app.include_router(market_router, prefix="/api/v1/market", tags=["Market Indices"])
# Include treemap router
app.include_router(treemap_router, prefix="/api/v1/treemap", tags=["Treemap"])
# Include treemap_color router
app.include_router(treemap_color_router, prefix="/api/v1")
# Include market indices adjust day router
app.include_router(marketindices_adjustday_router, prefix="/api/v1/market-adjust-indices")
# Database startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await MongoDB.connect()
    print("✅ Connected to MongoDB database")

@app.on_event("shutdown")
async def shutdown_db_client():
    await MongoDB.close()
    print("✅ Closed MongoDB database connection")

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