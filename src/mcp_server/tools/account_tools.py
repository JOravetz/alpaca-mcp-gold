"""
Account management tools following gold standard patterns.
Handles account information, positions, and portfolio management.
"""

import logging
from typing import Dict, Any
from ..models.alpaca_clients import AlpacaClientManager
from ..models.schemas import StateManager, TradingPortfolioSchema, EntityInfo

logger = logging.getLogger(__name__)


async def get_account_info() -> Dict[str, Any]:
    """
    Retrieves and formats the current account information including balances and status.

    Returns:
        Dict with status and account data or error message
    """
    try:
        trading_client = AlpacaClientManager.get_trading_client()
        account = trading_client.get_account()

        # Store portfolio schema for adaptive insights
        portfolio_data = {
            "buying_power": str(account.buying_power),
            "portfolio_value": str(account.portfolio_value),
            "equity": str(account.equity),
        }
        portfolio_schema = TradingPortfolioSchema.from_account_data(portfolio_data)
        StateManager.set_portfolio(portfolio_schema)

        account_data = {
            "account_id": str(account.id),
            "status": str(account.status),
            "currency": str(account.currency),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "equity": float(account.equity),
            "long_market_value": float(account.long_market_value),
            "short_market_value": float(account.short_market_value),
            "pattern_day_trader": account.pattern_day_trader,
            "daytrade_count": getattr(account, "daytrade_count", 0),
        }

        return {
            "status": "success",
            "data": account_data,
            "metadata": {
                "operation": "get_account_info",
                "suggested_operations": portfolio_schema.suggested_operations,
            },
        }

    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve account information: {str(e)}",
            "error_type": type(e).__name__,
        }


async def get_positions() -> Dict[str, Any]:
    """
    Retrieves and formats all current positions in the portfolio.

    Returns:
        Dict with status and positions data or error message
    """
    try:
        trading_client = AlpacaClientManager.get_trading_client()
        positions = trading_client.get_all_positions()

        if not positions:
            return {
                "status": "success",
                "data": [],
                "metadata": {"message": "No open positions found"},
            }

        positions_data = []
        portfolio = (
            StateManager.get_portfolio() or TradingPortfolioSchema.from_account_data({})
        )

        for position in positions:
            # Create entity info for adaptive insights
            position_data = {
                "qty": str(position.qty),
                "unrealized_pl": str(position.unrealized_pl),
                "market_value": str(position.market_value),
            }
            entity_info = EntityInfo.from_position_data(position.symbol, position_data)
            portfolio.add_entity(entity_info)
            StateManager.add_symbol(position.symbol, entity_info)

            position_info = {
                "symbol": position.symbol,
                "quantity": float(position.qty),
                "market_value": float(position.market_value),
                "avg_entry_price": float(position.avg_entry_price),
                "current_price": float(position.current_price),
                "unrealized_pl": float(position.unrealized_pl),
                "unrealized_plpc": float(position.unrealized_plpc),
                "suggested_role": entity_info.suggested_role.value,
                "characteristics": entity_info.characteristics,
            }
            positions_data.append(position_info)

        # Update portfolio state
        StateManager.set_portfolio(portfolio)

        return {
            "status": "success",
            "data": positions_data,
            "metadata": {
                "operation": "get_positions",
                "total_positions": len(positions_data),
                "portfolio_insights": portfolio.suggested_operations,
            },
        }

    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve positions: {str(e)}",
            "error_type": type(e).__name__,
        }


async def get_open_position(symbol: str) -> Dict[str, Any]:
    """
    Retrieves and formats details for a specific open position.

    Args:
        symbol: The symbol name of the asset to get position for (e.g., 'AAPL', 'MSFT')

    Returns:
        Dict with status and position data or error message
    """
    try:
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty",
                "error_type": "ValueError",
            }

        trading_client = AlpacaClientManager.get_trading_client()
        position = trading_client.get_open_position(symbol.upper())

        # Create entity info for insights
        position_data = {
            "qty": str(position.qty),
            "unrealized_pl": str(position.unrealized_pl),
            "market_value": str(position.market_value),
        }
        entity_info = EntityInfo.from_position_data(position.symbol, position_data)
        StateManager.add_symbol(position.symbol, entity_info)

        # Check if it's an options position
        is_option = len(symbol) > 6 and any(c in symbol for c in ["C", "P"])
        quantity_text = (
            f"{position.qty} contracts" if is_option else f"{position.qty} shares"
        )

        position_info = {
            "symbol": position.symbol,
            "quantity": float(position.qty),
            "quantity_display": quantity_text,
            "market_value": float(position.market_value),
            "avg_entry_price": float(position.avg_entry_price),
            "current_price": float(position.current_price),
            "unrealized_pl": float(position.unrealized_pl),
            "unrealized_plpc": float(position.unrealized_plpc),
            "asset_type": "option" if is_option else "stock",
            "suggested_role": entity_info.suggested_role.value,
            "characteristics": entity_info.characteristics,
        }

        return {
            "status": "success",
            "data": position_info,
            "metadata": {
                "operation": "get_open_position",
                "insights": entity_info.characteristics,
            },
        }

    except Exception as e:
        logger.error(f"Error getting position for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve position for {symbol}: {str(e)}",
            "error_type": type(e).__name__,
        }


async def get_portfolio_summary() -> Dict[str, Any]:
    """
    Get a comprehensive portfolio summary with adaptive insights.

    Returns:
        Dict with portfolio analysis and recommendations
    """
    try:
        # Get current portfolio state
        portfolio = StateManager.get_portfolio()
        if not portfolio:
            # Initialize with account data
            account_result = await get_account_info()
            if account_result["status"] == "error":
                return account_result
            portfolio = StateManager.get_portfolio()

        # Get memory usage
        memory_usage = StateManager.get_memory_usage()

        summary = {
            "portfolio_metrics": portfolio.portfolio_metrics,
            "entity_count": len(portfolio.entities),
            "suggested_operations": portfolio.suggested_operations,
            "entity_breakdown": {},
            "memory_usage": memory_usage,
        }

        # Analyze entities by type and role
        for entity in portfolio.entities.values():
            entity_type = entity.entity_type.value
            if entity_type not in summary["entity_breakdown"]:
                summary["entity_breakdown"][entity_type] = {"count": 0, "roles": {}}

            summary["entity_breakdown"][entity_type]["count"] += 1
            role = entity.suggested_role.value
            if role not in summary["entity_breakdown"][entity_type]["roles"]:
                summary["entity_breakdown"][entity_type]["roles"][role] = 0
            summary["entity_breakdown"][entity_type]["roles"][role] += 1

        return {
            "status": "success",
            "data": summary,
            "metadata": {
                "operation": "get_portfolio_summary",
                "last_updated": portfolio.last_updated.isoformat(),
            },
        }

    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        return {
            "status": "error",
            "message": f"Failed to generate portfolio summary: {str(e)}",
            "error_type": type(e).__name__,
        }
