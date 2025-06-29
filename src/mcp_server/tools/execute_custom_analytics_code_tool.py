"""
Custom Analytics Code Execution Tool
Implements universal dataset agnosticism patterns for any structured data analysis.
"""

import asyncio
import json
import logging
import textwrap
from typing import Dict, Any
from ..models.schemas import StateManager

logger = logging.getLogger(__name__)

async def execute_custom_analytics_code(
    dataset_name: str, 
    python_code: str,
    include_portfolio_context: bool = False
) -> str:
    """
    Execute custom Python analytics code against any loaded dataset with trading context.
    
    IMPORTANT FOR AI AGENTS:
    - Dataset will be available as 'df' pandas DataFrame in your code
    - Portfolio data available as 'portfolio' dict if include_portfolio_context=True
    - Libraries pre-imported: pandas as pd, numpy as np, plotly.express as px
    - To see results, you MUST print() them - only stdout output is returned
    - Any errors will be captured and returned so you can fix your code
    - Code runs in isolated subprocess with 30 second timeout
    
    USAGE EXAMPLES:
    
    Basic data exploration:
    ```python
    print("Dataset Info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\\nFirst 5 rows:")
    print(df.head())
    
    print(f"\\nData types:")
    print(df.dtypes)
    
    print(f"\\nBasic statistics:")
    print(df.describe())
    ```
    
    Advanced analytics:
    ```python
    # Custom correlation analysis
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    if len(numerical_cols) >= 2:
        corr_matrix = df[numerical_cols].corr()
        print("Correlation Matrix:")
        print(corr_matrix)
        
        # Find strongest correlations
        for i in range(len(numerical_cols)):
            for j in range(i+1, len(numerical_cols)):
                corr = corr_matrix.iloc[i, j]
                if abs(corr) > 0.5:
                    print(f"{numerical_cols[i]} <-> {numerical_cols[j]}: {corr:.3f}")
    ```
    
    Visualization:
    ```python
    # Create interactive charts
    if 'value_column' in df.columns and 'category_column' in df.columns:
        fig = px.bar(df, x='category_column', y='value_column', 
                     title='Values by Category')
        print("Chart created successfully")
        print(f"Data points: {len(df)}")
    ```
    
    Trading context integration:
    ```python
    # When include_portfolio_context=True
    if 'portfolio' in locals():
        print("Portfolio Integration:")
        print(f"Account Value: ${portfolio.get('account', {}).get('portfolio_value', 0):,.2f}")
        
        # Cross-reference with position data
        if 'symbol' in df.columns:
            portfolio_symbols = [pos['symbol'] for pos in portfolio.get('positions', [])]
            df['in_portfolio'] = df['symbol'].isin(portfolio_symbols)
            print(f"Symbols in portfolio: {df['in_portfolio'].sum()}")
    ```
    
    Args:
        dataset_name: Name of loaded dataset (use generic data loading patterns)
        python_code: Python code to execute (must print() results to see output)
        include_portfolio_context: Include current portfolio data for trading analysis
        
    Returns:
        str: Combined stdout and stderr output from code execution
    """
    try:
        # Step 1: Get dataset from state management
        # This demonstrates dataset agnosticism - works with ANY structured data
        tracked_symbols = StateManager.get_all_symbols()
        
        # For demo purposes, create a sample dataset if none provided
        # In real implementation, this would use DatasetManager.get_dataset(dataset_name)
        if dataset_name == "sample_market_data":
            # Create sample dataset from tracked symbols
            import pandas as pd
            sample_data = []
            for symbol, entity in tracked_symbols.items():
                sample_data.append({
                    'symbol': symbol,
                    'suggested_role': entity.suggested_role.value,
                    'characteristics': str(entity.characteristics),
                    'tracked_since': entity.first_seen.isoformat() if hasattr(entity, 'first_seen') else None
                })
            df_dict = pd.DataFrame(sample_data).to_dict('records')
        else:
            # This would normally be: df = DatasetManager.get_dataset(dataset_name)
            return f"ERROR: Dataset '{dataset_name}' not implemented. Use 'sample_market_data' for demo."
        
        # Step 2: Gather portfolio context if requested
        portfolio_context = {}
        if include_portfolio_context:
            try:
                from .account_tools import get_account_info, get_positions
                account_result = await get_account_info()
                if account_result["status"] == "success":
                    portfolio_context["account"] = account_result["data"]
                
                positions_result = await get_positions()
                if positions_result["status"] == "success":
                    portfolio_context["positions"] = positions_result["data"]
                else:
                    portfolio_context["positions"] = []
            except Exception as e:
                logger.warning(f"Could not gather portfolio context: {e}")
                portfolio_context = {"account": {}, "positions": []}
        
        # Step 3: Create execution template with dataset agnosticism
        dataset_json = json.dumps(df_dict, default=str)
        portfolio_json = json.dumps(portfolio_context, default=str)
        indented_user_code = textwrap.indent(python_code, '    ')
        
        execution_template = f'''
import pandas as pd
import numpy as np
import json
from datetime import datetime
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Note: Plotly not available for visualizations")

try:
    # Load dataset with universal agnosticism
    dataset_data = {dataset_json}
    df = pd.DataFrame(dataset_data)
    
    print("=== Dataset Analytics Execution Context ===")
    print(f"Dataset: {dataset_name}")
    print(f"Shape: {{df.shape[0]}} rows × {{df.shape[1]}} columns")
    print(f"Columns: {{list(df.columns)}}")
    
    # Load portfolio context if available
    portfolio_data = {portfolio_json}
    if portfolio_data and portfolio_data.get('account'):
        portfolio = portfolio_data
        print(f"Portfolio context loaded: ${{portfolio['account'].get('portfolio_value', 0):,.2f}} account value")
    
    print("=" * 45)
    print()
    
    # Execute user analytics code
{indented_user_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
'''
        
        # Step 4: Execute in subprocess with analytics libraries
        return await _execute_analytics_subprocess(execution_template)
        
    except Exception as e:
        logger.error(f"Error in custom analytics execution: {e}")
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"

