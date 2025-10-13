#!/usr/bin/env python3
"""
Finance Database Access Provider for Zava Retail

This module provides pre-written SQL queries for finance-related operations
to support the Finance Agent MCP server. All queries use the empty GUID
for RLS (Row Level Security) for simplicity.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import asyncpg
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor

from .config import Config

logger = logging.getLogger(__name__)
config = Config()

# Initialize AsyncPGInstrumentor with our tracer
AsyncPGInstrumentor().instrument()

# PostgreSQL connection configuration
POSTGRES_CONNECTION_PARAMS = config.get_postgres_connection_params()

SCHEMA_NAME = "retail"
# Use empty GUID for RLS as specified
RLS_USER_ID = "00000000-0000-0000-0000-000000000000"


class FinancePostgreSQLProvider:
    """Provides PostgreSQL database access for finance-related operations."""

    def __init__(self, postgres_config: Optional[Dict[str, Any]] = None) -> None:
        self.postgres_config = postgres_config or POSTGRES_CONNECTION_PARAMS
        self.connection_pool: Optional[asyncpg.Pool] = None

    async def __aenter__(self) -> "FinancePostgreSQLProvider":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[object],
    ) -> None:
        """Async context manager exit."""
        await self.close_pool()

    async def create_pool(self) -> None:
        """Create connection pool for better resource management."""
        if self.connection_pool is None:
            try:
                config_copy = dict(self.postgres_config)
                existing_server_settings = config_copy.pop("server_settings", {})
                
                merged_server_settings = {
                    **existing_server_settings,
                    "jit": "off",
                    "work_mem": "4MB",
                    "statement_timeout": "30s",
                }
                
                self.connection_pool = await asyncpg.create_pool(
                    **config_copy,
                    min_size=1,
                    max_size=3,
                    command_timeout=30,
                    server_settings=merged_server_settings,
                )
                logger.info(
                    "✅ Finance PostgreSQL connection pool created for host: %s:%s", 
                    self.postgres_config.get("host", "unknown"),
                    self.postgres_config.get("port", "unknown")
                )
            except Exception as e:
                logger.error("❌ Failed to create PostgreSQL pool: %s", e)
                raise

    async def close_pool(self) -> None:
        """Close connection pool and cleanup."""
        if self.connection_pool:
            await self.connection_pool.close()
            self.connection_pool = None
            logger.info("✅ Finance PostgreSQL connection pool closed")

    async def get_connection(self) -> asyncpg.Connection:
        """Get a connection from pool."""
        if not self.connection_pool:
            raise RuntimeError(
                "No database connection pool available. Call create_pool() first."
            )

        try:
            return await self.connection_pool.acquire()
        except Exception as e:
            logger.error("Failed to acquire connection from pool: %s", e)
            raise RuntimeError(f"Connection pool exhausted or unavailable: {e}") from e

    async def release_connection(self, conn: asyncpg.Connection) -> None:
        """Release connection back to pool."""
        if self.connection_pool:
            await self.connection_pool.release(conn)

    async def get_company_order_policy(
        self,
        department: Optional[str] = None
    ) -> str:
        """
        Get company order processing policies.
        
        Returns company policies related to order processing,
        budget authorization, and related procedures.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            query = f"""
                SELECT 
                    policy_id,
                    policy_name,
                    policy_type,
                    policy_content,
                    department,
                    minimum_order_threshold,
                    approval_required,
                    is_active,
                    CASE 
                        WHEN policy_type = 'order_processing' THEN 'Outlines order processing and fulfillment procedures'
                        WHEN policy_type = 'budget_authorization' THEN 'Specifies budget limits and authorization levels'
                        WHEN policy_type = 'procurement' THEN 'Covers supplier selection and procurement processes'
                        ELSE 'General company policy'
                    END as policy_description,
                    LENGTH(policy_content) as content_length
                FROM {SCHEMA_NAME}.company_policies
                WHERE is_active = true
                    AND policy_type IN ('order_processing', 'budget_authorization')
            """
            
            params = []
            param_index = 1
                
            if department:
                query += f" AND (department = ${param_index} OR department IS NULL)"
                params.append(department)
                param_index += 1
            
            query += " ORDER BY policy_type, policy_name"

            rows = await conn.fetch(query, *params)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": "No order policies found"},
                    separators=(",", ":"),
                    default=str,
                )

            columns = list(rows[0].keys())
            data_rows = [[row[col] for col in columns] for row in rows]
            
            return json.dumps(
                {"c": columns, "r": data_rows, "n": len(data_rows)},
                separators=(",", ":"),
                default=str,
            )

        except Exception as e:
            return json.dumps(
                {
                    "err": f"Company order policy query failed: {e!s}",
                    "c": [],
                    "r": [],
                    "n": 0,
                },
                separators=(",", ":"),
                default=str,
            )
        finally:
            if conn:
                await self.release_connection(conn)

    async def get_supplier_contract(
        self,
        supplier_id: int
    ) -> str:
        """
        Get supplier contract information.
        
        Returns active contract details including terms, conditions,
        and key contract metadata for the specified supplier.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            query = f"""
                SELECT 
                    s.supplier_name,
                    s.supplier_code,
                    s.contact_email,
                    s.contact_phone,
                    -- Contract details
                    sc.contract_id,
                    sc.contract_number,
                    sc.contract_status,
                    sc.start_date,
                    sc.end_date,
                    sc.contract_value,
                    sc.payment_terms,
                    sc.auto_renew,
                    sc.created_at as contract_created,
                    -- Calculated fields
                    CASE 
                        WHEN sc.end_date IS NOT NULL 
                        THEN sc.end_date - CURRENT_DATE 
                        ELSE NULL 
                    END as days_until_expiry,
                    CASE 
                        WHEN sc.end_date IS NOT NULL AND sc.end_date <= CURRENT_DATE + INTERVAL '90 days'
                        THEN true 
                        ELSE false 
                    END as renewal_due_soon
                FROM {SCHEMA_NAME}.suppliers s
                LEFT JOIN {SCHEMA_NAME}.supplier_contracts sc ON s.supplier_id = sc.supplier_id
                WHERE s.supplier_id = $1
                    AND (sc.contract_status = 'active' OR sc.contract_status IS NULL)
                ORDER BY sc.start_date DESC
            """

            rows = await conn.fetch(query, supplier_id)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": f"No contract found for supplier ID {supplier_id}"},
                    separators=(",", ":"),
                    default=str,
                )

            columns = list(rows[0].keys())
            data_rows = [[row[col] for col in columns] for row in rows]
            
            return json.dumps(
                {"c": columns, "r": data_rows, "n": len(data_rows)},
                separators=(",", ":"),
                default=str,
            )

        except Exception as e:
            return json.dumps(
                {
                    "err": f"Supplier contract query failed: {e!s}",
                    "c": [],
                    "r": [],
                    "n": 0,
                },
                separators=(",", ":"),
                default=str,
            )
        finally:
            if conn:
                await self.release_connection(conn)

    async def get_historical_sales_data(
        self,
        days_back: int = 90,
        store_id: Optional[int] = None,
        category_name: Optional[str] = None
    ) -> str:
        """
        Get historical sales data with comprehensive metrics.
        
        Returns sales statistics including total revenue, order counts,
        average values, and breakdowns by time period, store, and category.
        Default lookback period is 90 days.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            # Build the main query
            query = f"""
                SELECT 
                    o.order_date,
                    s.store_name,
                    s.is_online,
                    c.category_name,
                    COUNT(DISTINCT o.order_id) as order_count,
                    SUM(oi.total_amount) as total_revenue,
                    AVG(oi.total_amount) as avg_order_value,
                    SUM(oi.quantity) as total_units_sold,
                    COUNT(DISTINCT o.customer_id) as unique_customers
                FROM {SCHEMA_NAME}.orders o
                JOIN {SCHEMA_NAME}.order_items oi ON o.order_id = oi.order_id
                JOIN {SCHEMA_NAME}.stores s ON o.store_id = s.store_id
                JOIN {SCHEMA_NAME}.products p ON oi.product_id = p.product_id
                JOIN {SCHEMA_NAME}.categories c ON p.category_id = c.category_id
                WHERE o.order_date >= CURRENT_DATE - INTERVAL '{days_back} days'
            """
            
            params = []
            param_index = 1
            
            if store_id is not None:
                query += f" AND o.store_id = ${param_index}"
                params.append(store_id)
                param_index += 1
                
            if category_name:
                query += f" AND UPPER(c.category_name) = UPPER(${param_index})"
                params.append(category_name)
                param_index += 1
            
            query += """
                GROUP BY o.order_date, s.store_name, s.is_online, c.category_name
                ORDER BY o.order_date DESC, total_revenue DESC
            """

            rows = await conn.fetch(query, *params)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": f"No sales data found for last {days_back} days"},
                    separators=(",", ":"),
                    default=str,
                )

            columns = list(rows[0].keys())
            data_rows = [[row[col] for col in columns] for row in rows]
            
            return json.dumps(
                {"c": columns, "r": data_rows, "n": len(data_rows)},
                separators=(",", ":"),
                default=str,
            )

        except Exception as e:
            return json.dumps(
                {
                    "err": f"Historical sales query failed: {e!s}",
                    "c": [],
                    "r": [],
                    "n": 0,
                },
                separators=(",", ":"),
                default=str,
            )
        finally:
            if conn:
                await self.release_connection(conn)

    async def get_current_inventory_status(
        self,
        store_id: Optional[int] = None,
        category_name: Optional[str] = None,
        low_stock_threshold: int = 50
    ) -> str:
        """
        Get current inventory status across stores.
        
        Returns inventory levels, values, and low stock alerts
        for products across all stores or filtered by specific criteria.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            query = f"""
                SELECT 
                    s.store_name,
                    s.is_online,
                    p.product_name,
                    p.sku,
                    c.category_name,
                    pt.type_name as product_type,
                    i.stock_level,
                    p.cost,
                    p.base_price,
                    (i.stock_level * p.cost) as inventory_value,
                    (i.stock_level * p.base_price) as retail_value,
                    CASE 
                        WHEN i.stock_level <= $1 THEN true 
                        ELSE false 
                    END as low_stock_alert
                FROM {SCHEMA_NAME}.inventory i
                JOIN {SCHEMA_NAME}.stores s ON i.store_id = s.store_id
                JOIN {SCHEMA_NAME}.products p ON i.product_id = p.product_id
                JOIN {SCHEMA_NAME}.categories c ON p.category_id = c.category_id
                JOIN {SCHEMA_NAME}.product_types pt ON p.type_id = pt.type_id
                WHERE p.discontinued = false
            """
            
            params: list = [low_stock_threshold]
            param_index = 2
            
            if store_id is not None:
                query += f" AND i.store_id = ${param_index}"
                params.append(store_id)
                param_index += 1
                
            if category_name:
                query += f" AND UPPER(c.category_name) = UPPER(${param_index})"
                params.append(category_name)
                param_index += 1
            
            query += """
                ORDER BY s.store_name, c.category_name, i.stock_level ASC
            """

            rows = await conn.fetch(query, *params)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": "No inventory data found"},
                    separators=(",", ":"),
                    default=str,
                )

            columns = list(rows[0].keys())
            data_rows = [[row[col] for col in columns] for row in rows]
            
            return json.dumps(
                {"c": columns, "r": data_rows, "n": len(data_rows)},
                separators=(",", ":"),
                default=str,
            )

        except Exception as e:
            return json.dumps(
                {
                    "err": f"Inventory status query failed: {e!s}",
                    "c": [],
                    "r": [],
                    "n": 0,
                },
                separators=(",", ":"),
                default=str,
            )
        finally:
            if conn:
                await self.release_connection(conn)


async def test_connection() -> bool:
    """Test PostgreSQL connection and return success status."""
    try:
        pool = await asyncpg.create_pool(**POSTGRES_CONNECTION_PARAMS, min_size=1, max_size=1)
        conn = await pool.acquire()
        await pool.release(conn)
        await pool.close()
        return True
    except Exception as e:
        logger.error("Connection test failed: %s", e)
        return False


async def main() -> None:
    """Main function to test the finance provider."""
    logger.info("🤖 Finance PostgreSQL Provider Test")
    logger.info("=" * 50)

    if not await test_connection():
        logger.error("❌ Error: Cannot connect to PostgreSQL")
        return

    try:
        async with FinancePostgreSQLProvider() as provider:
            await provider.create_pool()

            logger.info("🧪 Testing Finance Queries:")
            logger.info("=" * 50)

            # Test 1: Get company order policies
            logger.info("📊 Test 1: Get company order policies")
            result = await provider.get_company_order_policy()
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 2: Get supplier contract (assuming supplier_id 1 exists)
            logger.info("📊 Test 2: Get supplier contract")
            result = await provider.get_supplier_contract(supplier_id=1)
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 3: Get historical sales data
            logger.info("📊 Test 3: Get historical sales data (90 days)")
            result = await provider.get_historical_sales_data(days_back=90)
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 4: Get current inventory status
            logger.info("📊 Test 4: Get current inventory status")
            result = await provider.get_current_inventory_status(low_stock_threshold=50)
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            logger.info("✅ Finance query tests completed!")

    except Exception as e:
        logger.error("❌ Error during testing: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())
