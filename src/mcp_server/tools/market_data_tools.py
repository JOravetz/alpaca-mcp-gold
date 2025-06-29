"""
Market data tools following gold standard patterns.
Handles stock quotes, historical data, and market information.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockBarsRequest,
    StockSnapshotRequest
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from ..models.alpaca_clients import AlpacaClientManager
from ..models.schemas import StateManager, EntityInfo

logger = logging.getLogger(__name__)

async def get_stock_quote(symbol: str) -> Dict[str, Any]:
    """
    Retrieves and formats the latest quote for a stock.
    
    Args:
        symbol: The stock symbol to get quote for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict with status and quote data or error message
    """
    try:
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
            
        symbol = symbol.upper()
        stock_client = AlpacaClientManager.get_stock_data_client()
        
        # Get latest quote
        quote_request = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
        quotes = stock_client.get_stock_latest_quote(quote_request)
        
        if symbol not in quotes:
            return {
                "status": "error",
                "message": f"No quote data found for symbol {symbol}"
            }
            
        quote = quotes[symbol]
        
        # Calculate additional metrics
        bid_ask_spread = float(quote.ask_price) - float(quote.bid_price)
        spread_percentage = (bid_ask_spread / float(quote.ask_price)) * 100 if quote.ask_price > 0 else 0
        
        # Create entity info for adaptive insights
        stock_data = {
            "price_change_percent": 0,  # Will be calculated with trade data
            "volume": 0,  # Will be added with trade data
            "bid_ask_spread": spread_percentage
        }
        
        quote_data = {
            "symbol": symbol,
            "bid_price": float(quote.bid_price),
            "ask_price": float(quote.ask_price),
            "bid_size": int(quote.bid_size),
            "ask_size": int(quote.ask_size),
            "bid_ask_spread": round(bid_ask_spread, 4),
            "spread_percentage": round(spread_percentage, 4),
            "timestamp": quote.timestamp.isoformat(),
            "exchange": quote.bid_exchange if hasattr(quote, 'bid_exchange') else "Unknown"
        }
        
        # Store entity info
        entity_info = EntityInfo.from_stock_data(symbol, stock_data)
        StateManager.add_symbol(symbol, entity_info)
        
        return {
            "status": "success",
            "data": quote_data,
            "metadata": {
                "operation": "get_stock_quote",
                "entity_insights": entity_info.characteristics
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve quote for {symbol}: {str(e)}",
            "error_type": type(e).__name__
        }

async def get_stock_trade(symbol: str) -> Dict[str, Any]:
    """
    Retrieves the latest trade information for a stock.
    
    Args:
        symbol: The stock symbol to get trade for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict with status and trade data or error message
    """
    try:
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
            
        symbol = symbol.upper()
        stock_client = AlpacaClientManager.get_stock_data_client()
        
        # Get latest trade
        trade_request = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        trades = stock_client.get_stock_latest_trade(trade_request)
        
        if symbol not in trades:
            return {
                "status": "error",
                "message": f"No trade data found for symbol {symbol}"
            }
            
        trade = trades[symbol]
        
        trade_data = {
            "symbol": symbol,
            "price": float(trade.price),
            "size": int(trade.size),
            "timestamp": trade.timestamp.isoformat(),
            "exchange": trade.exchange if hasattr(trade, 'exchange') else "Unknown",
            "conditions": trade.conditions if hasattr(trade, 'conditions') else []
        }
        
        # Update entity info with trade data
        existing_entity = StateManager.get_symbol(symbol)
        if existing_entity:
            existing_entity.characteristics.update({
                "latest_price": float(trade.price),
                "latest_volume": int(trade.size)
            })
            StateManager.add_symbol(symbol, existing_entity)
        
        return {
            "status": "success",
            "data": trade_data,
            "metadata": {
                "operation": "get_stock_trade"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting trade for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve trade for {symbol}: {str(e)}",
            "error_type": type(e).__name__
        }

async def get_stock_snapshot(symbol: str) -> Dict[str, Any]:
    """
    Retrieves comprehensive snapshot data for a stock including latest quote, trade, and daily bar.
    
    Args:
        symbol: The stock symbol to get snapshot for (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dict with status and comprehensive snapshot data or error message
    """
    try:
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
            
        symbol = symbol.upper()
        stock_client = AlpacaClientManager.get_stock_data_client()
        
        # Get stock snapshot
        snapshot_request = StockSnapshotRequest(symbol_or_symbols=[symbol])
        snapshots = stock_client.get_stock_snapshot(snapshot_request)
        
        if symbol not in snapshots:
            return {
                "status": "error",
                "message": f"No snapshot data found for symbol {symbol}"
            }
            
        snapshot = snapshots[symbol]
        
        # Extract data from snapshot
        snapshot_data = {
            "symbol": symbol
        }
        
        # Latest quote
        if snapshot.latest_quote:
            quote = snapshot.latest_quote
            snapshot_data.update({
                "latest_quote": {
                    "bid_price": float(quote.bid_price),
                    "ask_price": float(quote.ask_price),
                    "bid_size": int(quote.bid_size),
                    "ask_size": int(quote.ask_size),
                    "timestamp": quote.timestamp.isoformat()
                }
            })
        
        # Latest trade
        if snapshot.latest_trade:
            trade = snapshot.latest_trade
            snapshot_data.update({
                "latest_trade": {
                    "price": float(trade.price),
                    "size": int(trade.size),
                    "timestamp": trade.timestamp.isoformat()
                }
            })
        
        # Daily bar
        if snapshot.daily_bar:
            bar = snapshot.daily_bar
            daily_change = float(bar.close) - float(bar.open)
            daily_change_pct = (daily_change / float(bar.open)) * 100 if bar.open > 0 else 0
            
            snapshot_data.update({
                "daily_bar": {
                    "open": float(bar.open),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "close": float(bar.close),
                    "volume": int(bar.volume),
                    "daily_change": round(daily_change, 4),
                    "daily_change_percent": round(daily_change_pct, 4),
                    "timestamp": bar.timestamp.isoformat()
                }
            })
            
            # Create comprehensive entity info
            stock_data = {
                "price_change_percent": daily_change_pct,
                "volume": int(bar.volume),
                "high": float(bar.high),
                "low": float(bar.low),
                "volatility": ((float(bar.high) - float(bar.low)) / float(bar.open)) * 100 if bar.open > 0 else 0
            }
            entity_info = EntityInfo.from_stock_data(symbol, stock_data)
            StateManager.add_symbol(symbol, entity_info)
            
            snapshot_data["insights"] = {
                "suggested_role": entity_info.suggested_role.value,
                "characteristics": entity_info.characteristics
            }
        
        # Previous daily bar
        if snapshot.prev_daily_bar:
            prev_bar = snapshot.prev_daily_bar
            snapshot_data.update({
                "prev_daily_bar": {
                    "open": float(prev_bar.open),
                    "high": float(prev_bar.high),
                    "low": float(prev_bar.low),
                    "close": float(prev_bar.close),
                    "volume": int(prev_bar.volume),
                    "timestamp": prev_bar.timestamp.isoformat()
                }
            })
        
        return {
            "status": "success",
            "data": snapshot_data,
            "metadata": {
                "operation": "get_stock_snapshot",
                "data_completeness": {
                    "has_quote": snapshot.latest_quote is not None,
                    "has_trade": snapshot.latest_trade is not None,
                    "has_daily_bar": snapshot.daily_bar is not None,
                    "has_prev_daily_bar": snapshot.prev_daily_bar is not None
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting snapshot for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve snapshot for {symbol}: {str(e)}",
            "error_type": type(e).__name__
        }

async def get_historical_bars(
    symbol: str, 
    timeframe: str = "1Day", 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Retrieves historical bar data for a stock.
    
    Args:
        symbol: The stock symbol to get bars for (e.g., 'AAPL', 'MSFT')
        timeframe: The timeframe for bars ('1Min', '5Min', '15Min', '1Hour', '1Day')
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Maximum number of bars to return (default 100, max 10000)
    
    Returns:
        Dict with status and historical bar data or error message
    """
    try:
        if not symbol:
            return {
                "status": "error",
                "message": "Symbol parameter cannot be empty"
            }
            
        symbol = symbol.upper()
        
        # Parse timeframe
        timeframe_mapping = {
            "1Min": TimeFrame(1, TimeFrameUnit.Minute),
            "5Min": TimeFrame(5, TimeFrameUnit.Minute),
            "15Min": TimeFrame(15, TimeFrameUnit.Minute),
            "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
            "1Day": TimeFrame(1, TimeFrameUnit.Day)
        }
        
        if timeframe not in timeframe_mapping:
            return {
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(timeframe_mapping.keys())}"
            }
        
        tf = timeframe_mapping[timeframe]
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
        if not start_date:
            # Default to 30 days ago for daily, 7 days for intraday
            days_back = 30 if timeframe == "1Day" else 7
            start_date = end_date - timedelta(days=days_back)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        
        # Validate limit
        limit = max(1, min(limit, 10000))
        
        stock_client = AlpacaClientManager.get_stock_data_client()
        
        # Get historical bars
        bars_request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=tf,
            start=start_date,
            end=end_date,
            limit=limit
        )
        bars = stock_client.get_stock_bars(bars_request)
        
        if symbol not in bars:
            return {
                "status": "error",
                "message": f"No historical data found for symbol {symbol}"
            }
            
        bars_data = []
        symbol_bars = bars[symbol]
        
        for bar in symbol_bars:
            bars_data.append({
                "timestamp": bar.timestamp.isoformat(),
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": int(bar.volume),
                "trade_count": getattr(bar, 'trade_count', None),
                "vwap": float(getattr(bar, 'vwap', 0)) if hasattr(bar, 'vwap') else None
            })
        
        # Calculate summary statistics
        if bars_data:
            closes = [bar["close"] for bar in bars_data]
            volumes = [bar["volume"] for bar in bars_data]
            
            summary_stats = {
                "total_bars": len(bars_data),
                "price_range": {
                    "min": min(closes),
                    "max": max(closes),
                    "first": closes[0],
                    "last": closes[-1]
                },
                "volume_stats": {
                    "total": sum(volumes),
                    "average": sum(volumes) / len(volumes),
                    "min": min(volumes),
                    "max": max(volumes)
                },
                "period": {
                    "start": bars_data[0]["timestamp"],
                    "end": bars_data[-1]["timestamp"]
                }
            }
        else:
            summary_stats = {}
        
        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "bars": bars_data,
                "summary": summary_stats
            },
            "metadata": {
                "operation": "get_historical_bars",
                "request_params": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "limit": limit
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting historical bars for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve historical bars for {symbol}: {str(e)}",
            "error_type": type(e).__name__
        }