"""
Alpaca client management following gold standard patterns.
Centralized client initialization and management.
"""

import logging
from typing import Optional
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.live.stock import StockDataStream
from alpaca.trading.client import TradingClient
from ..config.simple_settings import settings

logger = logging.getLogger(__name__)


class AlpacaClientManager:
    """Centralized management of Alpaca API clients."""

    _trading_client: Optional[TradingClient] = None
    _stock_data_client: Optional[StockHistoricalDataClient] = None
    _options_data_client: Optional[OptionHistoricalDataClient] = None
    _stock_stream_client: Optional[StockDataStream] = None

    @classmethod
    def get_trading_client(cls) -> TradingClient:
        """Get or create trading client."""
        if cls._trading_client is None:
            logger.info("Initializing Alpaca trading client...")
            cls._trading_client = TradingClient(
                api_key=settings.alpaca_api_key,
                secret_key=settings.alpaca_secret_key,
                paper=settings.alpaca_paper_trade,
                url_override=settings.alpaca_trade_api_url,
            )
            logger.info(
                f"Trading client initialized (paper mode: {settings.alpaca_paper_trade})"
            )
        return cls._trading_client

    @classmethod
    def get_stock_data_client(cls) -> StockHistoricalDataClient:
        """Get or create stock historical data client."""
        if cls._stock_data_client is None:
            logger.info("Initializing Alpaca stock data client...")
            cls._stock_data_client = StockHistoricalDataClient(
                api_key=settings.alpaca_api_key,
                secret_key=settings.alpaca_secret_key,
                url_override=settings.alpaca_data_api_url,
            )
        return cls._stock_data_client

    @classmethod
    def get_options_data_client(cls) -> OptionHistoricalDataClient:
        """Get or create options historical data client."""
        if cls._options_data_client is None:
            logger.info("Initializing Alpaca options data client...")
            cls._options_data_client = OptionHistoricalDataClient(
                api_key=settings.alpaca_api_key, secret_key=settings.alpaca_secret_key
            )
        return cls._options_data_client

    @classmethod
    def get_stock_stream_client(cls) -> StockDataStream:
        """Get or create stock streaming data client."""
        if cls._stock_stream_client is None:
            logger.info("Initializing Alpaca stock stream client...")
            cls._stock_stream_client = StockDataStream(
                api_key=settings.alpaca_api_key,
                secret_key=settings.alpaca_secret_key,
                url_override=settings.alpaca_stream_data_wss,
            )
        return cls._stock_stream_client

    @classmethod
    def health_check(cls) -> dict:
        """Perform health check on all clients."""
        results = {}

        try:
            trading_client = cls.get_trading_client()
            account = trading_client.get_account()
            results["trading"] = {
                "status": "healthy",
                "account_id": str(account.id),
                "paper_mode": settings.alpaca_paper_trade,
            }
        except Exception as e:
            results["trading"] = {"status": "error", "error": str(e)}

        try:
            cls.get_stock_data_client()
            # Test with a simple request
            results["stock_data"] = {"status": "healthy"}
        except Exception as e:
            results["stock_data"] = {"status": "error", "error": str(e)}

        try:
            cls.get_options_data_client()
            results["options_data"] = {"status": "healthy"}
        except Exception as e:
            results["options_data"] = {"status": "error", "error": str(e)}

        return results

    @classmethod
    def close_all(cls):
        """Close all client connections."""
        logger.info("Closing all Alpaca client connections...")

        if cls._stock_stream_client:
            try:
                cls._stock_stream_client.close()
            except Exception as e:
                logger.warning(f"Error closing stream client: {e}")

        # Reset all clients
        cls._trading_client = None
        cls._stock_data_client = None
        cls._options_data_client = None
        cls._stock_stream_client = None

        logger.info("All Alpaca clients closed")
