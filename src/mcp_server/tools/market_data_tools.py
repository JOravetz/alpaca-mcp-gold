"""
Market data tools following gold standard patterns.
Handles stock quotes, historical data, and market information.
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from alpaca.data.requests import (
    StockLatestQuoteRequest,
    StockLatestTradeRequest,
    StockBarsRequest,
    StockSnapshotRequest,
)
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from ..models.alpaca_clients import AlpacaClientManager
from ..models.schemas import StateManager, EntityInfo
from ..config.simple_settings import settings

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
                "message": "Symbol parameter cannot be empty",
                "error_type": "ValueError",
            }

        symbol = symbol.upper()
        stock_client = AlpacaClientManager.get_stock_data_client()

        # Get latest quote
        quote_request = StockLatestQuoteRequest(symbol_or_symbols=[symbol])
        quotes = stock_client.get_stock_latest_quote(quote_request)

        if symbol not in quotes:
            return {
                "status": "error",
                "message": f"No quote data found for symbol {symbol}",
            }

        quote = quotes[symbol]

        # Calculate additional metrics
        bid_ask_spread = float(quote.ask_price) - float(quote.bid_price)
        spread_percentage = (
            (bid_ask_spread / float(quote.ask_price)) * 100
            if quote.ask_price > 0
            else 0
        )

        # Create entity info for adaptive insights
        stock_data = {
            "price_change_percent": 0,  # Will be calculated with trade data
            "volume": 0,  # Will be added with trade data
            "bid_ask_spread": spread_percentage,
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
            "exchange": (
                quote.bid_exchange if hasattr(quote, "bid_exchange") else "Unknown"
            ),
        }

        # Store entity info
        entity_info = EntityInfo.from_stock_data(symbol, stock_data)
        StateManager.add_symbol(symbol, entity_info)

        return {
            "status": "success",
            "data": quote_data,
            "metadata": {
                "operation": "get_stock_quote",
                "entity_insights": entity_info.characteristics,
            },
        }

    except Exception as e:
        logger.error(f"Error getting quote for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve quote for {symbol}: {str(e)}",
            "error_type": type(e).__name__,
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
                "message": "Symbol parameter cannot be empty",
                "error_type": "ValueError",
            }

        symbol = symbol.upper()
        stock_client = AlpacaClientManager.get_stock_data_client()

        # Get latest trade
        trade_request = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        trades = stock_client.get_stock_latest_trade(trade_request)

        if symbol not in trades:
            return {
                "status": "error",
                "message": f"No trade data found for symbol {symbol}",
            }

        trade = trades[symbol]

        trade_data = {
            "symbol": symbol,
            "price": float(trade.price),
            "size": int(trade.size),
            "timestamp": trade.timestamp.isoformat(),
            "exchange": trade.exchange if hasattr(trade, "exchange") else "Unknown",
            "conditions": trade.conditions if hasattr(trade, "conditions") else [],
        }

        # Update entity info with trade data
        existing_entity = StateManager.get_symbol(symbol)
        if existing_entity:
            existing_entity.characteristics.update(
                {"latest_price": float(trade.price), "latest_volume": int(trade.size)}
            )
            StateManager.add_symbol(symbol, existing_entity)

        return {
            "status": "success",
            "data": trade_data,
            "metadata": {"operation": "get_stock_trade"},
        }

    except Exception as e:
        logger.error(f"Error getting trade for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve trade for {symbol}: {str(e)}",
            "error_type": type(e).__name__,
        }


async def get_stock_snapshot(symbols: str) -> Dict[str, Any]:
    """
    Retrieves comprehensive snapshot data for one or more stocks including latest quote, trade, and daily bar.

    Args:
        symbols: Single stock symbol or comma-separated symbols (e.g., 'AAPL' or 'AAPL,MSFT,GOOGL')

    Returns:
        Dict with status and comprehensive snapshot data or error message
    """
    try:
        if not symbols:
            return {
                "status": "error",
                "message": "Symbols parameter cannot be empty",
                "error_type": "ValueError",
            }

        # Parse comma-separated symbols
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]

        if not symbol_list:
            return {"status": "error", "message": "No valid symbols provided"}

        stock_client = AlpacaClientManager.get_stock_data_client()

        # Get stock snapshots for all symbols in one API call
        snapshot_request = StockSnapshotRequest(symbol_or_symbols=symbol_list)
        snapshots = stock_client.get_stock_snapshot(snapshot_request)

        if not snapshots:
            return {
                "status": "error",
                "message": f"No snapshot data found for symbols: {', '.join(symbol_list)}",
            }

        # Process all symbols and build response data
        all_snapshots = {}

        for symbol in symbol_list:
            if symbol not in snapshots:
                logger.warning(f"No snapshot data found for symbol {symbol}")
                continue

            snapshot = snapshots[symbol]

            # Extract data from snapshot
            snapshot_data = {"symbol": symbol}

            # Latest quote
            if snapshot.latest_quote:
                quote = snapshot.latest_quote
                snapshot_data.update(
                    {
                        "latest_quote": {
                            "bid_price": float(quote.bid_price),
                            "ask_price": float(quote.ask_price),
                            "bid_size": int(quote.bid_size),
                            "ask_size": int(quote.ask_size),
                            "timestamp": quote.timestamp.isoformat(),
                        }
                    }
                )

            # Latest trade
            if snapshot.latest_trade:
                trade = snapshot.latest_trade
                snapshot_data.update(
                    {
                        "latest_trade": {
                            "price": float(trade.price),
                            "size": int(trade.size),
                            "timestamp": trade.timestamp.isoformat(),
                        }
                    }
                )

            # Daily bar
            if snapshot.daily_bar:
                bar = snapshot.daily_bar

                # Calculate daily change from previous close (correct method)
                if (
                    hasattr(snapshot, "previous_daily_bar")
                    and snapshot.previous_daily_bar
                ):
                    prev_close = float(snapshot.previous_daily_bar.close)
                    daily_change = float(bar.close) - prev_close
                    daily_change_pct = (
                        (daily_change / prev_close) * 100 if prev_close > 0 else 0
                    )
                else:
                    # Fallback to open-to-close if no previous data available
                    daily_change = float(bar.close) - float(bar.open)
                    daily_change_pct = (
                        (daily_change / float(bar.open)) * 100 if bar.open > 0 else 0
                    )

                snapshot_data.update(
                    {
                        "daily_bar": {
                            "open": float(bar.open),
                            "high": float(bar.high),
                            "low": float(bar.low),
                            "close": float(bar.close),
                            "volume": int(bar.volume),
                            "daily_change": round(daily_change, 4),
                            "daily_change_percent": round(daily_change_pct, 4),
                            "timestamp": bar.timestamp.isoformat(),
                        }
                    }
                )

                # Create comprehensive entity info
                stock_data = {
                    "price_change_percent": daily_change_pct,
                    "volume": int(bar.volume),
                    "high": float(bar.high),
                    "low": float(bar.low),
                    "volatility": (
                        ((float(bar.high) - float(bar.low)) / float(bar.open)) * 100
                        if bar.open > 0
                        else 0
                    ),
                }
                entity_info = EntityInfo.from_stock_data(symbol, stock_data)
                StateManager.add_symbol(symbol, entity_info)

                snapshot_data["insights"] = {
                    "suggested_role": entity_info.suggested_role.value,
                    "characteristics": entity_info.characteristics,
                }

            # Previous daily bar (if available)
            if hasattr(snapshot, "previous_daily_bar") and snapshot.previous_daily_bar:
                prev_bar = snapshot.previous_daily_bar
                snapshot_data.update(
                    {
                        "prev_daily_bar": {
                            "open": float(prev_bar.open),
                            "high": float(prev_bar.high),
                            "low": float(prev_bar.low),
                            "close": float(prev_bar.close),
                            "volume": int(prev_bar.volume),
                            "timestamp": prev_bar.timestamp.isoformat(),
                        }
                    }
                )

            all_snapshots[symbol] = snapshot_data

        # Return single snapshot data for single symbol, or all snapshots for multiple symbols
        if len(symbol_list) == 1:
            return {
                "status": "success",
                "data": all_snapshots.get(symbol_list[0], {}),
                "metadata": {
                    "operation": "get_stock_snapshot",
                    "symbols_requested": symbol_list,
                    "symbols_found": list(all_snapshots.keys()),
                },
            }
        else:
            return {
                "status": "success",
                "data": all_snapshots,
                "metadata": {
                    "operation": "get_stock_snapshot",
                    "symbols_requested": symbol_list,
                    "symbols_found": list(all_snapshots.keys()),
                    "total_symbols": len(all_snapshots),
                },
            }

    except Exception as e:
        logger.error(f"Error getting snapshot for symbols {symbols}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve snapshot for symbols {symbols}: {str(e)}",
            "error_type": type(e).__name__,
        }


async def get_historical_bars(
    symbol: str,
    timeframe: str = "1Day",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    feed: str = "sip",
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
                "message": "Symbol parameter cannot be empty",
                "error_type": "ValueError",
            }

        symbol = symbol.upper()

        # Parse timeframe
        timeframe_mapping = {
            "1Min": TimeFrame(1, TimeFrameUnit.Minute),
            "5Min": TimeFrame(5, TimeFrameUnit.Minute),
            "15Min": TimeFrame(15, TimeFrameUnit.Minute),
            "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
            "1Day": TimeFrame(1, TimeFrameUnit.Day),
        }

        if timeframe not in timeframe_mapping:
            return {
                "status": "error",
                "message": f"Invalid timeframe. Supported: {list(timeframe_mapping.keys())}",
            }

        tf = timeframe_mapping[timeframe]

        # Set default dates - use correct business day logic
        now = datetime.now()
        
        if not end_date:
            # For end date, use the most recent business day (not future dates)
            # Monday = 0, Sunday = 6
            weekday = now.weekday()
            if weekday == 6:  # Sunday
                end_date_obj = now - timedelta(days=2)  # Friday
            elif weekday == 5:  # Saturday  
                end_date_obj = now - timedelta(days=1)  # Friday
            else:  # Monday-Friday
                end_date_obj = now
            end_date_str = end_date_obj.strftime("%Y-%m-%d")
        else:
            end_date_str = end_date

        if not start_date:
            # For intraday data, use same business day as end date
            if timeframe in ["1Min", "5Min", "15Min", "1Hour"]:
                start_date_str = end_date_str  # Same day for intraday
            else:
                # For daily data, go back appropriate business days from end date
                days_back = 30
                start_date_obj = datetime.strptime(end_date_str, "%Y-%m-%d") - timedelta(days=days_back)
                start_date_str = start_date_obj.strftime("%Y-%m-%d")
        else:
            start_date_str = start_date

        # Validate limit
        limit = max(1, min(limit, 10000))

        # Use direct API call like your working script instead of SDK
        url = "https://data.alpaca.markets/v2/stocks/bars"
        params = {
            'symbols': symbol,
            'timeframe': timeframe,  # Use original timeframe string
            'start': start_date_str,
            'end': end_date_str,
            'limit': limit,
            'adjustment': 'split',
            'feed': feed,
            'sort': 'desc'  # Most recent first
        }

        headers = {
            'APCA-API-KEY-ID': settings.alpaca_api_key,
            'APCA-API-SECRET-KEY': settings.alpaca_secret_key
        }
        
        logger.info(f"Requesting bars for {symbol} from {start_date_str} to {end_date_str} via direct API")
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            api_data = response.json()
            
            # Extract bars for the symbol
            all_bars_raw = api_data.get('bars', {}).get(symbol, [])
            
            if not all_bars_raw:
                return {
                    "status": "error",
                    "message": f"No trading data available for {symbol} in the requested date range {start_date_str} to {end_date_str}. Try a different date range or check if the symbol is correct.",
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching bars via direct API: {e}")
            return {
                "status": "error",
                "message": f"Failed to retrieve historical bars for {symbol}: {str(e)}",
                "error_type": type(e).__name__,
            }

        bars_data = []

        for bar in all_bars_raw:
            # Raw API data - convert from your script's format
            bars_data.append(
                {
                    "timestamp": bar["t"],  # timestamp in ISO format from API
                    "open": float(bar["o"]),
                    "high": float(bar["h"]),
                    "low": float(bar["l"]),
                    "close": float(bar["c"]),
                    "volume": int(bar["v"]),
                    "trade_count": bar.get("n"),
                    "vwap": float(bar.get("vw", 0)) if bar.get("vw") else None,
                }
            )

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
                    "last": closes[-1],
                },
                "volume_stats": {
                    "total": sum(volumes),
                    "average": sum(volumes) / len(volumes),
                    "min": min(volumes),
                    "max": max(volumes),
                },
                "period": {
                    "start": bars_data[0]["timestamp"],
                    "end": bars_data[-1]["timestamp"],
                },
            }
        else:
            summary_stats = {}

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "bars": bars_data,
                "summary": summary_stats,
            },
            "metadata": {
                "operation": "get_historical_bars",
                "request_params": {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "limit": limit,
                },
            },
        }

    except Exception as e:
        logger.error(f"Error getting historical bars for {symbol}: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve historical bars for {symbol}: {str(e)}",
            "error_type": type(e).__name__,
        }
