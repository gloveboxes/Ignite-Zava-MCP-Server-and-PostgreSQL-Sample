#!/usr/bin/env python3
"""
Finance Agent MCP Server for Zava Retail

This MCP server provides finance-related tools and operations to support
finance agents with order policies, contracts, sales analysis, and inventory.

The server uses pre-written SQL queries (not dynamically generated SQL) with SQLite ORM.
"""

from ..finance_sqlite import FinanceSQLiteProvider
from ..config import Config

import asyncio
import json
import logging
from datetime import datetime, UTC
from typing import Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from mcp.server.fastmcp import FastMCP
from opentelemetry.instrumentation.starlette import StarletteInstrumentor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Suppress verbose Azure Application Insights logging
for name in [
    "azure.core.pipeline.policies.http_logging_policy",
    "azure.ai.agents",
    "azure.ai.projects",
    "azure.core",
    "azure.identity",
    "uvicorn.access",
    "azure.monitor.opentelemetry.exporter.export._base",
]:
    logging.getLogger(name).setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Zava Finance Agent MCP Server")

# Initialize configuration
config = Config()

# Create database provider
finance_provider = FinanceSQLiteProvider()


async def get_finance_provider() -> FinanceSQLiteProvider:
    """Get or create finance provider instance."""
    return finance_provider


