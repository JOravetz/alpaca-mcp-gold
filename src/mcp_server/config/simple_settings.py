"""
Simple configuration management for Alpaca MCP server.
Using environment variables directly without pydantic-settings complexity.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Simple configuration management using environment variables."""
    
    def __init__(self):
        # Alpaca API settings
        self.alpaca_api_key = os.getenv("ALPACA_API_KEY", "")
        self.alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY", "")
        self.alpaca_paper_trade = os.getenv("ALPACA_PAPER_TRADE", "True").lower() == "true"
        
        # Optional Alpaca API URLs
        self.alpaca_trade_api_url = os.getenv("TRADE_API_URL")
        self.alpaca_trade_api_wss = os.getenv("TRADE_API_WSS")
        self.alpaca_data_api_url = os.getenv("DATA_API_URL")
        self.alpaca_stream_data_wss = os.getenv("STREAM_DATA_WSS")
        
        # MCP Server settings
        self.server_name = os.getenv("MCP_SERVER_NAME", "alpaca-trading-gold")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.version = "1.0.0"

    def validate(self):
        """Validate that required settings are available."""
        missing = []
        
        if not self.alpaca_api_key:
            missing.append("ALPACA_API_KEY")
        
        if not self.alpaca_secret_key:
            missing.append("ALPACA_SECRET_KEY")
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Please update your .env file with valid Alpaca API credentials."
            )
        
        # Check for demo values
        if self.alpaca_api_key == "demo_key_please_replace" or self.alpaca_secret_key == "demo_secret_please_replace":
            raise ValueError(
                "Demo credentials detected. "
                "Please update your .env file with valid Alpaca API credentials."
            )

# Global settings instance
settings = Settings()

# For development/testing, allow demo credentials
try:
    settings.validate()
except ValueError as e:
    if any(key in str(e) for key in ["demo_key_please_replace", "demo_secret_please_replace"]):
        print(f"Warning: {e}")
        print("The server will start but Alpaca API calls will fail.")
        print("Please update your .env file with valid credentials for actual trading.")
    else:
        raise