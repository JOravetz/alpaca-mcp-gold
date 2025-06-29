# Anthropic MCP Server SDK Reference for AI Development

This document provides AI-optimized reference for the Anthropic MCP (Model Context Protocol) Server SDK used in our implementation.

## 📦 Core SDK Components

### Server Initialization
```python
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("Alpaca Trading Gold Standard")

# Run the server
if __name__ == "__main__":
    mcp.run()
```

### Tool Registration
```python
from typing import Dict, Any, Optional, List

@mcp.tool()
async def your_tool_name(
    required_param: str,
    optional_param: Optional[int] = None
) -> Dict[str, Any]:
    """
    Tool description that explains functionality to AI clients.
    
    Args:
        required_param: Description of required parameter
        optional_param: Description of optional parameter
    
    Returns:
        Dict containing operation results or error information
    """
    try:
        # Tool implementation
        result = perform_operation(required_param, optional_param)
        
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "operation": "your_tool_name",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Operation failed: {str(e)}",
            "error_type": type(e).__name__
        }
```

### Resource Registration
```python
@mcp.resource("scheme://path/to/resource")
async def get_resource_handler(path_param: str) -> Dict[str, Any]:
    """
    Resource handler for URI-based data access.
    
    Args:
        path_param: Dynamic path parameter from URI
    
    Returns:
        Dict containing resource data or error
    """
    try:
        data = fetch_resource_data(path_param)
        return {"resource_data": data}
    except Exception as e:
        return {"error": f"Failed to get resource: {str(e)}"}

# Register resource with URI pattern
@mcp.resource("trading://account/{resource}")
async def trading_account_resource(resource: str) -> Dict[str, Any]:
    """Handle trading account resources dynamically."""
    if resource == "info":
        return await get_account_info_resource()
    elif resource == "positions":
        return await get_positions_resource()
    else:
        return {"error": f"Unknown account resource: {resource}"}
```

### Prompt Registration
```python
@mcp.prompt()
async def contextual_guidance_prompt(
    context_param: str = "general"
) -> Dict[str, Any]:
    """
    Generate context-aware prompts for AI interactions.
    
    Args:
        context_param: Context to adapt prompt content
    
    Returns:
        MCP prompt specification dict
    """
    # Generate adaptive prompt content
    prompt_content = generate_prompt_content(context_param)
    
    return {
        "name": "contextual_guidance",
        "description": f"Contextual guidance for {context_param}",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_content
                }
            }
        ]
    }
```

## 🔧 Advanced Tool Patterns

### Tool with Complex Return Types
```python
from pydantic import BaseModel
from typing import Union

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_type: Optional[str] = None

@mcp.tool()
async def comprehensive_analysis_tool(
    entity_id: str,
    analysis_type: str = "full"
) -> Union[SuccessResponse, ErrorResponse]:
    """
    Comprehensive analysis with structured response types.
    
    Args:
        entity_id: ID of entity to analyze
        analysis_type: Type of analysis to perform
    
    Returns:
        Structured response with comprehensive data
    """
    try:
        # Validate inputs
        if not entity_id:
            return ErrorResponse(
                message="Entity ID cannot be empty",
                error_type="ValidationError"
            )
        
        # Perform analysis
        analysis_result = perform_comprehensive_analysis(entity_id, analysis_type)
        
        return SuccessResponse(
            data=analysis_result,
            metadata={
                "analysis_type": analysis_type,
                "entity_id": entity_id,
                "generated_at": datetime.now().isoformat()
            }
        )
        
    except ValueError as e:
        return ErrorResponse(
            message=f"Invalid input: {str(e)}",
            error_type="ValidationError"
        )
    except Exception as e:
        return ErrorResponse(
            message=f"Analysis failed: {str(e)}",
            error_type=type(e).__name__
        )
```

### Tool with File Operations
```python
from pathlib import Path

@mcp.tool()
async def export_data_tool(
    data_format: str,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Export data with automatic file management.
    
    Args:
        data_format: Format for export (json, csv, excel)
        output_path: Optional custom output path
    
    Returns:
        Export operation results
    """
    try:
        # Prepare output directory
        if output_path is None:
            output_dir = Path("outputs/exports")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{data_format}"
        
        # Export data
        exported_file = export_data(data_format, output_path)
        
        return {
            "status": "success",
            "data": {
                "exported_file": str(exported_file),
                "format": data_format,
                "size_bytes": exported_file.stat().st_size
            },
            "metadata": {
                "operation": "export_data",
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Export failed: {str(e)}",
            "error_type": type(e).__name__
        }
```

