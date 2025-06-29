# Alpaca-py SDK Reference for AI Development

This document provides AI-optimized reference for the Alpaca-py SDK used in our MCP server implementation.

## 📦 Core SDK Components

### Client Management
```python
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream

# Initialize clients
trading_client = TradingClient(api_key="key", secret_key="secret", paper=True)
stock_client = StockHistoricalDataClient(api_key="key", secret_key="secret")
```

### Account Information
```python
# Get account details
account = trading_client.get_account()
print(f"Buying Power: ${account.buying_power}")
print(f"Portfolio Value: ${account.portfolio_value}")
print(f"Cash: ${account.cash}")
print(f"Day Trade Count: {account.day_trade_count}")
```

### Position Management
```python
# Get all positions
positions = trading_client.get_all_positions()
for position in positions:
    print(f"{position.symbol}: {position.qty} shares")
    print(f"Market Value: ${position.market_value}")
    print(f"Unrealized P&L: ${position.unrealized_pl}")

# Get specific position
position = trading_client.get_open_position("AAPL")
```

### Market Data - Real-Time Quotes
```python
from alpaca.data.requests import StockLatestQuoteRequest

# Get latest quote
quote_request = StockLatestQuoteRequest(symbol_or_symbols=["AAPL"])
quotes = stock_client.get_stock_latest_quote(quote_request)

quote = quotes["AAPL"]
print(f"Bid: ${quote.bid_price} x {quote.bid_size}")
print(f"Ask: ${quote.ask_price} x {quote.ask_size}")
print(f"Timestamp: {quote.timestamp}")
```

### Market Data - Latest Trades
```python
from alpaca.data.requests import StockLatestTradeRequest

# Get latest trade
trade_request = StockLatestTradeRequest(symbol_or_symbols=["AAPL"])
trades = stock_client.get_stock_latest_trade(trade_request)

trade = trades["AAPL"]
print(f"Price: ${trade.price}")
print(f"Size: {trade.size}")
print(f"Exchange: {trade.exchange}")
```

### Market Data - Comprehensive Snapshots
```python
from alpaca.data.requests import StockSnapshotRequest

# Get comprehensive market data
snapshot_request = StockSnapshotRequest(symbol_or_symbols=["AAPL", "MSFT", "GOOGL"])
snapshots = stock_client.get_stock_snapshot(snapshot_request)

for symbol, snapshot in snapshots.items():
    print(f"\n{symbol} Snapshot:")
    
    # Latest quote
    if snapshot.latest_quote:
        quote = snapshot.latest_quote
        print(f"  Quote: ${quote.bid_price} x {quote.ask_price}")
    
    # Latest trade
    if snapshot.latest_trade:
        trade = snapshot.latest_trade
        print(f"  Trade: ${trade.price} ({trade.size} shares)")
    
    # Daily bar
    if snapshot.daily_bar:
        bar = snapshot.daily_bar
        print(f"  Daily: O:${bar.open} H:${bar.high} L:${bar.low} C:${bar.close}")
        print(f"  Volume: {bar.volume:,}")
    
    # Previous daily bar
    if snapshot.previous_daily_bar:
        prev_bar = snapshot.previous_daily_bar
        print(f"  Prev Close: ${prev_bar.close}")
```

### Historical Data - Bars
```python
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import datetime, timedelta

# Define timeframes
timeframes = {
    "1Min": TimeFrame(1, TimeFrameUnit.Minute),
    "5Min": TimeFrame(5, TimeFrameUnit.Minute),
    "15Min": TimeFrame(15, TimeFrameUnit.Minute),
    "1Hour": TimeFrame(1, TimeFrameUnit.Hour),
    "1Day": TimeFrame(1, TimeFrameUnit.Day)
}

# Get historical bars
bars_request = StockBarsRequest(
    symbol_or_symbols=["AAPL"],
    timeframe=timeframes["1Day"],
    start=datetime.now() - timedelta(days=30),
    end=datetime.now(),
    limit=100
)

bars = stock_client.get_stock_bars(bars_request)

# Access data through .data attribute
symbol_bars = bars.data["AAPL"]
for bar in symbol_bars:
    print(f"{bar.timestamp}: O:${bar.open} H:${bar.high} L:${bar.low} C:${bar.close}")
    print(f"  Volume: {bar.volume:,}")
    if hasattr(bar, 'trade_count'):
        print(f"  Trades: {bar.trade_count}")
    if hasattr(bar, 'vwap'):
        print(f"  VWAP: ${bar.vwap:.2f}")
```

