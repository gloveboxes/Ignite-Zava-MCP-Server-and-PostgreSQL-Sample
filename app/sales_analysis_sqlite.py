#!/usr/bin/env python3
"""
Sales Analysis Database Access Provider for Zava Retail - SQLite Edition

This module provides pre-written SQL queries for sales analysis operations
to support the Sales Analysis MCP server using SQLite with SQLAlchemy ORM.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from .config import Config

logger = logging.getLogger(__name__)
config = Config()


class SalesAnalysisSQLiteProvider:
    """Provides SQLite database access for sales analysis operations."""

    def __init__(self, sqlite_url: Optional[str] = None) -> None:
        # Use default SQLite URL if not provided
        self.sqlite_url = sqlite_url or "sqlite+aiosqlite:///./data/retail.db"
        self.engine: Optional[AsyncEngine] = None
        self.async_session_factory: Optional[async_sessionmaker] = None

    async def __aenter__(self) -> "SalesAnalysisSQLiteProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Async context manager exit."""
        await self.close_engine()

    async def create_pool(self) -> None:
        """Create async engine for database connections."""
        if self.engine is None:
            try:
                self.engine = create_async_engine(
                    self.sqlite_url,
                    connect_args={"timeout": 30, "check_same_thread": False},
                    pool_pre_ping=True,
                    echo=False,
                )

                # Create async session factory
                self.async_session_factory = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )

                logger.info("✅ Sales Analysis SQLite async engine created")
            except Exception as e:
                logger.error("❌ Failed to create SQLAlchemy engine: %s", e)
                raise

    async def close_engine(self) -> None:
        """Close async engine and cleanup."""
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session_factory = None
            logger.info("✅ Sales Analysis SQLite async engine closed")

    def get_session(self) -> AsyncSession:
        """Get a new async session."""
        if not self.async_session_factory:
            raise RuntimeError(
                "No session factory available. Call create_pool() first."
            )
        return self.async_session_factory()

    async def execute_query(self, sql_query: str) -> str:
        """
        Execute a SQL query and return results in compact JSON.

        Compact success shape:
          {"c":["col1","col2"],"r":[[v11,v12],[v21,v22]],"n":2}
        Empty result adds 'msg':
          {"c":[],"r":[],"n":0,"msg":"No rows"}
        Error shape:
          {"err":"...","q":"SELECT ...","c":[],"r":[],"n":0}
        """
        try:
            async with self.get_session() as session:
                # Execute the query
                result = await session.execute(text(sql_query))
                rows = result.fetchall()

                if not rows:
                    return json.dumps(
                        {"c": [], "r": [], "n": 0, "msg": "No rows"},
                        separators=(",", ":"),
                        default=str,
                    )

                # Get column names from result
                columns = list(result.keys())
                data_rows = [
                    [row[i] for i in range(len(columns))] for row in rows
                ]

                return json.dumps(
                    {"c": columns, "r": data_rows, "n": len(data_rows)},
                    separators=(",", ":"),
                    default=str,
                )
        except Exception as e:
            return json.dumps(
                {
                    "err": f"SQLite query failed: {e!s}",
                    "q": sql_query,
                    "c": [],
                    "r": [],
                    "n": 0,
                },
                separators=(",", ":"),
                default=str,
            )

    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Return schema information for a given table."""
        try:
            async with self.get_session() as session:
                # Get column information from pragma
                result = await session.execute(
                    text(f"PRAGMA table_info({table_name})")
                )
                columns = result.fetchall()

                if not columns:
                    return {"error": f"Table '{table_name}' not found"}

                columns_format = ", ".join(
                    f"{col[1]}:{col[2]}" for col in columns
                )

                schema_data = {
                    "table_name": table_name,
                    "description": f"Table containing {table_name} data",
                    "columns_format": columns_format,
                    "columns": [
                        {
                            "name": col[1],
                            "type": col[2],
                            "primary_key": col[5] == 1,
                            "required": col[3] == 1,
                            "default_value": col[4],
                        }
                        for col in columns
                    ],
                }

                return schema_data

        except Exception as e:
            logger.error("Error getting schema: %s", e)
            return {"error": f"Error getting schema: {e!s}"}

    async def get_all_table_names(self) -> List[str]:
        """Get all table names in the database."""
        try:
            async with self.get_session() as session:
                result = await session.execute(
                    text(
                        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                    )
                )
                rows = result.fetchall()
                return [row[0] for row in rows]
        except Exception:
            return []

    def format_schema_metadata_for_ai(self, schema: Dict[str, Any]) -> str:
        """Format schema data into an AI-readable format."""
        if "error" in schema:
            return f"**ERROR:** {schema['error']}"

        table_name = schema.get("table_name", "unknown")
        table_description = table_name.replace("_", " ")

        lines = [f"# Table: {table_name}", ""]
        lines.append(
            f"**Purpose:** {schema.get('description', 'No description available')}"
        )
        lines.append("\n## Schema")
        lines.append(schema.get("columns_format", "N/A"))

        lines.append("\n## Query Hints")
        lines.append(f"- Use `{table_name}` for queries about {table_description}")

        return "\n".join(lines) + "\n"

    async def get_table_metadata_string(self, table_name: str) -> str:
        """Return formatted schema metadata string for a single table."""
        schema = await self.get_table_schema(table_name)
        return self.format_schema_metadata_for_ai(schema)

    async def get_table_metadata_from_list(
        self, table_names: List[str]
    ) -> str:
        """Return formatted schema metadata strings for multiple tables."""
        if not table_names:
            return "Error: table_names parameter is required and cannot be empty"

        schemas = []
        for table_name in table_names:
            try:
                schema_data = await self.get_table_schema(table_name)
                formatted_schema = self.format_schema_metadata_for_ai(schema_data)
                schemas.append(f"\n\n{formatted_schema}")
            except Exception as e:
                schemas.append(f"Error retrieving {table_name} schema: {e!s}\n")

        return "".join(schemas)


async def test_connection() -> bool:
    """Test SQLite connection and return success status."""
    try:
        provider = SalesAnalysisSQLiteProvider()
        await provider.create_pool()
        await provider.close_engine()
        return True
    except Exception as e:
        logger.error("Connection test failed: %s", e)
        return False


async def main() -> None:
    """Main function to test the sales analysis provider."""
    logger.info("🤖 Sales Analysis SQLite Provider Test")
    logger.info("=" * 50)

    if not await test_connection():
        logger.error("❌ Error: Cannot connect to SQLite database")
        return

    try:
        async with SalesAnalysisSQLiteProvider() as provider:
            await provider.create_pool()

            logger.info("🧪 Testing Sales Analysis Queries:")
            logger.info("=" * 50)

            # Test 1: Count all customers
            logger.info("📊 Test 1: Count all customers")
            result = await provider.execute_query(
                "SELECT COUNT(*) as total_customers FROM customers"
            )
            logger.info(
                "Result: %s", result[: 200] + "..." if len(result) > 200 else result
            )

            # Test 2: Count stores
            logger.info("📊 Test 2: Count stores")
            result = await provider.execute_query(
                "SELECT COUNT(*) as total_stores FROM stores"
            )
            logger.info(
                "Result: %s", result[: 200] + "..." if len(result) > 200 else result
            )

            # Test 3: Count categories
            logger.info("📊 Test 3: Count categories")
            result = await provider.execute_query(
                "SELECT COUNT(*) as total_categories FROM categories"
            )
            logger.info(
                "Result: %s", result[: 200] + "..." if len(result) > 200 else result
            )

            # Test 4: Orders with revenue
            logger.info("📊 Test 4: Orders with revenue")
            result = await provider.execute_query(
                """SELECT COUNT(DISTINCT o.order_id) as orders, 
                    SUM(oi.total_amount) as revenue 
                    FROM orders o 
                    JOIN order_items oi ON o.order_id = oi.order_id 
                    LIMIT 1"""
            )
            logger.info(
                "Result: %s", result[: 200] + "..." if len(result) > 200 else result
            )

            logger.info("✅ Sales Analysis query tests completed!")

    except Exception as e:
        logger.error("❌ Error during testing: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
