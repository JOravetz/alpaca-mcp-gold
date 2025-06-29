"""
Order management tools following gold standard patterns.
Handles order placement, modification, and tracking.
"""

import logging
from typing import Dict, Any, Optional, List
from decimal import Decimal
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    StopLimitOrderRequest,
    TrailingStopOrderRequest,
    GetOrdersRequest
)
from alpaca.trading.enums import (
    OrderSide,
    OrderType,
    TimeInForce,
    QueryOrderStatus
)
from ..models.alpaca_clients import AlpacaClientManager
from ..models.schemas import StateManager, EntityInfo, TradingEntityType

logger = logging.getLogger(__name__)

async def place_market_order(
    symbol: str,
    side: str,
    quantity: float,
    time_in_force: str = "day"
) -> Dict[str, Any]:
    """
    Places a market order for a stock.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        time_in_force: 'day', 'gtc', 'ioc', 'fok' (default: 'day')
    
    Returns:
        Dict with status and order data or error message
    """
    try:
        # Input validation
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
        
        if side.lower() not in ['buy', 'sell']:
            return {
                "status": "error", 
                "message": "Side must be 'buy' or 'sell'"
            }
        
        if quantity <= 0:
            return {
                "status": "error",
                "message": "Quantity must be greater than 0"
            }
        
        symbol = symbol.upper()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        
        # Map time in force
        tif_mapping = {
            'day': TimeInForce.DAY,
            'gtc': TimeInForce.GTC,
            'ioc': TimeInForce.IOC,
            'fok': TimeInForce.FOK
        }
        
        if time_in_force.lower() not in tif_mapping:
            return {
                "status": "error",
                "message": f"Invalid time_in_force. Supported: {list(tif_mapping.keys())}"
            }
        
        tif = tif_mapping[time_in_force.lower()]
        
        trading_client = AlpacaClientManager.get_trading_client()
        
        # Create market order request
        market_order = MarketOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=tif
        )
        
        # Submit order
        order = trading_client.submit_order(order_data=market_order)
        
        # Track order entity
        order_info = EntityInfo(
            name=f"order_{order.id}",
            entity_type=TradingEntityType.ORDER,
            characteristics={
                "order_type": "market",
                "symbol": symbol,
                "side": side.lower(),
                "quantity": quantity,
                "status": str(order.status)
            },
            suggested_role=EntityInfo.EntityRole.SPECULATIVE,
            metadata={"order_id": str(order.id)}
        )
        StateManager.add_symbol(f"order_{order.id}", order_info)
        
        order_data = {
            "order_id": str(order.id),
            "symbol": symbol,
            "side": side.lower(),
            "order_type": "market",
            "quantity": float(quantity),
            "status": str(order.status),
            "time_in_force": time_in_force.lower(),
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
        }
        
        return {
            "status": "success",
            "data": order_data,
            "metadata": {
                "operation": "place_market_order",
                "order_tracking": order_info.characteristics
            }
        }
        
    except Exception as e:
        logger.error(f"Error placing market order for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to place market order: {str(e)}",
            "error_type": type(e).__name__
        }