### Order Management - Market Orders
```python
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# Place market order
market_order_data = MarketOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY
)

order = trading_client.submit_order(order_data=market_order_data)
print(f"Order ID: {order.id}")
print(f"Status: {order.status}")
print(f"Symbol: {order.symbol}")
print(f"Qty: {order.qty}")
print(f"Side: {order.side}")
```

### Order Management - Limit Orders
```python
from alpaca.trading.requests import LimitOrderRequest

# Place limit order
limit_order_data = LimitOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY,
    limit_price=150.00
)

order = trading_client.submit_order(order_data=limit_order_data)
print(f"Limit Order placed at ${order.limit_price}")
```

### Order Management - Stop Loss Orders
```python
from alpaca.trading.requests import StopOrderRequest

# Place stop loss order
stop_order_data = StopOrderRequest(
    symbol="AAPL",
    qty=10,
    side=OrderSide.SELL,
    time_in_force=TimeInForce.DAY,
    stop_price=140.00
)

order = trading_client.submit_order(order_data=stop_order_data)
print(f"Stop Loss placed at ${order.stop_price}")
```

### Order Management - Retrieval and Management
```python
from alpaca.trading.enums import QueryOrderStatus

# Get all orders
orders = trading_client.get_orders()
for order in orders:
    print(f"{order.symbol}: {order.side} {order.qty} @ {order.status}")

# Get orders by status
open_orders = trading_client.get_orders(status=QueryOrderStatus.OPEN)
filled_orders = trading_client.get_orders(status=QueryOrderStatus.FILLED)

# Get specific order
order = trading_client.get_order_by_id("order_id_here")

# Cancel order
trading_client.cancel_order_by_id("order_id_here")

# Cancel all orders
trading_client.cancel_orders()
```

## 🔧 Error Handling Patterns

### Common Exceptions
```python
from alpaca.trading.requests import MarketOrderRequest
from alpaca.common.exceptions import APIError

try:
    order = trading_client.submit_order(order_data=market_order_data)
except APIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Market Data Error Handling
```python
try:
    quotes = stock_client.get_stock_latest_quote(quote_request)
    if symbol not in quotes:
        print(f"No quote data for {symbol}")
except APIError as e:
    print(f"Market data error: {e}")