## 🌐 Resource Implementation Patterns

### Dynamic Resource Routing
```python
@mcp.resource("domain://{category}/{resource}")
async def dynamic_resource_handler(category: str, resource: str) -> Dict[str, Any]:
    """
    Dynamic resource routing based on URI pattern.
    
    Args:
        category: Resource category from URI
        resource: Specific resource from URI
    
    Returns:
        Resource data or error
    """
    try:
        # Route to appropriate handler
        if category == "account":
            return await handle_account_resource(resource)
        elif category == "portfolio":
            return await handle_portfolio_resource(resource)
        elif category == "market":
            return await handle_market_resource(resource)
        else:
            return {"error": f"Unknown category: {category}"}
            
    except Exception as e:
        return {"error": f"Resource error: {str(e)}"}

async def handle_account_resource(resource: str) -> Dict[str, Any]:
    """Handle account-specific resources."""
    handlers = {
        "info": get_account_info_data,
        "positions": get_positions_data,
        "orders": get_orders_data,
        "history": get_account_history_data
    }
    
    if resource in handlers:
        data = await handlers[resource]()
        return {"resource_data": data}
    else:
        return {"error": f"Unknown account resource: {resource}"}
```

### Resource with Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

class ResourceCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value):
        self.cache[key] = (value, datetime.now())

# Global cache instance
resource_cache = ResourceCache(ttl_seconds=300)

@mcp.resource("cached://market/{symbol}")
async def cached_market_resource(symbol: str) -> Dict[str, Any]:
    """
    Resource with intelligent caching for performance.
    
    Args:
        symbol: Stock symbol for market data
    
    Returns:
        Cached or fresh market data
    """
    try:
        cache_key = f"market_{symbol}"
        
        # Check cache first
        cached_data = resource_cache.get(cache_key)
        if cached_data:
            return {
                "resource_data": cached_data,
                "metadata": {"source": "cache"}
            }
        
        # Fetch fresh data
        market_data = await fetch_market_data(symbol)
        
        # Cache the result
        resource_cache.set(cache_key, market_data)
        
        return {
            "resource_data": market_data,
            "metadata": {"source": "api"}
        }
        
    except Exception as e:
        return {"error": f"Market data error: {str(e)}"}
```

## 💬 Prompt Engineering Patterns

### Context-Aware Prompts
```python
@mcp.prompt()
async def adaptive_guidance_prompt(
    domain_context: str = "general",
    user_level: str = "beginner"
) -> Dict[str, Any]:
    """
    Generate adaptive prompts based on context and user level.
    
    Args:
        domain_context: Domain-specific context
        user_level: User experience level
    
    Returns:
        Contextual prompt specification
    """
    # Get current system state for context
    system_state = await get_current_system_state()
    
    # Build adaptive content
    prompt_content = build_contextual_content(
        domain_context, 
        user_level, 
        system_state
    )
    
    return {
        "name": f"adaptive_guidance_{domain_context}",
        "description": f"Contextual guidance for {domain_context} ({user_level} level)",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_content
                }
            }
        ]
    }

def build_contextual_content(domain: str, level: str, state: Dict) -> str:
    """Build context-aware prompt content."""
    base_content = f"# {domain.title()} Guidance ({level.title()} Level)\n\n"
    
    # Add state-specific context
    if state.get("active_entities"):
        entity_count = len(state["active_entities"])
        base_content += f"I can see you have {entity_count} active entities loaded.\n\n"
        
        # Add specific recommendations
        for entity in state["active_entities"][:3]:
            base_content += f"• **{entity['name']}**: {entity['description']}\n"
    
    # Add level-appropriate guidance
    if level == "beginner":
        base_content += """
## Getting Started
1. Start with basic operations
2. Use suggested commands below
3. Ask for help when needed
"""
    elif level == "advanced":
        base_content += """
## Advanced Operations
1. Combine multiple tools for complex workflows
2. Use batch operations for efficiency
3. Implement custom automation
"""
    
    return base_content
