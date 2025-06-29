"""
Resource mirror tools following gold standard patterns.
Provides tool access to resources for tool-only clients.
"""

import logging
from typing import Dict, Any
from ..resources.trading_resources import get_trading_resource

logger = logging.getLogger(__name__)

# Account Resource Mirrors

async def resource_account_info() -> Dict[str, Any]:
    """
    Tool mirror of trading://account/info resource.
    Retrieves account information via tool interface for compatibility.
    
    Returns:
        Dict with status and account data or error message
    """
    try:
        result = await get_trading_resource("trading://account/info")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_account_info",
                "source": "trading://account/info"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for account info: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve account info: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_account_positions() -> Dict[str, Any]:
    """
    Tool mirror of trading://account/positions resource.
    Retrieves all positions via tool interface for compatibility.
    
    Returns:
        Dict with status and positions data or error message
    """
    try:
        result = await get_trading_resource("trading://account/positions")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_account_positions",
                "source": "trading://account/positions",
                "total_positions": len(result["resource_data"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for account positions: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve positions: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_account_orders() -> Dict[str, Any]:
    """
    Tool mirror of trading://account/orders resource.
    Retrieves recent orders via tool interface for compatibility.
    
    Returns:
        Dict with status and orders data or error message
    """
    try:
        result = await get_trading_resource("trading://account/orders")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_account_orders",
                "source": "trading://account/orders",
                "total_orders": len(result["resource_data"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for account orders: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve orders: {str(e)}",
            "error_type": type(e).__name__
        }

# Portfolio Resource Mirrors

async def resource_portfolio_summary() -> Dict[str, Any]:
    """
    Tool mirror of trading://portfolio/summary resource.
    Retrieves portfolio summary via tool interface for compatibility.
    
    Returns:
        Dict with status and portfolio summary or error message
    """
    try:
        result = await get_trading_resource("trading://portfolio/summary")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_portfolio_summary",
                "source": "trading://portfolio/summary"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for portfolio summary: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve portfolio summary: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_portfolio_entities() -> Dict[str, Any]:
    """
    Tool mirror of trading://portfolio/entities resource.
    Retrieves portfolio entities via tool interface for compatibility.
    
    Returns:
        Dict with status and entities data or error message
    """
    try:
        result = await get_trading_resource("trading://portfolio/entities")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_portfolio_entities",
                "source": "trading://portfolio/entities",
                "total_entities": len(result["resource_data"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for portfolio entities: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve portfolio entities: {str(e)}",
            "error_type": type(e).__name__
        }

# Symbols Resource Mirrors

async def resource_symbols_active() -> Dict[str, Any]:
    """
    Tool mirror of trading://symbols/active resource.
    Retrieves active symbols via tool interface for compatibility.
    
    Returns:
        Dict with status and symbols data or error message
    """
    try:
        result = await get_trading_resource("trading://symbols/active")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_symbols_active",
                "source": "trading://symbols/active",
                "total_symbols": len(result["resource_data"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for active symbols: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve active symbols: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_symbols_count() -> Dict[str, Any]:
    """
    Tool mirror of trading://symbols/count resource.
    Retrieves symbol count via tool interface for compatibility.
    
    Returns:
        Dict with status and count data or error message
    """
    try:
        result = await get_trading_resource("trading://symbols/count")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_symbols_count",
                "source": "trading://symbols/count"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for symbols count: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve symbols count: {str(e)}",
            "error_type": type(e).__name__
        }

# System Resource Mirrors

async def resource_system_health() -> Dict[str, Any]:
    """
    Tool mirror of trading://system/health resource.
    Retrieves system health via tool interface for compatibility.
    
    Returns:
        Dict with status and health data or error message
    """
    try:
        result = await get_trading_resource("trading://system/health")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_system_health",
                "source": "trading://system/health"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for system health: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve system health: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_system_memory() -> Dict[str, Any]:
    """
    Tool mirror of trading://system/memory resource.
    Retrieves memory usage via tool interface for compatibility.
    
    Returns:
        Dict with status and memory data or error message
    """
    try:
        result = await get_trading_resource("trading://system/memory")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_system_memory",
                "source": "trading://system/memory"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for system memory: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve memory usage: {str(e)}",
            "error_type": type(e).__name__
        }

async def resource_system_status() -> Dict[str, Any]:
    """
    Tool mirror of trading://system/status resource.
    Retrieves system status via tool interface for compatibility.
    
    Returns:
        Dict with status and system status data or error message
    """
    try:
        result = await get_trading_resource("trading://system/status")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"],
                "error_type": "ResourceError"
            }
        
        return {
            "status": "success",
            "data": result["resource_data"],
            "metadata": {
                "operation": "resource_system_status",
                "source": "trading://system/status"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in resource mirror for system status: {e}")
        return {
            "status": "error",
            "message": f"Failed to retrieve system status: {str(e)}",
            "error_type": type(e).__name__
        }