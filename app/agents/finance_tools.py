#!/usr/bin/env python3
"""
Finance Agent MCP Server for Zava Retail

This MCP server provides finance-related tools and operations to support
finance agents with order policies, contracts, sales analysis, and inventory.

The server uses pre-written SQL queries (not dynamically generated SQL) and
the empty GUID for RLS for simplicity.
"""

from ..finance_postgres import FinancePostgreSQLProvider
from ..config import Config

import json
import logging
from datetime import datetime, UTC
from typing import Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

from agent_framework import ai_function

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


# Initialize configuration
config = Config()

# Create database provider
finance_provider = FinancePostgreSQLProvider()


async def get_finance_provider() -> FinancePostgreSQLProvider:
    """Get or create finance provider instance."""
    return finance_provider


@ai_function
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


@ai_function
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


@ai_function
async def get_historical_sales_data(
    days_back: int = 90,
    store_id: Optional[int] = None,
    category_name: Optional[str] = None
) -> str:
    """
    Get historical sales data with revenue, order counts, and customer metrics.
    
    Returns comprehensive sales statistics including total revenue, order counts,
    average order values, units sold, and unique customer counts. Data can be
    filtered by store and category. Default lookback period is 90 days.
    
    Args:
        days_back: Number of days to look back (default: 90)
        store_id: Optional store ID to filter results
        category_name: Optional category name to filter results
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes date, store, category, revenue, orders, and customer metrics.
    
    Example:
        >>> # Get last 90 days of sales for Electronics
        >>> result = await get_historical_sales_data(days_back=90, category_name="Electronics")
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


@ai_function
async def get_current_inventory_status(
    store_id: Optional[int] = None,
    category_name: Optional[str] = None,
    low_stock_threshold: int = 50
) -> str:
    """
    Get current inventory status across stores with values and low stock alerts.
    
    Returns inventory levels, cost values, retail values, and low stock alerts
    for products across all stores. Can be filtered by store and category.
    Includes inventory value calculations and stock level warnings.
    
    Args:
        store_id: Optional store ID to filter results
        category_name: Optional category name to filter results
        low_stock_threshold: Stock level below which to trigger alert (default: 50)
    
    Returns:
        JSON string with format: {"c": [columns], "r": [[row data]], "n": count}
        Includes store, product, category, stock levels, values, and alerts.
    
    Example:
        >>> # Get low stock items in Electronics
        >>> result = await get_current_inventory_status(
        >>>     category_name="Electronics",
        >>>     low_stock_threshold=20
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


@ai_function
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