async def place_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    limit_price: float,
    time_in_force: str = "day"
) -> Dict[str, Any]:
    """
    Places a limit order for a stock.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        limit_price: The limit price for the order
        time_in_force: 'day', 'gtc', 'ioc', 'fok' (default: 'day')
    
    Returns:
        Dict with status and order data or error message
    """
    try:
        # Input validation
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
        
        if side.lower() not in ['buy', 'sell']:
            return {
                "status": "error",
                "message": "Side must be 'buy' or 'sell'"
            }
        
        if quantity <= 0:
            return {
                "status": "error",
                "message": "Quantity must be greater than 0"
            }
        
        if limit_price <= 0:
            return {
                "status": "error",
                "message": "Limit price must be greater than 0"
            }
        
        symbol = symbol.upper()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        
        # Map time in force
        tif_mapping = {
            'day': TimeInForce.DAY,
            'gtc': TimeInForce.GTC,
            'ioc': TimeInForce.IOC,
            'fok': TimeInForce.FOK
        }
        
        if time_in_force.lower() not in tif_mapping:
            return {
                "status": "error",
                "message": f"Invalid time_in_force. Supported: {list(tif_mapping.keys())}"
            }
        
        tif = tif_mapping[time_in_force.lower()]
        
        trading_client = AlpacaClientManager.get_trading_client()
        
        # Create limit order request
        limit_order = LimitOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=tif,
            limit_price=limit_price
        )
        
        # Submit order
        order = trading_client.submit_order(order_data=limit_order)
        
        # Track order entity
        order_info = EntityInfo(
            name=f"order_{order.id}",
            entity_type=TradingEntityType.ORDER,
            characteristics={
                "order_type": "limit",
                "symbol": symbol,
                "side": side.lower(),
                "quantity": quantity,
                "limit_price": limit_price,
                "status": str(order.status)
            },
            suggested_role=EntityInfo.EntityRole.SPECULATIVE,
            metadata={"order_id": str(order.id)}
        )
        StateManager.add_symbol(f"order_{order.id}", order_info)
        
        order_data = {
            "order_id": str(order.id),
            "symbol": symbol,
            "side": side.lower(),
            "order_type": "limit",
            "quantity": float(quantity),
            "limit_price": float(limit_price),
            "status": str(order.status),
            "time_in_force": time_in_force.lower(),
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
        }
        
        return {
            "status": "success",
            "data": order_data,
            "metadata": {
                "operation": "place_limit_order",
                "order_tracking": order_info.characteristics
            }
        }
        
    except Exception as e:
        logger.error(f"Error placing limit order for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to place limit order: {str(e)}",
            "error_type": type(e).__name__
        }

async def place_stop_loss_order(
    symbol: str,
    side: str,
    quantity: float,
    stop_price: float,
    time_in_force: str = "day"
) -> Dict[str, Any]:
    """
    Places a stop loss order for a stock.
    
    Args:
        symbol: The stock symbol to trade (e.g., 'AAPL', 'MSFT')
        side: 'buy' or 'sell'
        quantity: Number of shares to trade
        stop_price: The stop price for the order
        time_in_force: 'day', 'gtc' (default: 'day')
    
    Returns:
        Dict with status and order data or error message
    """
    try:
        # Input validation (similar to limit order)
        if not symbol:
            return {"status": "error", "message": "Symbol parameter cannot be empty"}
        
        if side.lower() not in ['buy', 'sell']:
            return {"status": "error", "message": "Side must be 'buy' or 'sell'"}
        
        if quantity <= 0:
            return {"status": "error", "message": "Quantity must be greater than 0"}
        
        if stop_price <= 0:
            return {"status": "error", "message": "Stop price must be greater than 0"}
        
        symbol = symbol.upper()
        order_side = OrderSide.BUY if side.lower() == 'buy' else OrderSide.SELL
        
        # Map time in force (stop orders typically use DAY or GTC)
        tif_mapping = {
            'day': TimeInForce.DAY,
            'gtc': TimeInForce.GTC
        }
        
        if time_in_force.lower() not in tif_mapping:
            return {
                "status": "error",
                "message": f"Invalid time_in_force for stop order. Supported: {list(tif_mapping.keys())}"
            }
        
        tif = tif_mapping[time_in_force.lower()]
        
        trading_client = AlpacaClientManager.get_trading_client()
        
        # Create stop order request
        stop_order = StopOrderRequest(
            symbol=symbol,
            qty=quantity,
            side=order_side,
            time_in_force=tif,
            stop_price=stop_price
        )
        
        # Submit order
        order = trading_client.submit_order(order_data=stop_order)
        
        # Track order entity
        order_info = EntityInfo(
            name=f"order_{order.id}",
            entity_type=TradingEntityType.ORDER,
            characteristics={
                "order_type": "stop",
                "symbol": symbol,
                "side": side.lower(),
                "quantity": quantity,
                "stop_price": stop_price,
                "status": str(order.status)
            },
            suggested_role=EntityInfo.EntityRole.HEDGE_INSTRUMENT,
            metadata={"order_id": str(order.id)}
        )
        StateManager.add_symbol(f"order_{order.id}", order_info)
        
        order_data = {
            "order_id": str(order.id),
            "symbol": symbol,
            "side": side.lower(),
            "order_type": "stop",
            "quantity": float(quantity),
            "stop_price": float(stop_price),
            "status": str(order.status),
            "time_in_force": time_in_force.lower(),
            "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None
        }
        
        return {
            "status": "success",
            "data": order_data,
            "metadata": {
                "operation": "place_stop_loss_order",
                "order_tracking": order_info.characteristics
            }
        }
        
    except Exception as e:
        logger.error(f"Error placing stop order for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to place stop order: {str(e)}",
            "error_type": type(e).__name__
        }