@mcp.tool()
async def get_company_order_policy(
    department: Optional[str] = None
) -> str:
    """
    Get company order processing policies and budget authorization rules.
    
    Returns company policies related to order processing, budget authorization,
    and approval requirements. Policies can be filtered by department.
    
    Args:
        department: Optional department name to filter policies (e.g., "Procurement", "Finance")
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes policy names, types, content, thresholds, and approval requirements.
    
    Example:
        >>> result = await get_company_order_policy(department="Finance")
        >>> data = json.loads(result)
        >>> print(f"Found {data['n']} policies")
    """
    try:
        provider = await get_finance_provider()
        result = await provider.get_company_order_policy(
            department=department
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_company_order_policy: {e}")
        return json.dumps(
            {
                "err": f"Failed to retrieve company order policy: {e!s}",
                "c": [],
                "r": [],
                "n": 0,
            },
            separators=(",", ":"),
            default=str,
        )


@mcp.tool()
async def get_supplier_contract(
    supplier_id: int
) -> str:
    """
    Get supplier contract information including terms and conditions.
    
    Returns active contract details for a specific supplier including
    contract numbers, dates, values, payment terms, and renewal status.
    
    Args:
        supplier_id: The unique identifier for the supplier (required)
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes contract details, dates, values, and calculated expiry information.
    
    Example:
        >>> result = await get_supplier_contract(supplier_id=123)
        >>> data = json.loads(result)
        >>> if data['n'] > 0:
        >>>     contract = dict(zip(data['c'], data['r'][0]))
        >>>     print(f"Contract expires in {contract['days_until_expiry']} days")
    """
    try:
        provider = await get_finance_provider()
        result = await provider.get_supplier_contract(
            supplier_id=supplier_id
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_supplier_contract: {e}")
        return json.dumps(
            {
                "err": f"Failed to retrieve supplier contract: {e!s}",
                "c": [],
                "r": [],
                "n": 0,
            },
            separators=(",", ":"),
            default=str,
        )


@mcp.tool()
async def get_historical_sales_data(
    days_back: int = 30,
    store_id: Optional[int] = None,
    category_name: Optional[str] = None
) -> str:
    """
    Get historical sales data with revenue, order counts, and customer metrics.
    
    Returns comprehensive sales statistics including total revenue, order counts,
    average order values, units sold, and unique customer counts. Data can be
    filtered by store and category. Default lookback period is 90 days.
    
    Args:
        days_back: Number of days to look back (default: 30)
        store_id: Optional store ID to filter results
        category_name: Optional category name to filter results
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes date, store, category, revenue, orders, and customer metrics.
    
    Example:
        >>> # Get last 30 days of sales for Electronics
        >>> result = await get_historical_sales_data(days_back=30, category_name="Electronics")
        >>> data = json.loads(result)
        >>> total_revenue = sum(row[data['c'].index('total_revenue')] for row in data['r'])
    """
    try:
        provider = await get_finance_provider()
        result = await provider.get_historical_sales_data(
            days_back=days_back,
            store_id=store_id,
            category_name=category_name
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_historical_sales_data: {e}")
        return json.dumps(
            {
                "err": f"Failed to retrieve historical sales data: {e!s}",
                "c": [],
                "r": [],
                "n": 0,
            },
            separators=(",", ":"),
            default=str,
        )


@mcp.tool()
async def get_current_inventory_status(
    store_id: Optional[int] = None,
    category_name: Optional[str] = None,
    low_stock_threshold: int = 10
) -> str:
    """
    Get current inventory status across stores with values and low stock alerts.
    
    Returns inventory levels, cost values, retail values, and low stock alerts
    for products across all stores. Can be filtered by store and category.
    Includes inventory value calculations and stock level warnings.
    
    Args:
        store_id: Optional store ID to filter results
        category_name: Optional category name to filter results
        low_stock_threshold: Stock level below which to trigger alert (default: 10)
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes store, product, category, stock levels, values, and alerts.
    
    Example:
        >>> # Get low stock items in Electronics
        >>> result = await get_current_inventory_status(
        >>>     category_name="Electronics",
        >>>     low_stock_threshold=10
        >>> )
        >>> data = json.loads(result)
        >>> low_stock_items = [row for row in data['r'] 
        >>>                    if row[data['c'].index('low_stock_alert')]]
    """
    try:
        provider = await get_finance_provider()
        result = await provider.get_current_inventory_status(
            store_id=store_id,
            category_name=category_name,
            low_stock_threshold=low_stock_threshold
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_current_inventory_status: {e}")
        return json.dumps(
            {
                "err": f"Failed to retrieve inventory status: {e!s}",
                "c": [],
                "r": [],
                "n": 0,
            },
            separators=(",", ":"),
            default=str,
        )


@mcp.tool()
async def get_stores(
    store_name: Optional[str] = None
) -> str:
    """
    Get store information with optional filtering by name.
    
    Returns store details including store IDs, names, and online status.
    Can be filtered by store name using partial, case-insensitive matching.
    Returns all stores if no filter is provided.
    
    Args:
        store_name: Optional store name to search for (partial match, case-insensitive)
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes store_id, store_name, is_online, rls_user_id.
    
    Example:
        >>> # Get all stores
        >>> result = await get_stores()
        >>> data = json.loads(result)
        >>> store_ids = [row[data['c'].index('store_id')] for row in data['r']]
        >>> 
        >>> # Search by name
        >>> result = await get_stores(store_name="Downtown")
        >>> 
        >>> # Get online stores
        >>> result = await get_stores(store_name="Online")
    """
    try:
        provider = await get_finance_provider()
        result = await provider.get_stores(
            store_name=store_name
        )
        return result
    except Exception as e:
        logger.error(f"Error in get_stores: {e}")
        return json.dumps(
            {
                "err": f"Failed to retrieve stores: {e!s}",
                "c": [],
                "r": [],
                "n": 0,
            },
            separators=(",", ":"),
            default=str,
        )


@mcp.tool()
async def get_current_utc_date() -> str:
    """
    Get the current date and time in UTC format.
    
    Useful for calculating date ranges, tracking when analyses were performed,
    and providing context for time-sensitive financial data.
    
    Returns:
        ISO 8601 formatted UTC datetime string (YYYY-MM-DDTHH:MM:SS.ffffffZ)
    
    Example:
        >>> current_time = await get_current_utc_date()
        >>> print(f"Analysis performed at: {current_time}")
    """
    try:
        return datetime.now(UTC).isoformat()
    except Exception as e:
        logger.error(f"Error getting current UTC date: {e}")
        return json.dumps(
            {"err": f"Failed to get current date: {e!s}"},
            separators=(",", ":"),
        )


async def run_http_server() -> None:
    """Run the MCP server in HTTP mode."""

    # Only configure azure monitor if a valid connection string is provided.
    appinsights_connection_string = config.applicationinsights_connection_string
    if (
        appinsights_connection_string
        and "InstrumentationKey=" in appinsights_connection_string
    ):
        configure_azure_monitor(connection_string=appinsights_connection_string)
    else:
        logger.info("Azure Application Insights not configured - running without telemetry")

    # Ensure a single connection pool is created once for the process.
    try:
        await finance_provider.create_pool()
        
        # Instrument Starlette after pool creation
        StarletteInstrumentor().instrument()
        
        logger.info("🚀 Starting Finance Agent MCP Server")
        logger.info("Available tools:")
        logger.info("  - get_company_order_policy: Get order processing policies")
        logger.info("  - get_supplier_contract: Get supplier contract details")
        logger.info("  - get_historical_sales_data: Get sales metrics (90 day default)")
        logger.info("  - get_current_inventory_status: Get inventory with valuations")
        logger.info("  - get_stores: Get store information by name")
        logger.info("  - get_current_utc_date: Get current date/time")
        
        # Configure server settings
        mcp.settings.port = 8002
        mcp.settings.host = "0.0.0.0"
        StarletteInstrumentor().instrument_app(mcp.sse_app())
        StarletteInstrumentor().instrument_app(mcp.streamable_http_app())
        logger.info(
            "❤️ 📡 Finance MCP endpoint available at: http://%s:%d/mcp",
            mcp.settings.host,
            mcp.settings.port,
        )

        # Run the FastMCP server as HTTP endpoint
        await mcp.run_streamable_http_async()
        
    finally:
        # Close the engine on shutdown
        try:
            await finance_provider.close_engine()
        except Exception as e:
            logger.error("⚠️  Error closing finance database engine: %s", e)


def main() -> None:
    """Main entry point for the Finance MCP server."""
    # Run the HTTP server
    asyncio.run(run_http_server())


if __name__ == "__main__":
    main()
