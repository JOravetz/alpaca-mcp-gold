"""
Trading resources following gold standard patterns.
Provides read-only data access via custom URI schemes.
"""

import logging
import urllib.parse
from typing import Dict, Any
from ..models.alpaca_clients import AlpacaClientManager
from ..models.schemas import StateManager

logger = logging.getLogger(__name__)

async def get_trading_resource(uri: str) -> Dict[str, Any]:
    """
    Handle trading-related resource requests.
    
    Supported URIs:
    - trading://account/info - Account information
    - trading://account/positions - All positions
    - trading://account/orders - Recent orders
    - trading://portfolio/summary - Portfolio analysis
    - trading://symbols/active - Currently tracked symbols
    - trading://system/health - System health check
    - trading://system/memory - Memory usage statistics
    
    Args:
        uri: Resource URI like 'trading://account/info'
        
    Returns:
        Dict with resource_data or error
    """
    try:
        # Parse URI
        parsed = urllib.parse.urlparse(uri)
        scheme = parsed.scheme
        
        # Validate scheme
        if scheme != "trading":
            return {"error": f"Unsupported scheme: {scheme}. Expected 'trading'"}
        
        # Handle netloc (hostname) as category and path as resource
        category = parsed.netloc
        resource = parsed.path.strip('/')
        
        if not category or not resource:
            return {"error": f"Invalid URI format: {uri}. Expected format: trading://category/resource"}
        
        # Route based on category
        if category == "account":
            return await _handle_account_resource(resource)
        elif category == "portfolio":
            return await _handle_portfolio_resource(resource)
        elif category == "symbols":
            return await _handle_symbols_resource(resource)
        elif category == "system":
            return await _handle_system_resource(resource)
        else:
            return {"error": f"Unknown resource category: {category}"}
            
    except Exception as e:
        logger.error(f"Error handling trading resource {uri}: {e}")
        return {"error": f"Failed to get resource: {str(e)}"}

async def _handle_account_resource(resource: str) -> Dict[str, Any]:
    """Handle account-related resources."""
    trading_client = AlpacaClientManager.get_trading_client()
    
    if resource == "info":
        account = trading_client.get_account()  # type: ignore
        return {
            "resource_data": {
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
                "daytrade_count": getattr(account, 'daytrade_count', 0)
            }
        }
    
    elif resource == "positions":
        positions = trading_client.get_all_positions()  # type: ignore
        positions_data = []
        
        for position in positions:
            if hasattr(position, 'symbol'):
                positions_data.append({
                    "symbol": position.symbol,
                    "quantity": float(position.qty),
                    "market_value": float(position.market_value or 0),
                    "avg_entry_price": float(position.avg_entry_price or 0),
                    "current_price": float(position.current_price or 0),
                    "unrealized_pl": float(position.unrealized_pl or 0),
                    "unrealized_plpc": float(position.unrealized_plpc or 0)
                })
        
        return {"resource_data": positions_data}
    
    elif resource == "orders":
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        
        # Get recent orders (last 50)
        orders_request = GetOrdersRequest(status=QueryOrderStatus.ALL, limit=50)
        orders = trading_client.get_orders(filter=orders_request)  # type: ignore
        
        orders_data = []
        for order in orders:
            if hasattr(order, 'id'):
                order_data = {
                    "order_id": str(order.id),
                    "symbol": order.symbol,
                    "side": str(order.side).lower(),
                    "order_type": str(order.order_type).lower(),
                    "quantity": float(order.qty or 0),
                    "status": str(order.status),
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0
                }
                orders_data.append(order_data)
        
        return {"resource_data": orders_data}
    
    else:
        return {"error": f"Unknown account resource: {resource}"}

async def _handle_portfolio_resource(resource: str) -> Dict[str, Any]:
    """Handle portfolio-related resources."""
    if resource == "summary":
        portfolio = StateManager.get_portfolio()
        if not portfolio:
            return {"error": "No portfolio data available. Please call account tools first."}
        
        return {
            "resource_data": {
                "portfolio_metrics": portfolio.portfolio_metrics,
                "entity_count": len(portfolio.entities),
                "suggested_operations": portfolio.suggested_operations,
                "last_updated": portfolio.last_updated.isoformat()
            }
        }
    
    elif resource == "entities":
        portfolio = StateManager.get_portfolio()
        if not portfolio:
            return {"error": "No portfolio data available"}
        
        entities_data = []
        for entity in portfolio.entities.values():
            entities_data.append({
                "name": entity.name,
                "entity_type": entity.entity_type.value,
                "suggested_role": entity.suggested_role.value,
                "characteristics": entity.characteristics
            })
        
        return {"resource_data": entities_data}
    
    else:
        return {"error": f"Unknown portfolio resource: {resource}"}

async def _handle_symbols_resource(resource: str) -> Dict[str, Any]:
    """Handle symbols-related resources."""
    if resource == "active":
        symbols = StateManager.get_all_symbols()
        
        symbols_data = []
        for symbol, entity_info in symbols.items():
            symbols_data.append({
                "symbol": symbol,
                "entity_type": entity_info.entity_type.value,
                "suggested_role": entity_info.suggested_role.value,
                "characteristics": entity_info.characteristics,
                "metadata": entity_info.metadata
            })
        
        return {"resource_data": symbols_data}
    
    elif resource == "count":
        symbols = StateManager.get_all_symbols()
        return {
            "resource_data": {
                "total_symbols": len(symbols),
                "by_type": {}
            }
        }
    
    else:
        return {"error": f"Unknown symbols resource: {resource}"}

async def _handle_system_resource(resource: str) -> Dict[str, Any]:
    """Handle system-related resources."""
    if resource == "health":
        health_results = AlpacaClientManager.health_check()
        return {"resource_data": health_results}
    
    elif resource == "memory":
        memory_usage = StateManager.get_memory_usage()
        return {"resource_data": memory_usage}
    
    elif resource == "status":
        from ..config.simple_settings import settings
        
        status_data = {
            "server_name": settings.server_name,
            "paper_trading": settings.alpaca_paper_trade,
            "log_level": settings.log_level,
            "memory_usage": StateManager.get_memory_usage(),
            "client_health": AlpacaClientManager.health_check()
        }
        
        return {"resource_data": status_data}
    
    else:
        return {"error": f"Unknown system resource: {resource}"}