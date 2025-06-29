"""
Main MCP server implementation following gold standard patterns.
Central registration point for all tools, resources, and prompts.
"""

import logging
from mcp.server.fastmcp import FastMCP
from .config.settings import settings

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.server_name,
    version="1.0.0"
)

logger = logging.getLogger(__name__)

# Import all tool functions
from .tools.account_tools import (
    get_account_info,
    get_positions,
    get_open_position,
    get_portfolio_summary
)

from .tools.market_data_tools import (
    get_stock_quote,
    get_stock_trade,
    get_stock_snapshot,
    get_historical_bars
)

from .tools.order_management_tools import (
    place_market_order,
    place_limit_order,
    place_stop_loss_order,
    get_orders,
    cancel_order
)

from .tools.resource_mirror_tools import (
    resource_account_info,
    resource_account_positions,
    resource_account_orders,
    resource_portfolio_summary,
    resource_portfolio_entities,
    resource_symbols_active,
    resource_symbols_count,
    resource_system_health,
    resource_system_memory,
    resource_system_status
)

# Import resource function
from .resources.trading_resources import get_trading_resource

# Import prompt functions
from .prompts.trading_prompts import (
    portfolio_first_look,
    trading_strategy_workshop,
    market_analysis_session,
    list_mcp_capabilities
)

# Register all tools following gold standard patterns
logger.info("Registering MCP tools...")

# Account Management Tools
@mcp.tool()
async def get_account_info_tool() -> dict:
    """
    Retrieves and formats the current account information including balances and status.
    
    Returns:
        Dict containing account details including buying power, cash, portfolio value, equity, and trading status
    """
    return await get_account_info()

@mcp.tool()
async def get_positions_tool() -> dict:
    """
    Retrieves and formats all current positions in the portfolio.
    
    Returns:
        Dict containing details of all open positions with P&L analysis and adaptive insights
    """
    return await get_positions()

@mcp.tool()
async def get_open_position_tool(symbol: str) -> dict:
    """
    Retrieves and formats details for a specific open position.
    
    Args:
        symbol: The symbol name of the asset to get position for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing position details with market value, P&L, and role analysis
    """
    return await get_open_position(symbol)

@mcp.tool()
async def get_portfolio_summary_tool() -> dict:
    """
    Get a comprehensive portfolio summary with adaptive insights and recommendations.
    
    Returns:
        Dict containing portfolio metrics, entity breakdown, and suggested operations
    """
    return await get_portfolio_summary()

# Market Data Tools
@mcp.tool()
async def get_stock_quote_tool(symbol: str) -> dict:
    """
    Retrieves and formats the latest quote for a stock including bid/ask spread analysis.
    
    Args:
        symbol: The stock symbol to get quote for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing bid/ask prices, sizes, spread metrics, and entity insights
    """
    return await get_stock_quote(symbol)

@mcp.tool()
async def get_stock_trade_tool(symbol: str) -> dict:
    """
    Retrieves the latest trade information for a stock.
    
    Args:
        symbol: The stock symbol to get trade for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing latest trade price, size, timestamp, and exchange information
    """
    return await get_stock_trade(symbol)

@mcp.tool()
async def get_stock_snapshot_tool(symbol: str) -> dict:
    """
    Retrieves comprehensive snapshot data for a stock including quote, trade, and daily bar data.
    
    Args:
        symbol: The stock symbol to get snapshot for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing complete market data with volatility analysis and role suggestions
    """
    return await get_stock_snapshot(symbol)

@mcp.tool()
async def get_historical_bars_tool(
    symbol: str, 
    timeframe: str = "1Day", 
    start_date: str = None,
    end_date: str = None,
    limit: int = 100
) -> dict:
    """
    Retrieves historical bar data for a stock with summary statistics.
    
    Args:
        symbol: The stock symbol to get bars for (e.g., 'AAPL', 'MSFT')
        timeframe: The timeframe for bars ('1Min', '5Min', '15Min', '1Hour', '1Day')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Maximum number of bars to return (default 100, max 10000)
    
    Returns:
        Dict containing historical bars with price/volume statistics and trend analysis
    """
    return await get_historical_bars(symbol, timeframe, start_date, end_date, limit)