async def _execute_analytics_subprocess(execution_code: str) -> str:
    """Execute analytics code in isolated subprocess with data science libraries."""
    try:
        # Execute subprocess with data science stack
        process = await asyncio.create_subprocess_exec(
            'uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
            'python', '-c', execution_code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd='/home/jjoravet/mcp_server_best_practices/alpaca-mcp-gold-standard'
        )
        
        # Wait for completion with timeout
        try:
            stdout, _ = await asyncio.wait_for(process.communicate(), timeout=30)
            return stdout.decode('utf-8', errors='replace')
        except asyncio.TimeoutError:
            # Kill the process if it times out
            process.kill()
            await process.wait()
            return "TIMEOUT: Analytics execution exceeded 30 second limit"
            
    except Exception as e:
        logger.error(f"Subprocess execution error: {e}")
        return f"SUBPROCESS ERROR: {type(e).__name__}: {str(e)}"

# Additional helper for creating generic dataset loading patterns
async def create_sample_dataset_from_portfolio() -> Dict[str, Any]:
    """
    Create a sample dataset from current portfolio state for analytics demonstration.
    This demonstrates the dataset agnosticism pattern - any structured data becomes analyzable.
    """
    try:
        from .account_tools import get_positions
        from .market_data_tools import get_stock_snapshot
        
        # Get current positions
        positions_result = await get_positions()
        if positions_result["status"] != "success":
            return {"status": "error", "message": "Could not load portfolio data"}
        
        positions = positions_result["data"]
        if not positions:
            return {"status": "error", "message": "No positions found to create dataset"}
        
        # Create dataset from positions
        dataset_rows = []
        for pos in positions:
            # Get market data for each position
            try:
                snapshot_result = await get_stock_snapshot(pos["symbol"])
                market_data = snapshot_result.get("data", {}) if snapshot_result["status"] == "success" else {}
                
                # Combine position and market data into generic structure
                row = {
                    "entity_id": pos["symbol"],
                    "quantity": float(pos["qty"]),
                    "market_value": float(pos["market_value"]),
                    "unrealized_pnl": float(pos["unrealized_pl"]),
                    "unrealized_pnl_percent": float(pos["unrealized_plpc"]) * 100,
                    "current_price": market_data.get("latest_trade", {}).get("price", 0),
                    "daily_change_percent": market_data.get("daily_bar", {}).get("daily_change_percent", 0),
                    "suggested_role": StateManager.get_symbol(pos["symbol"]).suggested_role.value if StateManager.get_symbol(pos["symbol"]) is not None else "unknown"
                }
                dataset_rows.append(row)
                
            except Exception as e:
                logger.warning(f"Could not get market data for {pos['symbol']}: {e}")
        
        return {
            "status": "success",
            "data": {
                "dataset_name": "portfolio_analytics_dataset",
                "rows": len(dataset_rows),
                "columns": list(dataset_rows[0].keys()) if dataset_rows else [],
                "sample_data": dataset_rows[:5],  # First 5 rows for preview
                "description": "Auto-generated dataset from current portfolio positions with market data"
            },
            "metadata": {
                "operation": "create_sample_dataset",
                "source": "portfolio_positions",
                "adaptable_patterns": [
                    "Works with any position data structure",
                    "Combines multiple data sources into unified dataset", 
                    "Enables cross-dataset analytics and correlation analysis"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating sample dataset: {e}")
        return {
            "status": "error",
            "message": f"Dataset creation failed: {str(e)}",
            "error_type": type(e).__name__
        }