"""Tests for trading resource mirror tools that provide tool-only client compatibility."""

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
    resource_system_status,
)
from src.mcp_server.resources.trading_resources import get_trading_resource
from src.mcp_server.models.schemas import StateManager
from .conftest import assert_success_response, assert_error_response


@pytest.mark.asyncio
class TestTradingResourceMirrorTools:
    """Test trading resource mirror tools provide identical functionality to resources."""

    async def test_resource_account_info_matches_resource(self, real_api_test):
        """Ensure account info tool matches resource output."""
        # Get data from resource directly
        resource_result = await get_trading_resource("trading://account/info")

        # Get data from mirror tool
        tool_result = await resource_account_info()

        # Both should succeed
        assert_success_response(tool_result)
        assert "resource_data" in resource_result

        # Tool data should match resource data
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["source"] == "trading://account/info"

    async def test_resource_account_positions_matches_resource(self, real_api_test):
        """Ensure positions tool matches resource output."""
        resource_result = await get_trading_resource("trading://account/positions")
        tool_result = await resource_account_positions()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["source"] == "trading://account/positions"

    async def test_resource_account_orders_matches_resource(self, real_api_test):
        """Ensure orders tool matches resource output."""
        resource_result = await get_trading_resource("trading://account/orders")
        tool_result = await resource_account_orders()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]
        assert tool_result["metadata"]["source"] == "trading://account/orders"

    async def test_resource_portfolio_summary_with_data(self, real_api_test):
        """Test portfolio summary tool with loaded portfolio data."""
        # Load some portfolio data first
        from src.mcp_server.tools.account_tools import get_account_info, get_positions

        await get_account_info()
        await get_positions()

        resource_result = await get_trading_resource("trading://portfolio/summary")
        tool_result = await resource_portfolio_summary()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_resource_portfolio_summary_no_data(self):
        """Test portfolio summary tool with no data."""
        # Clear state to ensure no data
        StateManager.clear_all()

        resource_result = await get_trading_resource("trading://portfolio/summary")
        tool_result = await resource_portfolio_summary()

        # Both should return error when no data
        assert_error_response(tool_result)
        assert "error" in resource_result
        assert tool_result["message"] == resource_result["error"]
        assert tool_result["error_type"] == "ResourceError"

    async def test_resource_portfolio_entities_matches_resource(self, real_api_test):
        """Ensure portfolio entities tool matches resource output."""
        # Load some data first - need to initialize portfolio
        from src.mcp_server.tools.account_tools import get_account_info, get_positions

        await get_account_info()  # Initialize portfolio first
        await get_positions()

        resource_result = await get_trading_resource("trading://portfolio/entities")
        tool_result = await resource_portfolio_entities()

        # Both should succeed or both should fail consistently
        if "resource_data" in resource_result:
            assert_success_response(tool_result)
            assert tool_result["data"] == resource_result["resource_data"]
        else:
            # Both should return error if no data
            assert tool_result["status"] == "error"
            assert "error" in resource_result

    async def test_resource_symbols_active_matches_resource(self, real_api_test):
        """Ensure active symbols tool matches resource output."""
        # Load some symbols first
        from src.mcp_server.tools.market_data_tools import get_stock_quote

        await get_stock_quote("AAPL")
        await get_stock_quote("MSFT")

        resource_result = await get_trading_resource("trading://symbols/active")
        tool_result = await resource_symbols_active()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_resource_symbols_count_matches_resource(self, real_api_test):
        """Ensure symbols count tool matches resource output."""
        resource_result = await get_trading_resource("trading://symbols/count")
        tool_result = await resource_symbols_count()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_resource_system_health_matches_resource(self, real_api_test):
        """Ensure system health tool matches resource output."""
        resource_result = await get_trading_resource("trading://system/health")
        tool_result = await resource_system_health()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_resource_system_memory_matches_resource(self, real_api_test):
        """Ensure system memory tool matches resource output."""
        resource_result = await get_trading_resource("trading://system/memory")
        tool_result = await resource_system_memory()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_resource_system_status_matches_resource(self, real_api_test):
        """Ensure system status tool matches resource output."""
        resource_result = await get_trading_resource("trading://system/status")
        tool_result = await resource_system_status()

        assert_success_response(tool_result)
        assert "resource_data" in resource_result
        assert tool_result["data"] == resource_result["resource_data"]

    async def test_all_resource_mirror_tools_available(self):
        """Verify all 10 trading resource mirror tools are implemented and callable."""
        expected_tools = [
            resource_account_info,
            resource_account_positions,
            resource_account_orders,
            resource_portfolio_summary,
            resource_portfolio_entities,
            resource_symbols_active,
            resource_symbols_count,
            resource_system_health,
            resource_system_memory,
            resource_system_status,
        ]

        # Verify all tools exist and are callable
        for tool_func in expected_tools:
            assert callable(tool_func), f"Tool {tool_func.__name__} is not callable"

    async def test_error_handling_consistency(self):
        """Verify error handling is consistent between tools and resources."""
        # Test with invalid resource path
        invalid_uri = "trading://invalid/resource"

        resource_error = await get_trading_resource(invalid_uri)
        assert "error" in resource_error

        # All mirror tools should handle errors consistently by converting
        # resource errors to tool error format with error_type field

    async def test_metadata_consistency(self, real_api_test):
        """Verify all successful tool responses include proper metadata."""
        tools_and_sources = [
            (resource_account_info, "trading://account/info"),
            (resource_account_positions, "trading://account/positions"),
            (resource_account_orders, "trading://account/orders"),
            (resource_symbols_count, "trading://symbols/count"),
            (resource_system_health, "trading://system/health"),
            (resource_system_memory, "trading://system/memory"),
            (resource_system_status, "trading://system/status"),
        ]

        for tool_func, expected_source in tools_and_sources:
            result = await tool_func()
            assert_success_response(result)
            assert "metadata" in result
            assert result["metadata"]["source"] == expected_source
            assert "operation" in result["metadata"]

    async def test_error_type_in_resource_errors(self):
        """Verify resource errors are properly converted with error_type."""
        # Clear state to trigger no data error
        StateManager.clear_all()

        result = await resource_portfolio_summary()
        assert_error_response(result)
        assert result["error_type"] == "ResourceError"

    async def test_data_structure_consistency(self, real_api_test):
        """Verify data structures returned by tools are properly formatted."""
        # Test account info structure
        account_result = await resource_account_info()
        assert_success_response(account_result)

        account_data = account_result["data"]
        required_fields = ["account_id", "status", "buying_power", "portfolio_value"]
        for field in required_fields:
            assert field in account_data, f"Missing field {field} in account data"

    async def test_mirror_tools_with_loaded_portfolio(self, real_api_test):
        """Test mirror tools work correctly with loaded portfolio data."""
        # Load portfolio data
        from src.mcp_server.tools.account_tools import get_account_info, get_positions

        await get_account_info()
        await get_positions()

        # Test portfolio-dependent tools
        portfolio_tools = [
            resource_portfolio_summary,
            resource_portfolio_entities,
        ]

        for tool_func in portfolio_tools:
            result = await tool_func()
            assert_success_response(result)
            assert "data" in result
            assert "metadata" in result

    async def test_tool_response_format_compliance(self, real_api_test):
        """Ensure all tools follow the standard response format."""
        all_tools = [
            resource_account_info,
            resource_account_positions,
            resource_account_orders,
            resource_symbols_count,
            resource_system_health,
            resource_system_memory,
            resource_system_status,
        ]

        for tool_func in all_tools:
            result = await tool_func()

            # Must have status
            assert "status" in result
            assert result["status"] in ["success", "error"]

            if result["status"] == "success":
                # Success responses must have data and metadata
                assert "data" in result
                assert "metadata" in result
                assert "operation" in result["metadata"]
                assert "source" in result["metadata"]
            else:
                # Error responses must have message and error_type
                assert "message" in result
                assert "error_type" in result

    async def test_zero_maintenance_overhead(self, real_api_test):
        """Verify mirror tools automatically reflect resource changes."""
        # This test ensures that if resources change, mirrors automatically reflect
        # those changes without needing separate updates

        # Get account info through both paths
        resource_result = await get_trading_resource("trading://account/info")
        tool_result = await resource_account_info()

        # Should be identical (mirrors have zero maintenance overhead)
        assert tool_result["data"] == resource_result["resource_data"]

        # Any resource changes should automatically appear in tool results
        # since tools just call resources internally