# Order Management Tools
@mcp.tool()
async def place_market_order_tool(
    symbol: str,
    side: str,
    quantity: float,
    time_in_force: str = "day"
) -> dict:
    """
    Places a market order for immediate execution at current market price.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        time_in_force: 'day', 'gtc', 'ioc', 'fok' (default: 'day')
    
    Returns:
        Dict containing order confirmation with status, fill details, and tracking info
    """
    return await place_market_order(symbol, side, quantity, time_in_force)

@mcp.tool()
async def place_limit_order_tool(
    symbol: str,
    side: str,
    quantity: float,
    limit_price: float,
    time_in_force: str = "day"
) -> dict:
    """
    Places a limit order to buy/sell at a specific price or better.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        limit_price: The maximum price to pay (buy) or minimum price to accept (sell)
        time_in_force: 'day', 'gtc', 'ioc', 'fok' (default: 'day')
    
    Returns:
        Dict containing order confirmation with limit price, status, and tracking info
    """
    return await place_limit_order(symbol, side, quantity, limit_price, time_in_force)

@mcp.tool()
async def place_stop_loss_order_tool(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    time_in_force: str = "day"
) -> dict:
    """
    Places a stop loss order for risk management and position protection.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        stop_price: The stop price that triggers the order
        time_in_force: 'day', 'gtc' (default: 'day')
    
    Returns:
        Dict containing stop order confirmation with trigger price and risk management details
    """
    return await place_stop_loss_order(symbol, side, quantity, stop_price, time_in_force)

@mcp.tool()
async def get_orders_tool(
    status: str = None,
    limit: int = 50,
    symbols: list = None
) -> dict:
    """
    Retrieves orders with filtering options and summary statistics.
    
    Args:
        status: Filter by order status ('open', 'closed', 'all') (optional)
        limit: Maximum number of orders to return (default 50, max 500)
        symbols: List of symbols to filter by (optional)
    
    Returns:
        Dict containing orders with status breakdown, side analysis, and type distribution
    """
    return await get_orders(status, limit, symbols)

@mcp.tool()
async def cancel_order_tool(order_id: str) -> dict:
    """
    Cancels an existing pending order.
    
    Args:
        order_id: The ID of the order to cancel
    
    Returns:
        Dict containing cancellation confirmation and status update
    """
    return await cancel_order(order_id)

# Resource Mirror Tools (for universal compatibility)
@mcp.tool()
async def resource_account_info_tool() -> dict:
    """Tool mirror of trading://account/info resource for universal client compatibility."""
    return await resource_account_info()

@mcp.tool()
async def resource_account_positions_tool() -> dict:
    """Tool mirror of trading://account/positions resource for universal client compatibility."""
    return await resource_account_positions()

@mcp.tool()
async def resource_account_orders_tool() -> dict:
    """Tool mirror of trading://account/orders resource for universal client compatibility."""
    return await resource_account_orders()

@mcp.tool()
async def resource_portfolio_summary_tool() -> dict:
    """Tool mirror of trading://portfolio/summary resource for universal client compatibility."""
    return await resource_portfolio_summary()

@mcp.tool()
async def resource_portfolio_entities_tool() -> dict:
    """Tool mirror of trading://portfolio/entities resource for universal client compatibility."""
    return await resource_portfolio_entities()

@mcp.tool()
async def resource_symbols_active_tool() -> dict:
    """Tool mirror of trading://symbols/active resource for universal client compatibility."""
    return await resource_symbols_active()

@mcp.tool()
async def resource_symbols_count_tool() -> dict:
    """Tool mirror of trading://symbols/count resource for universal client compatibility."""
    return await resource_symbols_count()

@mcp.tool()
async def resource_system_health_tool() -> dict:
    """Tool mirror of trading://system/health resource for universal client compatibility."""
    return await resource_system_health()

