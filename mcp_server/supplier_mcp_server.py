#!/usr/bin/env python3
"""
Supplier Agent MCP Server for Zava Retail

This MCP server provides tools to support a Supplier Agent with the following capabilities:
1. Find suppliers for the request - DB query
2. Supplier history and performance - DB query  
3. Get Supplier Contract - document
4. Get Company's Supplier policy - document

Uses pre-written SQL queries from supplier_postgres.py for all database operations.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Annotated, Optional
from azure.monitor.opentelemetry import configure_azure_monitor
from mcp.server.fastmcp import Context, FastMCP
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from pydantic import Field

try:
    from .config import Config
    from .supplier_postgres import SupplierPostgreSQLProvider
except ImportError:
    # Handle direct execution (not as module)
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from mcp_server.config import Config
    from mcp_server.supplier_postgres import SupplierPostgreSQLProvider

config = Config()
logger = logging.getLogger(__name__)

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

# Create database provider
supplier_provider = SupplierPostgreSQLProvider()

# Create MCP server with lifespan support
mcp = FastMCP("mcp-zava-supplier", stateless_http=True)


def get_header(ctx: Context, header_name: str) -> Optional[str]:
    """Extract a specific header from the request context."""
    request = ctx.request_context.request
    if request is not None and hasattr(request, "headers"):
        headers = request.headers
        if headers:
            return headers.get(header_name)
    return None


def get_rls_user_id(ctx: Context) -> str:
    """Get the Row Level Security User ID from the request context."""
    rls_user_id = get_header(ctx, "x-rls-user-id")
    if rls_user_id is None:
        # Default to empty GUID for simplicity as specified
        rls_user_id = "00000000-0000-0000-0000-000000000000"
    return rls_user_id


@mcp.tool()
async def find_suppliers_for_request(
    ctx: Context,
    product_category: Annotated[
        Optional[str],
        Field(
            description="Product category to filter suppliers by (e.g., 'Tools', 'Hardware', 'Building Materials'). Leave empty to search all categories."
        ),
    ] = None,
    esg_required: Annotated[
        bool,
        Field(
            description="Whether ESG (Environmental, Social, Governance) compliance is required. Set to true if the request specifically requires ESG-compliant suppliers."
        ),
    ] = False,
    min_rating: Annotated[
        float,
        Field(
            description="Minimum supplier rating required (0.0 to 5.0). Default is 3.0 for acceptable quality suppliers."
        ),
    ] = 3.0,
    max_lead_time: Annotated[
        int,
        Field(
            description="Maximum acceptable lead time in days. Default is 30 days for standard procurement."
        ),
    ] = 30,
    budget_min: Annotated[
        Optional[float],
        Field(
            description="Minimum budget amount to consider suppliers with appropriate minimum order amounts."
        ),
    ] = None,
    budget_max: Annotated[
        Optional[float],
        Field(
            description="Maximum budget amount to filter suppliers by bulk discount thresholds."
        ),
    ] = None,
    limit: Annotated[
        int,
        Field(
            description="Maximum number of suppliers to return. Default is 10."
        ),
    ] = 10,
) -> str:
    """
    Find suppliers that match procurement request requirements.
    
    This tool searches for suppliers based on product category, ESG compliance,
    rating requirements, lead time constraints, and budget considerations.
    Returns suppliers ranked by preference and performance.
    
    Returns:
        JSON with supplier details including ratings, contact info, terms, and contract status.
    """
    
    rls_user_id = get_rls_user_id(ctx)
    
    logger.info("Finding suppliers - Category: %s, ESG: %s, Min Rating: %.1f", 
                product_category, esg_required, min_rating)
    logger.info("RLS User ID: %s", rls_user_id)

    try:
        result = await supplier_provider.find_suppliers_for_request(
            product_category=product_category,
            esg_required=esg_required,
            min_rating=min_rating,
            max_lead_time=max_lead_time,
            budget_min=budget_min,
            budget_max=budget_max,
            limit=limit
        )
        return result

    except Exception as e:
        logger.error("Find suppliers failed: %s", e)
        return f'{{"err":"Find suppliers failed: {e!s}","c":[],"r":[],"n":0}}'


@mcp.tool()
async def get_supplier_history_and_performance(
    ctx: Context,
    supplier_id: Annotated[
        int,
        Field(
            description="Unique identifier of the supplier to get performance history for."
        ),
    ],
    months_back: Annotated[
        int,
        Field(
            description="Number of months of history to retrieve. Default is 12 months for annual performance view."
        ),
    ] = 12,
) -> str:
    """
    Get detailed supplier performance history and metrics.
    
    This tool retrieves historical performance evaluations, procurement activity,
    and performance trends for a specific supplier. Includes cost, quality,
    delivery, and compliance scores over time.
    
    Returns:
        JSON with performance scores, evaluation dates, procurement history, and trend data.
    """
    
    rls_user_id = get_rls_user_id(ctx)
    
    logger.info("Getting supplier history - ID: %d, Months: %d", supplier_id, months_back)
    logger.info("RLS User ID: %s", rls_user_id)

    try:
        result = await supplier_provider.get_supplier_history_and_performance(
            supplier_id=supplier_id,
            months_back=months_back
        )
        return result

    except Exception as e:
        logger.error("Get supplier history failed: %s", e)
        return f'{{"err":"Get supplier history failed: {e!s}","c":[],"r":[],"n":0}}'


@mcp.tool()
async def get_supplier_contract(
    ctx: Context,
    supplier_id: Annotated[
        int,
        Field(
            description="Unique identifier of the supplier to get contract information for."
        ),
    ],
) -> str:
    """
    Get supplier contract details and terms.
    
    This tool retrieves active contract information including contract numbers,
    terms and conditions, payment terms, contract values, expiration dates,
    and renewal information for a specific supplier.
    
    Returns:
        JSON with contract details, terms, values, dates, and renewal status.
    """
    
    rls_user_id = get_rls_user_id(ctx)
    
    logger.info("Getting supplier contract - ID: %d", supplier_id)
    logger.info("RLS User ID: %s", rls_user_id)

    try:
        result = await supplier_provider.get_supplier_contract(supplier_id=supplier_id)
        return result

    except Exception as e:
        logger.error("Get supplier contract failed: %s", e)
        return f'{{"err":"Get supplier contract failed: {e!s}","c":[],"r":[],"n":0}}'


@mcp.tool()
async def get_company_supplier_policy(
    ctx: Context,
    policy_type: Annotated[
        Optional[str],
        Field(
            description="Type of policy to retrieve. Options: 'procurement', 'vendor_approval', 'budget_authorization', 'order_processing'. Leave empty to get all supplier-related policies."
        ),
    ] = None,
    department: Annotated[
        Optional[str],
        Field(
            description="Department-specific policies to retrieve. Leave empty to get company-wide policies."
        ),
    ] = None,
) -> str:
    """
    Get company policies related to supplier management.
    
    This tool retrieves company policies and procedures for supplier selection,
    procurement processes, vendor approval requirements, and budget authorization
    limits. Helps ensure compliance with company guidelines.
    
    Returns:
        JSON with policy documents, procedures, requirements, and approval thresholds.
    """
    
    rls_user_id = get_rls_user_id(ctx)
    
    logger.info("Getting company policies - Type: %s, Department: %s", policy_type, department)
    logger.info("RLS User ID: %s", rls_user_id)

    try:
        result = await supplier_provider.get_company_supplier_policy(
            policy_type=policy_type,
            department=department
        )
        return result

    except Exception as e:
        logger.error("Get company policy failed: %s", e)
        return f'{{"err":"Get company policy failed: {e!s}","c":[],"r":[],"n":0}}'


@mcp.tool()
async def get_current_utc_date() -> str:
    """Get the current UTC date and time in ISO format. Useful for date-time relative queries or understanding the current date for time-sensitive supplier analysis.

    Returns:
        Current UTC date and time in ISO format (YYYY-MM-DDTHH:MM:SS.fffffZ)
    """
    logger.info("Retrieving current UTC date and time")
    return datetime.now(timezone.utc).isoformat()


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
        await supplier_provider.create_pool()
        
        # Instrument Starlette after pool creation
        StarletteInstrumentor().instrument()
        
        logger.info("🚀 Starting Supplier Agent MCP Server")
        logger.info("Available tools:")
        logger.info("  - find_suppliers_for_request: Find suppliers matching requirements")
        logger.info("  - get_supplier_history_and_performance: Get supplier performance data")
        logger.info("  - get_supplier_contract: Get contract details")
        logger.info("  - get_company_supplier_policy: Get company policies")
        logger.info("  - get_current_utc_date: Get current date/time")
        
        # Configure server settings
        mcp.settings.port = 8001
        mcp.settings.host = "0.0.0.0"
        StarletteInstrumentor().instrument_app(mcp.sse_app())
        StarletteInstrumentor().instrument_app(mcp.streamable_http_app())
        logger.info(
            "❤️ 📡 Supplier MCP endpoint available at: http://%s:%d/mcp",
            mcp.settings.host,
            mcp.settings.port,
        )

        # Run the FastMCP server as HTTP endpoint
        await mcp.run_streamable_http_async()
        
    finally:
        # Close the pool on shutdown
        try:
            await supplier_provider.close_pool()
        except Exception as e:
            logger.error("⚠️  Error closing supplier database pool: %s", e)


def main() -> None:
    """Main entry point for the Supplier MCP server."""
    # Run the HTTP server
    asyncio.run(run_http_server())


if __name__ == "__main__":
    main()