#!/usr/bin/env python3
"""
Provides comprehensive customer sales database access with individual table schema tools for Zava Retail DIY Business.
"""

import asyncio
import logging
from typing import Annotated, Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from mcp.server.fastmcp import Context, FastMCP
from opentelemetry.instrumentation.starlette import StarletteInstrumentor
from pydantic import Field

from ..config import Config
from ..sales_analysis_sqlite import SalesAnalysisSQLiteProvider
from ..sales_analysis_text_embeddings import SemanticSearchTextEmbedding

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


db_provider = SalesAnalysisSQLiteProvider()
semantic_search_provider = SemanticSearchTextEmbedding()


# Create MCP server with lifespan support
mcp = FastMCP("mcp-zava-sales", stateless_http=True)


def get_header(ctx: Context, header_name: str) -> Optional[str]:
    """Extract a specific header from the request context."""

    request = ctx.request_context.request
    if request is not None and hasattr(request, "headers"):
        headers = request.headers
        if headers:
            header_value = headers.get(header_name)
            if header_value is not None:
                if isinstance(header_value, bytes):
                    return header_value.decode("utf-8")
                return str(header_value)

    return None


@mcp.tool()
async def get_multiple_table_schemas(
    ctx: Context,
    table_names: Annotated[
        list[str],
        Field(
            description="List of table names. Valid table names include 'customers', 'stores', 'categories', 'product_types', 'products', 'orders', 'order_items', 'inventory', 'suppliers', 'supplier_performance', 'procurement_requests', 'company_policies', 'supplier_contracts', 'approvers', 'notifications', 'product_image_embeddings', 'product_description_embeddings'."
        ),
    ],
) -> str:
    """
    Retrieve schemas for multiple tables. Use this tool only for schemas you have not already fetched during the conversation.

    Args:
        table_names: List of table names. Valid table names include 'customers', 'stores', 'categories', 'product_types', 'products', 'orders', 'order_items', 'inventory', 'suppliers', 'supplier_performance', 'procurement_requests', 'company_policies', 'supplier_contracts', 'approvers', 'notifications', 'product_image_embeddings', 'product_description_embeddings'.

    Returns:
        Concatenated schema strings for the requested tables.
    """

    if not table_names:
        logger.error("Error: table_names parameter is required and cannot be empty")
        return "Error: table_names parameter is required and cannot be empty"

    valid_tables = {
        "customers",
        "stores",
        "categories",
        "product_types",
        "products",
        "orders",
        "order_items",
        "inventory",
        "suppliers",
        "supplier_performance",
        "procurement_requests",
        "company_policies",
        "supplier_contracts",
        "approvers",
        "notifications",
        "product_image_embeddings",
        "product_description_embeddings",
    }

    # Validate table names
    invalid_tables = [name for name in table_names if name not in valid_tables]
    if invalid_tables:
        logger.error(
            "Error: Invalid table names: %s. Valid tables are: %s",
            invalid_tables,
            sorted(valid_tables),
        )
        return f"Error: Invalid table names: {invalid_tables}. Valid tables are: {sorted(valid_tables)}"

    logger.info("Retrieving schemas for tables: %s", ", ".join(table_names))

    try:
        return await db_provider.get_table_metadata_from_list(
            table_names
        )
    except Exception as e:
        logger.error("Error retrieving table schemas: %s", e)
        return f"Error retrieving table schemas: {e!s}"


@mcp.tool()
async def execute_sales_query(
    ctx: Context,
    sqlite_query: Annotated[
        str, Field(description="A well-formed SQLite query.")
    ],
) -> str:
    """Always fetch and inspect the database schema before generating any SQLite using the get_multiple_table_schemas tool; use only exact table and column names, and never invent or infer data, columns, tables, or values—if the information isn't present in the schema or database, clearly state that it cannot be answered. Join related tables for clarity, aggregate results where appropriate, and limit output to 20 rows with a note that the limit is for readability. To identify store types, use the stores.is_online boolean: true indicates an online store, false indicates a physical store. **NEVER** return entity IDs or UUIDs in the response, as they are not meaningful to the user. Instead, use descriptive names or values.

    Args:
        sqlite_query: A well-formed SQL query.

    Returns:
        Query results as a string.
    """

    logger.info("Executing SQL query: %s", sqlite_query)

    try:
        if not sqlite_query:
            return "Error: sqlite_query parameter is required"

        return await db_provider.execute_query(
            sqlite_query
        )

    except Exception as e:
        logger.error("Error executing database query: %s", e)
        return f"Error executing database query: {e!s}"


async def run_http_server() -> None:
    """Run the MCP server in HTTP mode."""

    # Only configure azure monitor if a valid connection string is provided.
    appinsights_connection_string = config.applicationinsights_connection_string
    if (
        appinsights_connection_string
        and "InstrumentationKey=" in appinsights_connection_string
    ):
        configure_azure_monitor(connection_string=appinsights_connection_string)
        logger.info("Azure Application Insights configured.")
    else:
        logger.info("Azure Application Insights not configured.")

    # Ensure a single connection pool is created once for the process.
    try:
        await db_provider.create_pool()

        mcp.settings.port = 8000
        mcp.settings.host = "0.0.0.0"
        StarletteInstrumentor().instrument_app(mcp.sse_app())
        StarletteInstrumentor().instrument_app(mcp.streamable_http_app())
        logger.info(
            "❤️ 📡 MCP endpoint available at: http://%s:%d/mcp",
            mcp.settings.host,
            mcp.settings.port,
        )

        # Run the FastMCP server as HTTP endpoint
        await mcp.run_streamable_http_async()
    finally:
        # Close the engine on shutdown
        try:
            await db_provider.close_engine()
        except Exception as e:
            logger.error("⚠️  Error closing database engine: %s", e)


def main() -> None:
    """Main entry point for the MCP server."""

    # Run the HTTP server
    asyncio.run(run_http_server())


if __name__ == "__main__":
    main()
