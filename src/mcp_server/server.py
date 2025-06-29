"""
Main MCP server implementation following gold standard patterns.
Central registration point for all tools, resources, and prompts.
"""

import logging
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP
from .config.simple_settings import settings

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

from .tools.custom_strategy_execution import (
    execute_custom_trading_strategy,
    execute_portfolio_optimization_strategy,
    execute_risk_analysis_strategy
)

from .tools.advanced_analysis_tools import (
    generate_portfolio_health_assessment,
    generate_advanced_market_correlation_analysis
)

from .tools.execute_custom_analytics_code_tool import (
    execute_custom_analytics_code,
    create_sample_dataset_from_portfolio
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

# Initialize FastMCP server
mcp = FastMCP(
    name=settings.server_name,
    version="1.0.0"
)

logger = logging.getLogger(__name__)

# Register all tools following gold standard patterns
# Note: Logging will be configured in main.py before this runs

# Account Management Tools
@mcp.tool()
async def get_account_info_tool() -> Dict[str, Any]:
    """
    Retrieves and formats the current account information including balances and status.
    
    Returns:
        Dict containing account details including buying power, cash, portfolio value, equity, and trading status
    """
    return await get_account_info()

@mcp.tool()
async def get_positions_tool() -> Dict[str, Any]:
    """
    Retrieves and formats all current positions in the portfolio.
    
    Returns:
        Dict containing details of all open positions with P&L analysis and adaptive insights
    """
    return await get_positions()

@mcp.tool()
async def get_open_position_tool(symbol: str) -> Dict[str, Any]:
    """
    Retrieves and formats details for a specific open position.
    
    Args:
        symbol: The symbol name of the asset to get position for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing position details with market value, P&L, and role analysis
    """
    return await get_open_position(symbol)

@mcp.tool()
async def get_portfolio_summary_tool() -> Dict[str, Any]:
    """
    Get a comprehensive portfolio summary with adaptive insights and recommendations.
    
    Returns:
        Dict containing portfolio metrics, entity breakdown, and suggested operations
    """
    return await get_portfolio_summary()

# Market Data Tools
@mcp.tool()
async def get_stock_quote_tool(symbol: str) -> Dict[str, Any]:
    """
    Retrieves and formats the latest quote for a stock including bid/ask spread analysis.
    
    Args:
        symbol: The stock symbol to get quote for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing bid/ask prices, sizes, spread metrics, and entity insights
    """
    return await get_stock_quote(symbol)

@mcp.tool()
async def get_stock_trade_tool(symbol: str) -> Dict[str, Any]:
    """
    Retrieves the latest trade information for a stock.
    
    Args:
        symbol: The stock symbol to get trade for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict containing latest trade price, size, timestamp, and exchange information
    """
    return await get_stock_trade(symbol)

@mcp.tool()
async def get_stock_snapshot_tool(symbols: str) -> Dict[str, Any]:
    """
    Retrieves comprehensive snapshot data for one or more stocks including quote, trade, and daily bar data.
    
    Args:
        symbols: Single stock symbol or comma-separated symbols (e.g., 'AAPL' or 'AAPL,MSFT,GOOGL')
    
    Returns:
        Dict containing complete market data with volatility analysis and role suggestions
    """
    return await get_stock_snapshot(symbols)

@mcp.tool()
async def get_historical_bars_tool(
    symbol: str, 
    timeframe: str = "1Day", 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Retrieves historical bar data for a stock with complete trading metrics.
    
    Args:
        symbol: The stock symbol to get bars for (e.g., 'AAPL', 'MSFT')
        timeframe: The timeframe for bars ('1Min', '5Min', '15Min', '1Hour', '1Day')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Maximum number of bars to return (default 100, max 10000)
    
    Returns:
        Dict containing historical bars with OHLCV data, trade_count, vwap, and comprehensive statistics
    """
    return await get_historical_bars(symbol, timeframe, start_date, end_date, limit)

# Order Management Tools
@mcp.tool()
async def place_market_order_tool(
    symbol: str,
    side: str,
    quantity: float,
    time_in_force: str = "day"
) -> Dict[str, Any]:
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
) -> Dict[str, Any]:
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
) -> Dict[str, Any]:
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
    status: Optional[str] = None,
    limit: int = 50,
    symbols: Optional[List[str]] = None
) -> Dict[str, Any]:
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
async def cancel_order_tool(order_id: str) -> Dict[str, Any]:
    """
    Cancels an existing pending order.
    
    Args:
        order_id: The ID of the order to cancel
    
    Returns:
        Dict containing cancellation confirmation and status update
    """
    return await cancel_order(order_id)

# Custom Strategy Execution Tools
@mcp.tool()
async def execute_custom_trading_strategy_tool(
    strategy_code: str,
    symbols: Optional[str] = None,
    portfolio_context: bool = True
) -> str:
    """
    Execute custom trading strategy code in isolated subprocess with trading libraries available.
    
    IMPORTANT FOR AI AGENTS:
    - Portfolio data will be available as 'portfolio' dict in your code
    - Market data will be available as 'market_data' dict for requested symbols
    - Libraries pre-imported: pandas as pd, numpy as np, datetime
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    USAGE EXAMPLES:
    
    Portfolio analysis:
    ```python
    print("Portfolio Overview:")
    print(f"Account Value: ${portfolio['account']['portfolio_value']:,.2f}")
    print(f"Buying Power: ${portfolio['account']['buying_power']:,.2f}")
    
    if portfolio['positions']:
        print("\\nTop Holdings:")
        for pos in portfolio['positions'][:5]:
            print(f"  {pos['symbol']}: {pos['qty']} shares, P&L: ${pos['unrealized_pl']:+.2f}")
    ```
    
    Market analysis:
    ```python
    for symbol, data in market_data.items():
        current_price = data['latest_trade']['price']
        daily_change = data['daily_bar']['daily_change_percent']
        print(f"{symbol}: ${current_price:.2f} ({daily_change:+.2f}%)")
    ```
    
    Custom strategy:
    ```python
    # RSI calculation example
    def calculate_rsi(prices, period=14):
        delta = pd.Series(prices).diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    # Analyze symbols
    for symbol, data in market_data.items():
        if 'historical_bars' in data:
            prices = [bar['close'] for bar in data['historical_bars']]
            if len(prices) >= 14:
                rsi = calculate_rsi(prices)
                current_rsi = rsi.iloc[-1]
                print(f"{symbol} RSI: {current_rsi:.2f}")
    ```
    
    Args:
        strategy_code: Python code to execute (must print() results to see output)
        symbols: Comma-separated symbols to include market data for (optional)
        portfolio_context: Include current portfolio data in execution context
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    return await execute_custom_trading_strategy(strategy_code, symbols, portfolio_context)

@mcp.tool()
async def execute_portfolio_optimization_strategy_tool(
    optimization_code: str,
    risk_tolerance: float = 0.5
) -> str:
    """
    Execute portfolio optimization strategy with risk parameters.
    
    Args:
        optimization_code: Python code for portfolio optimization
        risk_tolerance: Risk tolerance level (0.0 to 1.0)
    
    Returns:
        str: Optimization results and recommendations
    """
    return await execute_portfolio_optimization_strategy(optimization_code, risk_tolerance)

@mcp.tool()
async def execute_risk_analysis_strategy_tool(
    risk_analysis_code: str,
    market_symbols: str = "SPY,QQQ,IWM"
) -> str:
    """
    Execute risk analysis strategy with market benchmark data.
    
    Args:
        risk_analysis_code: Python code for risk analysis
        market_symbols: Market benchmark symbols for comparison
    
    Returns:
        str: Risk analysis results
    """
    return await execute_risk_analysis_strategy(risk_analysis_code, market_symbols)

# Advanced Analysis Tools
@mcp.tool()
async def generate_portfolio_health_assessment_tool() -> Dict[str, Any]:
    """
    Comprehensive portfolio health assessment with scoring and actionable recommendations.
    
    Analyzes your current portfolio across multiple dimensions:
    - Diversification scoring based on entity role distribution
    - Risk concentration analysis for volatile/speculative positions
    - Performance balance assessment (growth vs income focus)
    - Generates specific action items with tool recommendations
    
    Returns:
        Dict containing overall health score (0-100), detailed analysis by category,
        prioritized recommendations, and actionable next steps with specific MCP tools to use
    """
    return await generate_portfolio_health_assessment()

@mcp.tool()
async def generate_advanced_market_correlation_analysis_tool(
    symbols: Optional[str] = None
) -> Dict[str, Any]:
    """
    Advanced correlation analysis between portfolio holdings with diversification insights.
    
    Performs sophisticated correlation analysis:
    - Calculates correlation matrix using 30-day price returns
    - Identifies highly correlated pairs (potential concentration risk)
    - Provides diversification scoring based on correlation patterns
    - Generates risk insights and recommendations for portfolio balance
    
    Args:
        symbols: Optional comma-separated symbols to analyze (uses tracked symbols if not provided)
    
    Returns:
        Dict containing correlation matrix, high correlation pairs, diversification score,
        risk insights, and specific recommendations for improving portfolio balance
    """
    return await generate_advanced_market_correlation_analysis(symbols)

# Universal Dataset Analytics Tools
@mcp.tool()
async def execute_custom_analytics_code_tool(
    dataset_name: str,
    python_code: str,
    include_portfolio_context: bool = False
) -> str:
    """
    Execute custom Python analytics code against any dataset with full data science stack.
    
    UNIVERSAL DATASET AGNOSTICISM:
    This tool demonstrates the gold standard pattern for dataset-agnostic analytics.
    Works with ANY structured data - trading data, customer data, sales records, surveys, etc.
    
    IMPORTANT FOR AI AGENTS:
    - Dataset available as 'df' pandas DataFrame in your code
    - Portfolio context available as 'portfolio' dict if include_portfolio_context=True
    - Libraries pre-imported: pandas as pd, numpy as np, plotly.express as px
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    USAGE EXAMPLES:
    
    Basic data exploration:
    ```python
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(df.head())
    print(df.describe())
    ```
    
    Advanced analytics:
    ```python
    # Correlation analysis (works on any numerical columns)
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) >= 2:
        corr_matrix = df[numerical_cols].corr()
        print("Strongest correlations:")
        for i in range(len(numerical_cols)):
            for j in range(i+1, len(numerical_cols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.5:
                    print(f"{numerical_cols[i]} <-> {numerical_cols[j]}: {corr:.3f}")
    ```
    
    Visualization:
    ```python
    # Works with any categorical/numerical column combinations
    if len(df.columns) >= 2:
        cat_cols = df.select_dtypes(include=['object']).columns
        num_cols = df.select_dtypes(include=[np.number]).columns
        if len(cat_cols) > 0 and len(num_cols) > 0:
            fig = px.bar(df, x=cat_cols[0], y=num_cols[0], 
                         title=f'{num_cols[0]} by {cat_cols[0]}')
            print(f"Chart created: {num_cols[0]} by {cat_cols[0]}")
    ```
    
    Args:
        dataset_name: Name of dataset to analyze (use 'sample_market_data' for demo)
        python_code: Python code to execute (must print() results to see output)
        include_portfolio_context: Include current portfolio data for cross-dataset analysis
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    return await execute_custom_analytics_code(dataset_name, python_code, include_portfolio_context)

@mcp.tool()
async def create_sample_dataset_from_portfolio_tool() -> Dict[str, Any]:
    """
    Create a sample analytics dataset from current portfolio positions.
    
    Demonstrates universal dataset agnosticism pattern:
    - Takes trading data and converts to generic dataset structure
    - Enables cross-dataset analytics and correlation analysis
    - Works with any structured data source (positions, orders, market data, etc.)
    
    Returns:
        Dict containing sample dataset with rows, columns, and preview data ready for analytics
    """
    return await create_sample_dataset_from_portfolio()

# Resource Mirror Tools (for universal compatibility)
@mcp.tool()
async def resource_account_info_tool() -> Dict[str, Any]:
    """Tool mirror of trading://account/info resource for universal client compatibility."""
    return await resource_account_info()

@mcp.tool()
async def resource_account_positions_tool() -> Dict[str, Any]:
    """Tool mirror of trading://account/positions resource for universal client compatibility."""
    return await resource_account_positions()

@mcp.tool()
async def resource_account_orders_tool() -> Dict[str, Any]:
    """Tool mirror of trading://account/orders resource for universal client compatibility."""
    return await resource_account_orders()

@mcp.tool()
async def resource_portfolio_summary_tool() -> Dict[str, Any]:
    """Tool mirror of trading://portfolio/summary resource for universal client compatibility."""
    return await resource_portfolio_summary()

@mcp.tool()
async def resource_portfolio_entities_tool() -> Dict[str, Any]:
    """Tool mirror of trading://portfolio/entities resource for universal client compatibility."""
    return await resource_portfolio_entities()

@mcp.tool()
async def resource_symbols_active_tool() -> Dict[str, Any]:
    """Tool mirror of trading://symbols/active resource for universal client compatibility."""
    return await resource_symbols_active()

@mcp.tool()
async def resource_symbols_count_tool() -> Dict[str, Any]:
    """Tool mirror of trading://symbols/count resource for universal client compatibility."""
    return await resource_symbols_count()

@mcp.tool()
async def resource_system_health_tool() -> Dict[str, Any]:
    """Tool mirror of trading://system/health resource for universal client compatibility."""
    return await resource_system_health()

@mcp.tool()
async def resource_system_memory_tool() -> Dict[str, Any]:
    """Tool mirror of trading://system/memory resource for universal client compatibility."""
    return await resource_system_memory()

@mcp.tool()
async def resource_system_status_tool() -> Dict[str, Any]:
    """Tool mirror of trading://system/status resource for universal client compatibility."""
    return await resource_system_status()

# Register resources
# logger.info("Registering MCP resources...")

@mcp.resource("trading://{path}")
async def trading_resource_handler(path: str) -> Dict[str, Any]:
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
        path: The resource path (e.g., account/info)
    
    Returns:
        Dict with resource_data or error
    """
    uri = f"trading://{path}"
    return await get_trading_resource(uri)

# Register prompts
# logger.info("Registering MCP prompts...")

@mcp.prompt()
async def portfolio_first_look_prompt() -> Dict[str, Any]:
    """
    Adaptive portfolio exploration prompt that provides personalized guidance based on your current holdings and market data.
    Perfect for getting started with portfolio analysis and discovering actionable insights.
    """
    return await portfolio_first_look()

@mcp.prompt()
async def trading_strategy_workshop_prompt(strategy_focus: str = "general") -> Dict[str, Any]:
    """
    Strategic trading guidance tailored to your focus area and current portfolio composition.
    
    Args:
        strategy_focus: Type of strategy ('growth', 'income', 'risk_management', 'general')
    """
    return await trading_strategy_workshop(strategy_focus)

@mcp.prompt()
async def market_analysis_session_prompt() -> Dict[str, Any]:
    """
    Comprehensive market analysis framework with tools and techniques for researching stocks and identifying opportunities.
    Adapts guidance based on your currently tracked symbols.
    """
    return await market_analysis_session()

@mcp.prompt()
async def list_mcp_capabilities_prompt() -> Dict[str, Any]:
    """
    Complete overview of all available MCP tools, resources, and capabilities with usage examples and getting started guidance.
    """
    return await list_mcp_capabilities()

# Utility tools for state management
@mcp.tool()
async def clear_portfolio_state_tool() -> Dict[str, Any]:
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

# MCP server initialized - logging statements removed to prevent stdout interference