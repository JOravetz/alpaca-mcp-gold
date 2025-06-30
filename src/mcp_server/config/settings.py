"""
Configuration management for Alpaca MCP server.
Follows gold standard patterns for environment-based configuration.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AlpacaSettings(BaseSettings):
    """Alpaca API configuration settings."""

    # Required Alpaca credentials
    api_key: str = Field(description="Alpaca API key")
    secret_key: str = Field(description="Alpaca secret key")
    paper_trade: bool = Field(default=True)

    # Optional Alpaca API URLs
    trade_api_url: Optional[str] = Field(default=None)
    trade_api_wss: Optional[str] = Field(default=None)
    data_api_url: Optional[str] = Field(default=None)
    stream_data_wss: Optional[str] = Field(default=None)

    model_config = {"env_file": ".env"}


class MCPSettings(BaseSettings):
    """MCP server configuration settings."""

    server_name: str = Field(default="alpaca-trading-gold")
    version: str = "1.0.0"
    log_level: str = Field(default="INFO")

    model_config = {"env_file": ".env"}


class Settings:
    """Combined application settings."""

    def __init__(self) -> None:
        # Initialize sub-settings with required values from env
        import os
        from dotenv import load_dotenv

        load_dotenv()

        self.alpaca = AlpacaSettings(
            api_key=os.getenv("ALPACA_API_KEY", ""),
            secret_key=os.getenv("ALPACA_SECRET_KEY", ""),
        )
        self.mcp = MCPSettings()

    # Expose commonly used settings at the top level
    @property
    def server_name(self) -> str:
        return self.mcp.server_name

    @property
    def log_level(self) -> str:
        return self.mcp.log_level

    @property
    def alpaca_api_key(self) -> str:
        return self.alpaca.api_key

    @property
    def alpaca_secret_key(self) -> str:
        return self.alpaca.secret_key

    @property
    def alpaca_paper_trade(self) -> bool:
        return self.alpaca.paper_trade


# Global settings instance
settings = Settings()

# Validate that required credentials are available
if not settings.alpaca_api_key or not settings.alpaca_secret_key:
    raise ValueError(
        "Alpaca API credentials not found in environment variables. "
        "Please set ALPACA_API_KEY and ALPACA_SECRET_KEY."
    )