```

### Business Domain Prompts
```python
@mcp.prompt()
async def business_strategy_prompt(
    strategy_focus: str = "general",
    time_horizon: str = "medium"
) -> Dict[str, Any]:
    """
    Business strategy prompts adapted to current context.
    
    Args:
        strategy_focus: Strategy focus area
        time_horizon: Time horizon for strategy
    
    Returns:
        Business-focused prompt specification
    """
    # Get domain-specific data
    current_metrics = await get_business_metrics()
    
    # Strategy-specific templates
    strategy_templates = {
        "growth": generate_growth_strategy_content,
        "efficiency": generate_efficiency_strategy_content,
        "risk_management": generate_risk_strategy_content,
        "innovation": generate_innovation_strategy_content
    }
    
    # Generate content
    if strategy_focus in strategy_templates:
        content_generator = strategy_templates[strategy_focus]
        prompt_content = content_generator(current_metrics, time_horizon)
    else:
        prompt_content = generate_general_strategy_content(current_metrics, time_horizon)
    
    return {
        "name": f"business_strategy_{strategy_focus}",
        "description": f"Business strategy guidance for {strategy_focus}",
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt_content
                }
            }
        ]
    }
```

## 🧪 Testing Patterns

### Tool Testing
```python
import pytest
from unittest.mock import AsyncMock, patch

