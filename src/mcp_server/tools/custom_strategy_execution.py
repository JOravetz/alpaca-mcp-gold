"""
Custom Trading Strategy Execution Tool
Implements safe subprocess isolation for custom trading analysis code.
"""
# ruff: noqa: F821

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from ..models.schemas import StateManager

logger = logging.getLogger(__name__)

async def execute_custom_trading_strategy(
    strategy_code: str,
    symbols: Optional[str] = None,
    portfolio_context: bool = True
) -> str:
    """
    Execute custom trading strategy code in isolated subprocess with trading libraries available.
    
    IMPORTANT FOR AI AGENTS:
    - Portfolio data will be available as 'portfolio' dict in your code
    - Market data will be available as 'market_data' dict for requested symbols
    - Libraries pre-imported: pandas as pd, numpy as np, alpaca_trade_api, datetime
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
    import pandas as pd
    import numpy as np
    
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
                
                if current_rsi < 30:
                    print(f"  -> {symbol} is oversold (RSI < 30)")
                elif current_rsi > 70:
                    print(f"  -> {symbol} is overbought (RSI > 70)")
    ```
    
    Args:
        strategy_code: Python code to execute (must print() results to see output)
        symbols: Comma-separated symbols to include market data for (optional)
        portfolio_context: Include current portfolio data in execution context
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    try:
        # Step 1: Gather execution context
        execution_context = await _gather_trading_context(symbols, portfolio_context)
        
        # Step 2: Create execution template
        execution_code = _create_execution_template(strategy_code, execution_context)
        
        # Step 3: Execute in subprocess
        result = await _execute_in_subprocess(execution_code)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in custom strategy execution: {e}")
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"

async def _gather_trading_context(symbols: Optional[str], include_portfolio: bool) -> Dict[str, Any]:
    """Gather trading context data for strategy execution."""
    context = {}
    
    try:
        # Portfolio context
        if include_portfolio:
            portfolio_data = {}
            
            # Get account info
            try:
                from .account_tools import get_account_info, get_positions
                account_result = await get_account_info()
                if account_result["status"] == "success":
                    portfolio_data["account"] = account_result["data"]
                
                # Get positions
                positions_result = await get_positions()
                if positions_result["status"] == "success":
                    portfolio_data["positions"] = positions_result["data"]
                else:
                    portfolio_data["positions"] = []
                    
            except Exception as e:
                logger.warning(f"Could not gather portfolio context: {e}")
                portfolio_data = {"account": {}, "positions": []}
            
            # Get tracked symbols from state
            tracked_symbols = StateManager.get_all_symbols()
            portfolio_data["tracked_symbols"] = {
                symbol: {
                    "suggested_role": entity.suggested_role.value,
                    "characteristics": entity.characteristics
                }
                for symbol, entity in tracked_symbols.items()
            }
            
            context["portfolio"] = portfolio_data
        
        # Market data context
        if symbols:
            market_data = {}
            symbol_list = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            
            try:
                from .market_data_tools import get_stock_snapshot, get_historical_bars
                
                for symbol in symbol_list:
                    symbol_data = {}
                    
                    # Get snapshot
                    snapshot_result = await get_stock_snapshot(symbol)
                    if snapshot_result["status"] == "success":
                        symbol_data.update(snapshot_result["data"])
                    
                    # Get some historical data for technical analysis
                    try:
                        hist_result = await get_historical_bars(symbol, "1Day", limit=30)
                        if hist_result["status"] == "success":
                            symbol_data["historical_bars"] = hist_result["data"]["bars"]
                    except Exception:
                        pass  # Historical data is optional
                    
                    market_data[symbol] = symbol_data
                
            except Exception as e:
                logger.warning(f"Could not gather market data: {e}")
                market_data = {}
            
            context["market_data"] = market_data
        else:
            context["market_data"] = {}
            
    except Exception as e:
        logger.error(f"Error gathering trading context: {e}")
        context = {"portfolio": {}, "market_data": {}}
    
    return context

def _create_execution_template(user_code: str, context: Dict[str, Any]) -> str:
    """Create safe execution template with trading context."""
    
    # Serialize context data
    portfolio_json = json.dumps(context.get("portfolio", {}), default=str)
    market_data_json = json.dumps(context.get("market_data", {}), default=str)
    
    # Indent user code for proper execution
    indented_user_code = '\n'.join('    ' + line for line in user_code.split('\n'))
    
    execution_template = f'''
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

try:
    # Load trading context
    portfolio_data = {portfolio_json}
    market_data_raw = {market_data_json}
    
    # Make data easily accessible
    portfolio = portfolio_data
    market_data = market_data_raw
    
    # Helper functions for common calculations
    def calculate_portfolio_value(positions):
        """Calculate total portfolio value from positions."""
        return sum(float(pos.get('market_value', 0)) for pos in positions)
    
    def calculate_daily_pnl(positions):
        """Calculate total daily P&L from positions."""
        return sum(float(pos.get('unrealized_intraday_pl', 0)) for pos in positions)
    
    def get_position_by_symbol(symbol, positions):
        """Get position data for specific symbol."""
        for pos in positions:
            if pos.get('symbol') == symbol.upper():
                return pos
        return None
    
    def calculate_rsi(prices, period=14):
        """Calculate RSI for price series."""
        if len(prices) < period:
            return None
        prices_series = pd.Series(prices)
        delta = prices_series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1] if not rsi.empty else None
    
    def calculate_sma(prices, period):
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period
    
    def calculate_volatility(prices, period=20):
        """Calculate price volatility (standard deviation)."""
        if len(prices) < period:
            return None
        returns = pd.Series(prices).pct_change().dropna()
        return returns.std() * (252 ** 0.5)  # Annualized volatility
    
    # Print context info
    print("=== Trading Strategy Execution Context ===")
    if 'portfolio' in globals() and portfolio and 'account' in portfolio:  # noqa: F821
        account = portfolio['account']  # noqa: F821
        print(f"Account Value: ${account.get('portfolio_value', 0):,.2f}")  # noqa: F821
        print(f"Buying Power: ${account.get('buying_power', 0):,.2f}")  # noqa: F821
        print(f"Positions: {len(portfolio.get('positions', []))}")  # noqa: F821
    
    if 'market_data' in globals() and market_data:  # noqa: F821
        print(f"Market Data: {len(market_data)} symbols loaded")  # noqa: F821
        for sym in market_data.keys():  # noqa: F821
            print(f"  - {sym}")  # noqa: F821
    
    print("=" * 45)
    print()
    
    # Execute user strategy code
{indented_user_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
'''
    
    return execution_template

async def _execute_in_subprocess(execution_code: str) -> str:
    """Execute code in isolated subprocess with timeout."""
    try:
        # Execute subprocess with trading libraries available
        process = await asyncio.create_subprocess_exec(
            'uv', 'run', '--with', 'pandas', '--with', 'numpy', 
            'python', '-c', execution_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd='/home/jjoravet/mcp_server_best_practices/alpaca-mcp-gold-standard'
        )
        
        # Wait for completion with timeout
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
            return stdout.decode('utf-8', errors='replace')
        except asyncio.TimeoutError:
            # Kill the process if it times out
            process.kill()
            await process.wait()
            return "TIMEOUT: Strategy execution exceeded 30 second limit"
            
    except Exception as e:
        logger.error(f"Subprocess execution error: {e}")
        return f"SUBPROCESS ERROR: {type(e).__name__}: {str(e)}"

# Additional helper functions for advanced strategies
async def execute_portfolio_optimization_strategy(
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
    # Add risk tolerance to context
    context = await _gather_trading_context(None, True)
    context["risk_tolerance"] = risk_tolerance
    context["optimization_mode"] = True
    
    # Enhanced template for optimization
    enhanced_code = f"""
# Portfolio optimization context
risk_tolerance = {risk_tolerance}
optimization_mode = True

print("=== Portfolio Optimization Strategy ===")
print(f"Risk Tolerance: {risk_tolerance}")

{optimization_code}
"""
    
    return await execute_custom_trading_strategy(enhanced_code, None, True)

async def execute_risk_analysis_strategy(
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
    # Enhanced template for risk analysis
    enhanced_code = f"""
# Risk analysis context
market_benchmarks = "{market_symbols}".split(',')

print("=== Risk Analysis Strategy ===")
print(f"Benchmarks: {{market_benchmarks}}")

{risk_analysis_code}
"""
    
    return await execute_custom_trading_strategy(enhanced_code, market_symbols, True)