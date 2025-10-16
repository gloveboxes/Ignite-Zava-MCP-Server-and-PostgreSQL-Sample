#!/usr/bin/env python3
"""
Supplier Database Access Provider for Zava Retail

This module provides pre-written SQL queries for supplier-related operations
to support the Supplier Agent MCP server. All queries use the empty GUID
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


class SupplierPostgreSQLProvider:
    async def list_suppliers(
        self,
        name_query: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """
        List all suppliers or search by partial name (case-insensitive).
        Returns supplier_id, supplier_name, supplier_code, contact_email, supplier_rating, esg_compliant, preferred_vendor, approved_vendor, lead_time_days.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            query = f"""
                SELECT
                    supplier_id,
                    supplier_name,
                    supplier_code,
                    contact_email,
                    supplier_rating,
                    esg_compliant,
                    preferred_vendor,
                    approved_vendor,
                    lead_time_days
                FROM {SCHEMA_NAME}.suppliers
                WHERE active_status = true
            """
            params = []
            if name_query:
                query += " AND supplier_name ILIKE $1"
                params.append(f"%{name_query}%")
            query += " ORDER BY preferred_vendor DESC, supplier_rating DESC, supplier_name ASC LIMIT $2"
            params.append(limit)

            rows = await conn.fetch(query, *params)
            if not rows:
                return json.dumps({"c": [], "r": [], "n": 0, "msg": "No suppliers found"}, separators=(",", ":"), default=str)
            columns = list(rows[0].keys())
            data_rows = [[row[col] for col in columns] for row in rows]
            return json.dumps({"c": columns, "r": data_rows, "n": len(data_rows)}, separators=(",", ":"), default=str)
        except Exception as e:
            return json.dumps({"err": f"List suppliers query failed: {e!s}", "c": [], "r": [], "n": 0}, separators=(",", ":"), default=str)
        finally:
            if conn:
                await self.release_connection(conn)
    """Provides PostgreSQL database access for supplier-related operations."""

    def __init__(self, postgres_config: Optional[Dict[str, Any]] = None) -> None:
        self.postgres_config = postgres_config or POSTGRES_CONNECTION_PARAMS
        self.connection_pool: Optional[asyncpg.Pool] = None

    async def __aenter__(self) -> "SupplierPostgreSQLProvider":
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
                    "✅ Supplier PostgreSQL connection pool created for host: %s:%s", 
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
            logger.info("✅ Supplier PostgreSQL connection pool closed")

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

    async def find_suppliers_for_request(
        self,
        product_category: Optional[str] = None,
        esg_required: bool = False,
        min_rating: float = 3.0,
        max_lead_time: int = 30,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        limit: int = 10
    ) -> str:
        """
        Find suppliers for a request based on various criteria.
        
        Returns suppliers that match the specified requirements including
        product category, ESG compliance, rating, lead time, and budget constraints.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            # Base query using view
            query = f"""
                SELECT 
                    supplier_id,
                    supplier_name,
                    supplier_code,
                    contact_email,
                    contact_phone,
                    supplier_rating,
                    esg_compliant,
                    preferred_vendor,
                    approved_vendor,
                    lead_time_days,
                    minimum_order_amount,
                    bulk_discount_threshold,
                    bulk_discount_percent,
                    payment_terms,
                    available_products,
                    avg_performance_score,
                    contract_status,
                    contract_number,
                    category_name
                FROM {SCHEMA_NAME}.vw_suppliers_for_request
                WHERE supplier_rating >= $1
                    AND lead_time_days <= $2
            """
            
            params = [min_rating, max_lead_time]
            param_index = 3
            
            # Add ESG filter if required
            if esg_required:
                query += f" AND esg_compliant = ${param_index}"
                params.append(True)
                param_index += 1
            
            # Add product category filter if specified
            if product_category:
                query += f" AND UPPER(category_name) = UPPER(${param_index})"
                params.append(product_category)
                param_index += 1
            
            # Add budget filters if specified
            if budget_min is not None:
                query += f" AND minimum_order_amount <= ${param_index}"
                params.append(budget_min)
                param_index += 1
                
            if budget_max is not None:
                query += f" AND bulk_discount_threshold <= ${param_index}"
                params.append(budget_max)
                param_index += 1
            
            query += f"""
                ORDER BY preferred_vendor DESC, avg_performance_score DESC, supplier_rating DESC
                LIMIT ${param_index}
            """
            params.append(limit)

            rows = await conn.fetch(query, *params)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": "No suppliers found matching criteria"},
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
                    "err": f"Find suppliers query failed: {e!s}",
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

    async def get_supplier_history_and_performance(
        self,
        supplier_id: int,
        months_back: int = 12
    ) -> str:
        """
        Get supplier history and performance data.
        
        Returns performance evaluations, recent procurement requests,
        and overall performance trends for the specified supplier.
        """
        conn = None
        try:
            conn = await self.get_connection()
            await conn.execute(
                "SELECT set_config('app.current_rls_user_id', $1, false)", RLS_USER_ID
            )

            # Get supplier basic info and performance history using view
            query = f"""
                SELECT 
                    supplier_name,
                    supplier_code,
                    supplier_rating,
                    esg_compliant,
                    preferred_vendor,
                    lead_time_days,
                    supplier_since,
                    -- Performance metrics
                    evaluation_date,
                    cost_score,
                    quality_score,
                    delivery_score,
                    compliance_score,
                    overall_score,
                    performance_notes,
                    -- Recent procurement activity
                    total_requests,
                    total_value
                FROM {SCHEMA_NAME}.vw_supplier_history_performance
                WHERE supplier_id = $1
                    AND (evaluation_date >= CURRENT_DATE - INTERVAL '{months_back} months' OR evaluation_date IS NULL)
                ORDER BY evaluation_date DESC
            """

            rows = await conn.fetch(query, supplier_id)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": f"No data found for supplier ID {supplier_id}"},
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
                    "err": f"Supplier history query failed: {e!s}",
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
                    supplier_name,
                    supplier_code,
                    contact_email,
                    contact_phone,
                    -- Contract details
                    contract_id,
                    contract_number,
                    contract_status,
                    start_date,
                    end_date,
                    contract_value,
                    payment_terms,
                    auto_renew,
                    contract_created,
                    -- Calculated fields
                    days_until_expiry,
                    renewal_due_soon
                FROM {SCHEMA_NAME}.vw_supplier_contract_details
                WHERE supplier_id = $1
                ORDER BY start_date DESC
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

    async def get_company_supplier_policy(
        self,
        policy_type: Optional[str] = None,
        department: Optional[str] = None
    ) -> str:
        """
        Get company supplier policies.
        
        Returns company policies related to supplier management,
        procurement procedures, and vendor requirements.
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
                    policy_description,
                    content_length
                FROM {SCHEMA_NAME}.vw_company_supplier_policies
            """
            
            params = []
            param_index = 1
            
            # Add WHERE clause if we have filters
            where_added = False
            if policy_type:
                if not where_added:
                    query += " WHERE"
                    where_added = True
                query += f" policy_type = ${param_index}"
                params.append(policy_type)
                param_index += 1
                
            if department:
                if not where_added:
                    query += " WHERE"
                    where_added = True
                else:
                    query += " AND"
                query += f" (department = ${param_index} OR department IS NULL)"
                params.append(department)
                param_index += 1
            
            query += " ORDER BY policy_type, policy_name"

            rows = await conn.fetch(query, *params)
            
            if not rows:
                return json.dumps(
                    {"c": [], "r": [], "n": 0, "msg": "No company policies found"},
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
                    "err": f"Company policy query failed: {e!s}",
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
    """Main function to test the supplier provider."""
    logger.info("🤖 Supplier PostgreSQL Provider Test")
    logger.info("=" * 50)

    if not await test_connection():
        logger.error("❌ Error: Cannot connect to PostgreSQL")
        return

    try:
        async with SupplierPostgreSQLProvider() as provider:
            await provider.create_pool()

            logger.info("🧪 Testing Supplier Queries:")
            logger.info("=" * 50)

            # Test 1: Find suppliers
            logger.info("📊 Test 1: Find suppliers with ESG requirement")
            result = await provider.find_suppliers_for_request(
                esg_required=True,
                min_rating=4.0,
                limit=5
            )
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 2: Get supplier performance (assuming supplier_id 1 exists)
            logger.info("📊 Test 2: Get supplier performance history")
            result = await provider.get_supplier_history_and_performance(supplier_id=1)
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 3: Get supplier contract
            logger.info("📊 Test 3: Get supplier contract")
            result = await provider.get_supplier_contract(supplier_id=1)
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            # Test 4: Get company policies
            logger.info("📊 Test 4: Get procurement policies")
            result = await provider.get_company_supplier_policy(policy_type="procurement")
            logger.info("Result: %s", result[:200] + "..." if len(result) > 200 else result)

            logger.info("✅ Supplier query tests completed!")

    except Exception as e:
        logger.error("❌ Error during testing: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(main())