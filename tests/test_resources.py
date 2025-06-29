"""
Tests for resources following gold standard patterns.
"""

import pytest
from src.mcp_server.resources.trading_resources import get_trading_resource
from src.mcp_server.models.schemas import StateManager, TradingPortfolioSchema
from .conftest import assert_resource_response

class TestTradingResources:
    """Test suite for trading resources."""
    
    @pytest.mark.asyncio
    async def test_account_info_resource(self, mock_alpaca_clients):
        """Test trading://account/info resource."""
        result = await get_trading_resource("trading://account/info")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert data["account_id"] == "test_account_123"
        assert data["buying_power"] == 10000.0
        assert data["portfolio_value"] == 15000.0
    
    @pytest.mark.asyncio
    async def test_account_positions_resource(self, mock_alpaca_clients):
        """Test trading://account/positions resource."""
        result = await get_trading_resource("trading://account/positions")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert len(data) == 1
        assert data[0]["symbol"] == "AAPL"
        assert data[0]["quantity"] == 100.0
    
    @pytest.mark.asyncio
    async def test_account_orders_resource(self, mock_alpaca_clients):
        """Test trading://account/orders resource."""
        result = await get_trading_resource("trading://account/orders")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert len(data) == 1
        assert data[0]["order_id"] == "order_123"
        assert data[0]["symbol"] == "AAPL"
    
    @pytest.mark.asyncio
    async def test_portfolio_summary_resource_no_data(self):
        """Test trading://portfolio/summary resource with no data."""
        result = await get_trading_resource("trading://portfolio/summary")
        
        assert_resource_response(result)
        assert "error" in result
        assert "No portfolio data available" in result["error"]
    
    @pytest.mark.asyncio
    async def test_portfolio_summary_resource_with_data(self, sample_portfolio_data):
        """Test trading://portfolio/summary resource with data."""
        # Create and store portfolio
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        result = await get_trading_resource("trading://portfolio/summary")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert "portfolio_metrics" in data
        assert "entity_count" in data
        assert "suggested_operations" in data
    
    @pytest.mark.asyncio
    async def test_portfolio_entities_resource(self, sample_portfolio_data):
        """Test trading://portfolio/entities resource."""
        # Create portfolio with entities
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        result = await get_trading_resource("trading://portfolio/entities")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        # Should be empty initially
        data = result["resource_data"]
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_symbols_active_resource(self):
        """Test trading://symbols/active resource."""
        result = await get_trading_resource("trading://symbols/active")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        # Should be empty initially
        data = result["resource_data"]
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_symbols_count_resource(self):
        """Test trading://symbols/count resource."""
        result = await get_trading_resource("trading://symbols/count")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert "total_symbols" in data
        assert data["total_symbols"] == 0  # Initially empty
    
    @pytest.mark.asyncio
    async def test_system_health_resource(self, mock_alpaca_clients):
        """Test trading://system/health resource."""
        result = await get_trading_resource("trading://system/health")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert "trading" in data
        assert "stock_data" in data
        assert "options_data" in data
    
    @pytest.mark.asyncio
    async def test_system_memory_resource(self):
        """Test trading://system/memory resource."""
        result = await get_trading_resource("trading://system/memory")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert "portfolios_count" in data
        assert "symbols_count" in data
        assert "total_entities" in data
    
    @pytest.mark.asyncio
    async def test_system_status_resource(self, mock_alpaca_clients):
        """Test trading://system/status resource."""
        result = await get_trading_resource("trading://system/status")
        
        assert_resource_response(result)
        assert "resource_data" in result
        
        data = result["resource_data"]
        assert "server_name" in data
        assert "paper_trading" in data
        assert "log_level" in data
        assert "memory_usage" in data
        assert "client_health" in data
    
    @pytest.mark.asyncio
    async def test_invalid_scheme(self):
        """Test resource with invalid scheme."""
        result = await get_trading_resource("invalid://test")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unsupported scheme" in result["error"]
    
    @pytest.mark.asyncio
    async def test_invalid_path(self):
        """Test resource with invalid path."""
        result = await get_trading_resource("trading://")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Invalid URI path" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_category(self):
        """Test resource with unknown category."""
        result = await get_trading_resource("trading://unknown/resource")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unknown resource category" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_account_resource(self):
        """Test unknown account resource."""
        result = await get_trading_resource("trading://account/unknown")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unknown account resource" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_portfolio_resource(self):
        """Test unknown portfolio resource."""
        result = await get_trading_resource("trading://portfolio/unknown")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unknown portfolio resource" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_symbols_resource(self):
        """Test unknown symbols resource."""
        result = await get_trading_resource("trading://symbols/unknown")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unknown symbols resource" in result["error"]
    
    @pytest.mark.asyncio
    async def test_unknown_system_resource(self):
        """Test unknown system resource."""
        result = await get_trading_resource("trading://system/unknown")
        
        assert_resource_response(result)
        assert "error" in result
        assert "Unknown system resource" in result["error"]