async def get_orders(
    status: Optional[str] = None,
    limit: int = 50,
    symbols: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Retrieves orders based on filters.
    
    Args:
        status: Filter by order status ('open', 'closed', 'all') (optional)
        limit: Maximum number of orders to return (default 50, max 500)
        symbols: List of symbols to filter by (optional)
    
    Returns:
        Dict with status and orders data or error message
    """
    try:
        # Validate limit
        limit = max(1, min(limit, 500))
        
        trading_client = AlpacaClientManager.get_trading_client()
        
        # Map status
        status_mapping = {
            'open': QueryOrderStatus.OPEN,
            'closed': QueryOrderStatus.CLOSED,
            'all': QueryOrderStatus.ALL
        }
        
        query_status = None
        if status and status.lower() in status_mapping:
            query_status = status_mapping[status.lower()]
        
        # Create orders request
        orders_request = GetOrdersRequest(
            status=query_status,
            limit=limit,
            symbols=symbols
        )
        
        # Get orders
        orders = trading_client.get_orders(filter=orders_request)
        
        orders_data = []
        for order in orders:
            order_data = {
                "order_id": str(order.id),
                "symbol": order.symbol,
                "side": str(order.side).lower(),
                "order_type": str(order.order_type).lower(),
                "quantity": float(order.qty),
                "status": str(order.status),
                "time_in_force": str(order.time_in_force).lower(),
                "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None,
                "canceled_at": order.canceled_at.isoformat() if order.canceled_at else None
            }
            
            # Add order-specific fields
            if hasattr(order, 'limit_price') and order.limit_price:
                order_data["limit_price"] = float(order.limit_price)
            if hasattr(order, 'stop_price') and order.stop_price:
                order_data["stop_price"] = float(order.stop_price)
            if hasattr(order, 'trail_price') and order.trail_price:
                order_data["trail_price"] = float(order.trail_price)
            if hasattr(order, 'trail_percent') and order.trail_percent:
                order_data["trail_percent"] = float(order.trail_percent)
                
            orders_data.append(order_data)
        
        # Generate summary statistics
        summary = {
            "total_orders": len(orders_data),
            "by_status": {},
            "by_side": {},
            "by_type": {}
        }
        
        for order in orders_data:
            # Count by status
            status_key = order["status"]
            summary["by_status"][status_key] = summary["by_status"].get(status_key, 0) + 1
            
            # Count by side
            side_key = order["side"]
            summary["by_side"][side_key] = summary["by_side"].get(side_key, 0) + 1
            
            # Count by type
            type_key = order["order_type"]
            summary["by_type"][type_key] = summary["by_type"].get(type_key, 0) + 1
        
        return {
            "status": "success",
            "data": {
                "orders": orders_data,
                "summary": summary
            },
            "metadata": {
                "operation": "get_orders",
                "request_params": {
                    "status": status,
                    "limit": limit,
                    "symbols": symbols
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve orders: {str(e)}",
            "error_type": type(e).__name__
        }

async def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancels an existing order.
    
    Args:
        order_id: The ID of the order to cancel
    
    Returns:
        Dict with status and cancellation result or error message
    """
    try:
        if not order_id:
            return {
                "status": "error",
                "message": "Order ID parameter cannot be empty"
            }
        
        trading_client = AlpacaClientManager.get_trading_client()
        
        # Cancel the order
        trading_client.cancel_order_by_id(order_id)
        
        # Update order entity if tracked
        order_entity = StateManager.get_symbol(f"order_{order_id}")
        if order_entity:
            order_entity.characteristics["status"] = "canceled"
            StateManager.add_symbol(f"order_{order_id}", order_entity)
        
        return {
            "status": "success",
            "data": {
                "order_id": order_id,
                "cancellation_status": "requested"
            },
            "metadata": {
                "operation": "cancel_order",
                "message": "Order cancellation requested successfully"
            }
        }
        
    except Exception as e:
        logger.error(f"Error canceling order {order_id}: {e}")
        return {
            "status": "error",
            "message": f"Failed to cancel order {order_id}: {str(e)}",
            "error_type": type(e).__name__
        }