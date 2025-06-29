#!/usr/bin/env python3
"""
Alpaca Trading MCP Server - Gold Standard Implementation

This is the main entry point for the Alpaca trading MCP server.
Following gold standard patterns for MCP development.
"""

import asyncio
import logging
from src.mcp_server.server import mcp
from src.mcp_server.config.settings import settings

def setup_logging():
    """Configure logging based on environment settings."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

async def main():
    """Main entry point for the MCP server."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {settings.server_name} MCP server...")
    logger.info(f"Paper trading mode: {settings.alpaca_paper_trade}")
    
    # Run the FastMCP server
    async with mcp:
        await mcp.run()

if __name__ == "__main__":
    asyncio.run(main())