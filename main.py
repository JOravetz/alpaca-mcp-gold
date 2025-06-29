#!/usr/bin/env python3
"""
Alpaca Trading MCP Server - Gold Standard Implementation

This is the main entry point for the Alpaca trading MCP server.
Following gold standard patterns for MCP development.
"""

import asyncio
import logging
import sys
from src.mcp_server.server import mcp
from src.mcp_server.config.simple_settings import settings

def setup_logging():
    """Configure logging based on environment settings."""
    # For MCP servers, we need to log to stderr or a file, not stdout
    # stdout is reserved for MCP protocol communication
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Log to stderr instead of stdout
    )

def main():
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {settings.server_name} MCP server...")
    logger.info(f"Paper trading mode: {settings.alpaca_paper_trade}")
    
    # Test Alpaca connection at startup
    try:
        from src.mcp_server.models.alpaca_clients import AlpacaClientManager
        client = AlpacaClientManager.get_trading_client()
        account = client.get_account()
        logger.info(f"✓ Connected to Alpaca API - Account: {account.id}")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Alpaca API: {e}")
        logger.error("Server will still start but API calls will fail")
    
    # Run the FastMCP server (this starts its own event loop)
    mcp.run()

if __name__ == "__main__":
    main()