```

## 📊 Data Structures

### Account Object
```python
account = trading_client.get_account()
# Available attributes:
account.id                    # Account ID
account.account_number       # Account number
account.status              # Account status
account.crypto_status       # Crypto trading status
account.currency            # Account currency
account.buying_power        # Available buying power
account.regt_buying_power   # RegT buying power
account.daytrading_buying_power  # Day trading buying power
account.cash                # Cash balance
account.portfolio_value     # Total portfolio value
account.equity              # Equity value
account.last_equity         # Previous day equity
account.multiplier          # Account multiplier
account.day_trade_count     # Pattern day trader count
account.daytrade_count      # Current day trade count
```

### Position Object
```python
position = trading_client.get_open_position("AAPL")
# Available attributes:
position.asset_id           # Asset ID
position.symbol             # Stock symbol
position.exchange           # Exchange
position.asset_class        # Asset class
position.qty                # Quantity held
position.avg_entry_price    # Average entry price
position.side               # Long/Short
position.market_value       # Current market value
position.cost_basis         # Cost basis
position.unrealized_pl      # Unrealized P&L
position.unrealized_plpc    # Unrealized P&L percentage
position.unrealized_intraday_pl    # Intraday P&L
position.unrealized_intraday_plpc  # Intraday P&L percentage
position.current_price      # Current market price
position.lastday_price      # Previous day price
position.change_today       # Today's change
```

### Order Object
```python
order = trading_client.get_order_by_id("order_id")
# Available attributes:
order.id                    # Order ID
order.client_order_id       # Client order ID
order.created_at            # Creation timestamp
order.updated_at            # Last update timestamp
order.submitted_at          # Submission timestamp
order.filled_at             # Fill timestamp
order.expired_at            # Expiration timestamp
order.canceled_at           # Cancellation timestamp
order.failed_at             # Failure timestamp
order.replaced_at           # Replacement timestamp
order.replaced_by           # Replacement order ID
order.replaces              # Original order ID
order.asset_id              # Asset ID
order.symbol                # Stock symbol
order.asset_class           # Asset class
order.notional              # Notional value
order.qty                   # Quantity
order.filled_qty            # Filled quantity
order.filled_avg_price      # Average fill price
order.order_class           # Order class
order.order_type            # Order type
order.type                  # Order type (alias)
order.side                  # Buy/Sell
order.time_in_force         # Time in force
order.limit_price           # Limit price
order.stop_price            # Stop price
order.status                # Order status
order.extended_hours        # Extended hours flag
order.legs                  # Multi-leg orders
order.trail_percent         # Trailing stop percentage
order.trail_price           # Trailing stop price
order.hwm                   # High water mark
```

### Bar Object
```python
# From historical bars request
bar = symbol_bars[0]
# Available attributes:
bar.timestamp               # Bar timestamp
bar.open                    # Open price
bar.high                    # High price
bar.low                     # Low price
bar.close                   # Close price
bar.volume                  # Volume
bar.trade_count             # Number of trades (if available)
bar.vwap                    # Volume weighted average price (if available)
```

### Quote Object
```python
quote = quotes["AAPL"]
# Available attributes:
quote.timestamp             # Quote timestamp
quote.bid_price             # Bid price
quote.bid_size              # Bid size
quote.ask_price             # Ask price
quote.ask_size              # Ask size
quote.bid_exchange          # Bid exchange
quote.ask_exchange          # Ask exchange
```

### Trade Object
```python
trade = trades["AAPL"]
# Available attributes:
trade.timestamp             # Trade timestamp
trade.price                 # Trade price
trade.size                  # Trade size
trade.exchange              # Exchange
trade.conditions            # Trade conditions
trade.id                    # Trade ID
trade.sip_timestamp         # SIP timestamp
```

## 🚀 Advanced Patterns

### Batch Operations
```python
# Multiple symbols in single request
symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Batch quotes
quote_request = StockLatestQuoteRequest(symbol_or_symbols=symbols)
quotes = stock_client.get_stock_latest_quote(quote_request)

# Batch snapshots
snapshot_request = StockSnapshotRequest(symbol_or_symbols=symbols)
snapshots = stock_client.get_stock_snapshot(snapshot_request)

# Batch historical data
bars_request = StockBarsRequest(
    symbol_or_symbols=symbols,
    timeframe=TimeFrame(1, TimeFrameUnit.Day),
    start=datetime.now() - timedelta(days=7),
    limit=50
)
bars = stock_client.get_stock_bars(bars_request)
```

### Paper Trading vs Live Trading
```python
# Paper trading (recommended for development)
trading_client = TradingClient(
    api_key="your_api_key",
    secret_key="your_secret_key",
    paper=True  # Paper trading mode
)

# Live trading (production only)
trading_client = TradingClient(
    api_key="your_api_key",
    secret_key="your_secret_key",
    paper=False  # Live trading mode
)
```

### Environment Configuration
```python
import os

# Environment-based configuration
API_KEY = os.getenv('ALPACA_API_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET_KEY')
PAPER_TRADE = os.getenv('ALPACA_PAPER_TRADE', 'True').lower() == 'true'

trading_client = TradingClient(
    api_key=API_KEY,
    secret_key=SECRET_KEY,
    paper=PAPER_TRADE
)
```

## 📝 Best Practices

### 1. Error Handling
- Always wrap API calls in try-catch blocks
- Handle rate limiting gracefully
- Log errors with sufficient context
- Provide fallback behavior for non-critical operations

### 2. Data Validation
- Validate symbols before API calls
- Check for None values in optional fields
- Validate date ranges for historical data
- Sanitize user inputs

### 3. Performance Optimization
- Use batch requests when possible
- Cache frequently accessed data
- Implement proper pagination for large datasets
- Monitor API rate limits

### 4. Security
- Never hardcode API keys
- Use environment variables or secure vaults
- Validate all inputs from external sources
- Implement proper logging without exposing secrets

This reference provides the essential Alpaca-py SDK patterns used throughout our MCP server implementation. For complete API documentation, refer to the official Alpaca documentation at https://docs.alpaca.markets/