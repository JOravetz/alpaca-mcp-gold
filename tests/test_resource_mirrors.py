"""
Tests for resource mirror tools following gold standard patterns.
"""

import pytest
from src.mcp_server.tools.resource_mirror_tools import (
    resource_account_info,
    resource_account_positions,
    resource_account_orders,
    resource_portfolio_summary,
    resource_portfolio_entities,
    resource_symbols_active,
    resource_symbols_count,
    resource_system_health,
    resource_system_memory,
    resource_system_status
)
from src.mcp_server.resources.trading_resources import get_trading_resource
from src.mcp_server.models.schemas import StateManager, TradingPortfolioSchema
from .conftest import assert_success_response, assert_error_response

class TestResourceMirrors:
    """Test suite for resource mirror tools."""
    
    @pytest.mark.asyncio
    async def test_resource_account_info_mirror(self, mock_alpaca_clients):
        """Test that resource mirror returns same data as resource."""
        # Get data from resource
        resource_result = await get_trading_resource("trading://account/info")
        
        # Get data from mirror tool
        tool_result = await resource_account_info()
        
        # Compare results
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["source"] == "trading://account/info"
    
    @pytest.mark.asyncio
    async def test_resource_account_positions_mirror(self, mock_alpaca_clients):
        """Test positions resource mirror consistency."""
        resource_result = await get_trading_resource("trading://account/positions")
        tool_result = await resource_account_positions()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["total_positions"] == len(resource_result["resource_data"])
    
    @pytest.mark.asyncio
    async def test_resource_account_orders_mirror(self, mock_alpaca_clients):
        """Test orders resource mirror consistency."""
        resource_result = await get_trading_resource("trading://account/orders")
        tool_result = await resource_account_orders()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["total_orders"] == len(resource_result["resource_data"])
    
    @pytest.mark.asyncio
    async def test_resource_portfolio_summary_mirror_no_data(self):
        """Test portfolio summary mirror with no data."""
        resource_result = await get_trading_resource("trading://portfolio/summary")
        tool_result = await resource_portfolio_summary()
        
        # Both should return error when no data
        assert_error_response(tool_result)
        assert resource_result["error"] in tool_result["message"]
    
    @pytest.mark.asyncio
    async def test_resource_portfolio_summary_mirror_with_data(self, sample_portfolio_data):
        """Test portfolio summary mirror with data."""
        # Setup portfolio data
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        resource_result = await get_trading_resource("trading://portfolio/summary")
        tool_result = await resource_portfolio_summary()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
    
    @pytest.mark.asyncio
    async def test_resource_portfolio_entities_mirror(self, sample_portfolio_data):
        """Test portfolio entities mirror consistency."""
        portfolio = TradingPortfolioSchema.from_account_data(sample_portfolio_data)
        StateManager.set_portfolio(portfolio)
        
        resource_result = await get_trading_resource("trading://portfolio/entities")
        tool_result = await resource_portfolio_entities()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["total_entities"] == len(resource_result["resource_data"])
    
    @pytest.mark.asyncio
    async def test_resource_symbols_active_mirror(self):
        """Test active symbols mirror consistency."""
        resource_result = await get_trading_resource("trading://symbols/active")
        tool_result = await resource_symbols_active()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["total_symbols"] == len(resource_result["resource_data"])
    
    @pytest.mark.asyncio
    async def test_resource_symbols_count_mirror(self):
        """Test symbols count mirror consistency."""
        resource_result = await get_trading_resource("trading://symbols/count")
        tool_result = await resource_symbols_count()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
    
    @pytest.mark.asyncio
    async def test_resource_system_health_mirror(self, mock_alpaca_clients):
        """Test system health mirror consistency."""
        resource_result = await get_trading_resource("trading://system/health")
        tool_result = await resource_system_health()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
    
    @pytest.mark.asyncio
    async def test_resource_system_memory_mirror(self):
        """Test system memory mirror consistency."""
        resource_result = await get_trading_resource("trading://system/memory")
        tool_result = await resource_system_memory()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
    
    @pytest.mark.asyncio
    async def test_resource_system_status_mirror(self, mock_alpaca_clients):
        """Test system status mirror consistency."""
        resource_result = await get_trading_resource("trading://system/status")
        tool_result = await resource_system_status()
        
        assert_success_response(tool_result)
        assert tool_result["data"] == resource_result["resource_data"]
    
    @pytest.mark.asyncio
    async def test_error_propagation_in_mirrors(self, mock_alpaca_clients):
        """Test that errors are properly propagated through mirrors."""
        # Make the trading client fail
        mock_alpaca_clients["trading"].get_account.side_effect = Exception("API Error")
        
        # Resource should return error
        resource_result = await get_trading_resource("trading://account/info")
        assert "error" in resource_result
        
        # Mirror should convert error to tool format
        tool_result = await resource_account_info()
        assert_error_response(tool_result)
        assert "API Error" in tool_result["message"]
    
    @pytest.mark.asyncio
    async def test_mirror_metadata_consistency(self, mock_alpaca_clients):
        """Test that mirror tools include proper metadata."""
        tool_result = await resource_account_info()
        
        assert_success_response(tool_result)
        metadata = tool_result["metadata"]
        
        # Verify required metadata fields
        assert "operation" in metadata
        assert "source" in metadata
        assert metadata["operation"] == "resource_account_info"
        assert metadata["source"] == "trading://account/info"
    
    @pytest.mark.asyncio
    async def test_no_maintenance_overhead(self, mock_alpaca_clients):
        """Test that mirrors have no maintenance overhead (use same underlying functions)."""
        # This test verifies the architectural principle that mirrors 
        # should have zero maintenance overhead by calling the same functions
        
        # Call the resource directly
        resource_result = await get_trading_resource("trading://account/info")
        
        # Call through mirror
        tool_result = await resource_account_info()
        
        # Data should be identical (mirror just wraps the resource)
        assert tool_result["data"] == resource_result["resource_data"]
        
        # This proves the mirror pattern works without code duplication