class TestYourTool:
    @pytest.mark.asyncio
    async def test_tool_success_case(self):
        """Test successful tool execution."""
        # Setup
        test_param = "valid_input"
        expected_result = {"key": "value"}
        
        # Mock dependencies
        with patch('your_module.perform_operation') as mock_operation:
            mock_operation.return_value = expected_result
            
            # Execute
            result = await your_tool_name(test_param)
            
            # Verify
            assert result["status"] == "success"
            assert result["data"] == expected_result
            assert "metadata" in result
            mock_operation.assert_called_once_with(test_param, None)
    
    @pytest.mark.asyncio
    async def test_tool_error_handling(self):
        """Test tool error handling."""
        # Setup
        test_param = "invalid_input"
        
        # Mock dependencies to raise exception
        with patch('your_module.perform_operation') as mock_operation:
            mock_operation.side_effect = ValueError("Invalid input")
            
            # Execute
            result = await your_tool_name(test_param)
            
            # Verify
            assert result["status"] == "error"
            assert "Invalid input" in result["message"]
            assert result["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    async def test_tool_validation(self):
        """Test input validation."""
        # Test empty input
        result = await your_tool_name("")
        assert result["status"] == "error"
        assert "cannot be empty" in result["message"]
```

### Resource Testing
```python
class TestYourResource:
    @pytest.mark.asyncio
    async def test_resource_success(self):
        """Test successful resource access."""
        # Setup
        resource_param = "test_resource"
        expected_data = {"resource": "data"}
        
        # Mock data source
        with patch('your_module.fetch_resource_data') as mock_fetch:
            mock_fetch.return_value = expected_data
            
            # Execute
            result = await get_resource_handler(resource_param)
            
            # Verify
            assert "resource_data" in result
            assert result["resource_data"] == expected_data
    
    @pytest.mark.asyncio
    async def test_resource_error(self):
        """Test resource error handling."""
        # Setup
        resource_param = "invalid_resource"
        
        # Mock data source to raise exception
        with patch('your_module.fetch_resource_data') as mock_fetch:
            mock_fetch.side_effect = Exception("Resource not found")
            
            # Execute
            result = await get_resource_handler(resource_param)
            
            # Verify
            assert "error" in result
            assert "Resource not found" in result["error"]
```

### Integration Testing
```python
class TestMCPIntegration:
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Setup and teardown for integration tests."""
        # Setup
        await initialize_test_environment()
        yield
        # Teardown
        await cleanup_test_environment()
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete workflow from tool to resource."""
        # Step 1: Load data via tool
        load_result = await data_loading_tool("test_data")
        assert load_result["status"] == "success"
        
        # Step 2: Access via resource
        resource_result = await get_data_resource("test_data")
        assert "resource_data" in resource_result
        
        # Step 3: Verify consistency
        assert load_result["data"]["id"] == resource_result["resource_data"]["id"]
    
    @pytest.mark.asyncio
    async def test_resource_mirror_consistency(self):
        """Test resource and mirror tool consistency."""
        # Access via resource
        resource_result = await get_resource_handler("test")
        
        # Access via mirror tool
        tool_result = await resource_mirror_tool("test")
        
        # Verify identical data
        if "resource_data" in resource_result and tool_result["status"] == "success":
            assert resource_result["resource_data"] == tool_result["data"]
```

## 🚀 Production Patterns

### Logging Configuration
```python
import logging
from datetime import datetime

def setup_mcp_logging(log_level: str = "INFO"):
    """Configure logging for MCP server."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'mcp_server_{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )
    
    # Set specific logger levels
    logging.getLogger('mcp.server').setLevel(logging.INFO)
    logging.getLogger('your_domain').setLevel(logging.DEBUG)

# Use in tools
logger = logging.getLogger(__name__)

@mcp.tool()
async def logged_operation_tool(param: str) -> Dict[str, Any]:
    """Tool with comprehensive logging."""
    logger.info(f"Starting operation with param: {param}")
    
    try:
        result = await perform_operation(param)
        logger.info(f"Operation completed successfully: {result}")
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
```

### Environment Configuration
```python
import os
from typing import Optional

class MCPConfig:
    """MCP server configuration management."""
    
    def __init__(self):
        self.server_name = os.getenv('MCP_SERVER_NAME', 'default-server')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Domain-specific config
        self.api_key = os.getenv('API_KEY')
        self.api_secret = os.getenv('API_SECRET')
        
        # Validate required config
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration."""
        if not self.api_key:
            raise ValueError("API_KEY environment variable is required")
        if not self.api_secret:
            raise ValueError("API_SECRET environment variable is required")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return os.getenv('ENVIRONMENT', 'development').lower() == 'production'

# Global config instance
config = MCPConfig()
```

### Error Handling Middleware
```python
from functools import wraps
from typing import Callable, Any

def mcp_error_handler(tool_func: Callable) -> Callable:
    """Decorator for consistent error handling across tools."""
    @wraps(tool_func)
    async def wrapper(*args, **kwargs) -> Dict[str, Any]:
        try:
            result = await tool_func(*args, **kwargs)
            
            # Ensure consistent response format
            if not isinstance(result, dict):
                result = {"status": "success", "data": result}
            
            # Add metadata if missing
            if "metadata" not in result:
                result["metadata"] = {
                    "operation": tool_func.__name__,
                    "timestamp": datetime.now().isoformat()
                }
            
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error in {tool_func.__name__}: {e}")
            return {
                "status": "error",
                "message": f"Invalid input: {str(e)}",
                "error_type": "ValidationError"
            }
        except Exception as e:
            logger.error(f"Unexpected error in {tool_func.__name__}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Operation failed: {str(e)}",
                "error_type": type(e).__name__
            }
    
    return wrapper

# Usage
@mcp.tool()
@mcp_error_handler
async def protected_tool(param: str) -> Dict[str, Any]:
    """Tool with automatic error handling."""
    # Tool implementation without explicit error handling
    return perform_operation(param)
```

## 📝 Best Practices

### 1. Tool Design
- Use clear, descriptive function names
- Include comprehensive docstrings
- Implement consistent error handling
- Return structured response formats
- Validate all inputs thoroughly

### 2. Resource Architecture
- Design intuitive URI schemes
- Implement proper caching strategies
- Handle dynamic routing efficiently
- Provide clear error messages
- Support both individual and batch operations

### 3. Prompt Engineering
- Make prompts context-aware
- Reference actual system state
- Provide actionable guidance
- Adapt to user experience level
- Include specific command examples

### 4. Testing Strategy
- Test both success and error cases
- Verify resource-tool consistency
- Implement integration testing
- Use proper test fixtures
- Mock external dependencies

### 5. Production Deployment
- Configure comprehensive logging
- Implement proper error monitoring
- Use environment-based configuration
- Handle resource cleanup properly
- Monitor performance metrics

This reference provides the essential MCP Server SDK patterns used throughout our implementation. For complete SDK documentation, refer to the official Anthropic MCP documentation.