@mcp.tool()
async def resource_system_memory_tool() -> dict:
    """Tool mirror of trading://system/memory resource for universal client compatibility."""
    return await resource_system_memory()

@mcp.tool()
async def resource_system_status_tool() -> dict:
    """Tool mirror of trading://system/status resource for universal client compatibility."""
    return await resource_system_status()

# Register resources
logger.info("Registering MCP resources...")

@mcp.resource("trading://{path:.*}")
async def trading_resource_handler(path: str) -> dict:
    """
    Universal trading resource handler supporting the trading:// URI scheme.
    
    Supported URIs:
    - trading://account/info - Account information
    - trading://account/positions - All positions  
    - trading://account/orders - Recent orders
    - trading://portfolio/summary - Portfolio analysis
    - trading://portfolio/entities - Portfolio entities
    - trading://symbols/active - Currently tracked symbols
    - trading://symbols/count - Symbol statistics
    - trading://system/health - System health check
    - trading://system/memory - Memory usage statistics
    - trading://system/status - Complete system status
    
    Args:
        path: The resource path (everything after trading://)
    
    Returns:
        Dict with resource_data or error
    """
    uri = f"trading://{path}"
    return await get_trading_resource(uri)

# Register prompts
logger.info("Registering MCP prompts...")

@mcp.prompt()
async def portfolio_first_look_prompt() -> dict:
    """
    Adaptive portfolio exploration prompt that provides personalized guidance based on your current holdings and market data.
    Perfect for getting started with portfolio analysis and discovering actionable insights.
    """
    return await portfolio_first_look()

@mcp.prompt()
async def trading_strategy_workshop_prompt(strategy_focus: str = "general") -> dict:
    """
    Strategic trading guidance tailored to your focus area and current portfolio composition.
    
    Args:
        strategy_focus: Type of strategy ('growth', 'income', 'risk_management', 'general')
    """
    return await trading_strategy_workshop(strategy_focus)

@mcp.prompt()
async def market_analysis_session_prompt() -> dict:
    """
    Comprehensive market analysis framework with tools and techniques for researching stocks and identifying opportunities.
    Adapts guidance based on your currently tracked symbols.
    """
    return await market_analysis_session()

@mcp.prompt()
async def list_mcp_capabilities_prompt() -> dict:
    """
    Complete overview of all available MCP tools, resources, and capabilities with usage examples and getting started guidance.
    """
    return await list_mcp_capabilities()

# Utility tools for state management
@mcp.tool()
async def clear_portfolio_state_tool() -> dict:
    """
    Clears all portfolio state and tracked symbols. Useful for starting fresh or testing.
    
    Returns:
        Dict containing confirmation of state clearance and memory usage before/after
    """
    try:
        from .models.schemas import StateManager
        
        # Get memory usage before clearing
        memory_before = StateManager.get_memory_usage()
        
        # Clear all state
        StateManager.clear_all()
        
        # Get memory usage after clearing
        memory_after = StateManager.get_memory_usage()
        
        return {
            "status": "success",
            "data": {
                "message": "Portfolio state cleared successfully",
                "memory_before": memory_before,
                "memory_after": memory_after
            },
            "metadata": {
                "operation": "clear_portfolio_state"
            }
        }
        
    except Exception as e:
        logger.error(f"Error clearing portfolio state: {e}")
        return {
            "status": "error",
            "message": f"Failed to clear portfolio state: {str(e)}",
            "error_type": type(e).__name__
        }

logger.info(f"MCP server '{settings.server_name}' initialized with all tools, resources, and prompts")
logger.info("Gold standard patterns implemented:")
logger.info("✓ Modular tool organization")
logger.info("✓ Resource mirror pattern for universal compatibility")
logger.info("✓ Adaptive prompts with context awareness")
logger.info("✓ Consistent error handling")
logger.info("✓ Comprehensive state management")
logger.info("✓ Entity classification and insights")