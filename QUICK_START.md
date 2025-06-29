# Quick Start - Fix MCP Connection

The server failed because it needs valid Alpaca API credentials. Here's how to fix it:

## 🔧 Fix the Connection Issue

### 1. Get Alpaca API Credentials

1. **Sign up for Alpaca** (if you don't have an account):
   - Go to https://alpaca.markets/
   - Create a free paper trading account

2. **Get your API credentials**:
   - Login to your Alpaca dashboard
   - Go to "Settings" → "API Keys"
   - Generate new keys for paper trading
   - Copy your API Key and Secret Key

### 2. Update the .env File

Edit the `.env` file in this directory:

```bash
nano .env
```

Replace the demo credentials with your actual ones:

```env
# Replace these with your actual Alpaca credentials
ALPACA_API_KEY=your_actual_api_key_here
ALPACA_SECRET_KEY=your_actual_secret_key_here
ALPACA_PAPER_TRADE=True

# Keep these MCP settings as-is
MCP_SERVER_NAME=alpaca-trading-gold
LOG_LEVEL=INFO
```

### 3. Test the Server

```bash
# Test that the server starts
uv run --no-project python main.py

# You should see:
# INFO - Starting alpaca-trading-gold MCP server...
# INFO - Paper trading mode: True
```

Press Ctrl+C to stop the test.

### 4. Connect with Claude Code

Now Claude Code should connect successfully:

```bash
claude-code /home/jjoravet/mcp_server_best_practices/alpaca-mcp-gold-standard
```

## 🎯 First Commands to Try

Once connected, test these commands:

```
Get my account information
```

```
Show me a portfolio first look session
```

```
Get a stock quote for AAPL
```

## 🛡️ Safety Notes

- **Paper Trading**: The default configuration uses paper trading (safe mode)
- **No Real Money**: All trades are simulated in paper trading mode
- **Demo Data**: You'll see simulated portfolio data initially

## 💡 Alternative: Demo Mode (Limited)

If you want to test the MCP server architecture without Alpaca credentials, you can temporarily modify the validation:

1. Edit `src/mcp_server/config/simple_settings.py`
2. Comment out the validation lines:

```python
# For development/testing, allow demo credentials
# try:
#     settings.validate()
# except ValueError as e:
#     if any(key in str(e) for key in ["demo_key_please_replace", "demo_secret_please_replace"]):
#         print(f"Warning: {e}")
#         print("The server will start but Alpaca API calls will fail.")
#         print("Please update your .env file with valid credentials for actual trading.")
#     else:
#         raise
```

⚠️ **Note**: In demo mode, all API calls will fail but you can test the MCP architecture.

## 🔍 Troubleshooting

**Server still won't start?**
```bash
# Check your credentials format
cat .env | grep ALPACA

# Verify dependencies
uv run --no-project python -c "import alpaca; print('✓ Alpaca installed')"

# Test basic import
uv run --no-project python -c "from src.mcp_server.config.simple_settings import settings; print('✓ Settings loaded')"
```

**API connection issues?**
- Verify your API keys are correct
- Ensure you're using paper trading keys
- Check that your Alpaca account is active

The gold standard Alpaca MCP server will be ready to use once you complete these steps!