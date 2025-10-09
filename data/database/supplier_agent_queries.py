"""
Supplier Agent Query Examples

This script demonstrates how to query the enhanced supplier database
to support the Supplier Agent functionality shown in the diagram.

The database now supports all four Supplier Agent query types:
1. Find suppliers for the request
2. Supplier history and performance  
3. Get Supplier Contract
4. Get Company's Supplier Policy
"""

import asyncio
import asyncpg
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database configuration
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres', 
    'password': 'change-me',
    'database': 'zava'
}

SCHEMA_NAME = 'retail'

class SupplierAgent:
    """
    Supplier Agent class that demonstrates the four main query capabilities
    """
    
    def __init__(self, conn):
        self.conn = conn
    
    async def find_suppliers_for_request(self, product_category=None, esg_required=False, 
                                       max_lead_time=30, min_rating=3.5, budget_range=None):
        """
        1. Find suppliers for the request - DB query
        
        This query finds suitable suppliers based on procurement requirements
        """
        query = f"""
            SELECT DISTINCT
                s.supplier_id,
                s.supplier_name,
                s.supplier_code,
                s.contact_email,
                s.contact_phone,
                s.supplier_rating,
                s.esg_compliant,
                s.preferred_vendor,
                s.lead_time_days,
                s.minimum_order_amount,
                s.bulk_discount_threshold,
                s.bulk_discount_percent,
                AVG(sp.overall_score) as avg_performance,
                COUNT(p.product_id) as available_products,
                sc.contract_status,
                sc.contract_number
            FROM {SCHEMA_NAME}.suppliers s
            LEFT JOIN {SCHEMA_NAME}.products p ON s.supplier_id = p.supplier_id
            LEFT JOIN {SCHEMA_NAME}.supplier_performance sp ON s.supplier_id = sp.supplier_id
            LEFT JOIN {SCHEMA_NAME}.supplier_contracts sc ON s.supplier_id = sc.supplier_id
            WHERE s.active_status = true
                AND s.approved_vendor = true
                AND s.supplier_rating >= $1
                AND s.lead_time_days <= $2
        """
        
        params = [min_rating, max_lead_time]
        param_count = 3
        
        if esg_required:
            query += f" AND s.esg_compliant = ${param_count}"
            params.append(True)
            param_count += 1
        
        if product_category:
            query += f"""
                AND EXISTS (
                    SELECT 1 FROM {SCHEMA_NAME}.products prod
                    JOIN {SCHEMA_NAME}.categories cat ON prod.category_id = cat.category_id
                    WHERE prod.supplier_id = s.supplier_id 
                    AND UPPER(cat.category_name) LIKE UPPER($%{param_count}%)
                )
            """
            params.append(f"%{product_category}%")
            param_count += 1
        
        if budget_range:
            min_budget, max_budget = budget_range
            query += f" AND s.minimum_order_amount <= ${param_count}"
            params.append(max_budget)
            param_count += 1
        
        query += """
            GROUP BY s.supplier_id, s.supplier_name, s.supplier_code, s.contact_email, 
                     s.contact_phone, s.supplier_rating, s.esg_compliant, s.preferred_vendor,
                     s.lead_time_days, s.minimum_order_amount, s.bulk_discount_threshold,
                     s.bulk_discount_percent, sc.contract_status, sc.contract_number
            ORDER BY s.preferred_vendor DESC, avg_performance DESC, s.supplier_rating DESC
            LIMIT 10
        """
        
        results = await self.conn.fetch(query, *params)
        
        logging.info("\n🔍 SUPPLIER SEARCH RESULTS:")
        logging.info(f"Found {len(results)} suppliers matching criteria")
        logging.info(f"Filters: Category={product_category}, ESG={esg_required}, Max Lead Time={max_lead_time} days, Min Rating={min_rating}")
        
        for supplier in results:
            esg_icon = "🌱" if supplier['esg_compliant'] else "  "
            preferred_icon = "⭐" if supplier['preferred_vendor'] else "  "
            contract_status = supplier['contract_status'] or 'No Contract'
            
            logging.info(f"{preferred_icon}{esg_icon} {supplier['supplier_name']:<25} | "
                        f"Rating: {supplier['supplier_rating']:.1f} | "
                        f"Performance: {supplier['avg_performance']:.1f if supplier['avg_performance'] else 'N/A'} | "
                        f"Lead: {supplier['lead_time_days']}d | "
                        f"Contract: {contract_status}")
        
        return results
    
    async def get_supplier_history_and_performance(self, supplier_id):
        """
        2. Supplier history and performance - DB query
        
        This query retrieves comprehensive supplier performance history
        """
        # Get basic supplier info
        supplier_info = await self.conn.fetchrow(f"""
            SELECT * FROM {SCHEMA_NAME}.suppliers WHERE supplier_id = $1
        """, supplier_id)
        
        if not supplier_info:
            logging.error(f"Supplier ID {supplier_id} not found")
            return None
        
        # Get performance history
        performance_history = await self.conn.fetch(f"""
            SELECT 
                evaluation_date,
                cost_score,
                quality_score,
                delivery_score,
                compliance_score,
                overall_score,
                notes
            FROM {SCHEMA_NAME}.supplier_performance
            WHERE supplier_id = $1
            ORDER BY evaluation_date DESC
            LIMIT 12
        """, supplier_id)
        
        # Get recent procurement requests
        recent_orders = await self.conn.fetch(f"""
            SELECT 
                pr.request_number,
                pr.request_date,
                pr.total_cost,
                pr.approval_status,
                pr.urgency_level,
                p.product_name
            FROM {SCHEMA_NAME}.procurement_requests pr
            JOIN {SCHEMA_NAME}.products p ON pr.product_id = p.product_id
            WHERE pr.supplier_id = $1
            ORDER BY pr.request_date DESC
            LIMIT 10
        """, supplier_id)
        
        logging.info(f"\n📊 SUPPLIER PERFORMANCE ANALYSIS: {supplier_info['supplier_name']}")
        logging.info(f"Supplier Code: {supplier_info['supplier_code']}")
        logging.info(f"Overall Rating: {supplier_info['supplier_rating']:.1f}/5.0")
        logging.info(f"ESG Compliant: {'Yes' if supplier_info['esg_compliant'] else 'No'}")
        logging.info(f"Preferred Vendor: {'Yes' if supplier_info['preferred_vendor'] else 'No'}")
        
        if performance_history:
            logging.info("\n📈 Recent Performance Scores:")
            logging.info("Date       | Cost | Quality | Delivery | Compliance | Overall")
            logging.info("-" * 60)
            for perf in performance_history[:6]:
                logging.info(f"{perf['evaluation_date']} | "
                           f"{perf['cost_score']:.1f}  |   {perf['quality_score']:.1f}   |    {perf['delivery_score']:.1f}   |     {perf['compliance_score']:.1f}    |  {perf['overall_score']:.1f}")
        
        if recent_orders:
            logging.info("\n📦 Recent Orders:")
            total_value = sum(order['total_cost'] for order in recent_orders)
            logging.info(f"Total Recent Order Value: ${total_value:,.2f}")
            for order in recent_orders[:5]:
                status_icon = "✅" if order['approval_status'] == 'Approved' else "⏳"
                logging.info(f"{status_icon} {order['request_number']} - ${order['total_cost']:,.2f} - {order['product_name'][:30]}")
        
        return {
            'supplier_info': supplier_info,
            'performance_history': performance_history,
            'recent_orders': recent_orders
        }
    
    async def get_supplier_contract(self, supplier_id):
        """
        3. Get Supplier Contract - document
        
        This query retrieves the supplier's contract details and documents
        """
        contract_info = await self.conn.fetchrow(f"""
            SELECT 
                sc.*,
                s.supplier_name,
                s.supplier_code
            FROM {SCHEMA_NAME}.supplier_contracts sc
            JOIN {SCHEMA_NAME}.suppliers s ON sc.supplier_id = s.supplier_id
            WHERE sc.supplier_id = $1 
            AND sc.contract_status = 'active'
            ORDER BY sc.start_date DESC
            LIMIT 1
        """, supplier_id)
        
        if not contract_info:
            logging.warning(f"No active contract found for supplier ID {supplier_id}")
            return None
        
        # Get related contract policies
        contract_policies = await self.conn.fetch(f"""
            SELECT policy_type, policy_name, document_content, effective_date, version
            FROM {SCHEMA_NAME}.supplier_policies
            WHERE supplier_id = $1 
            AND policy_type IN ('contract', 'terms_conditions', 'payment_policy')
            AND is_active = true
        """, supplier_id)
        
        logging.info(f"\n📄 SUPPLIER CONTRACT: {contract_info['supplier_name']}")
        logging.info(f"Contract Number: {contract_info['contract_number']}")
        logging.info(f"Contract Type: {contract_info['contract_type'].title()}")
        logging.info(f"Status: {contract_info['contract_status'].title()}")
        logging.info(f"Start Date: {contract_info['start_date']}")
        logging.info(f"End Date: {contract_info['end_date']}")
        logging.info(f"Contract Value: ${contract_info['contract_value']:,.2f}")
        logging.info(f"Payment Terms: {contract_info['payment_terms']}")
        logging.info(f"Auto Renew: {'Yes' if contract_info['auto_renew'] else 'No'}")
        
        if contract_policies:
            logging.info("\n📋 Related Contract Documents:")
            for policy in contract_policies:
                logging.info(f"• {policy['policy_name']} (v{policy['version']})")
                logging.info(f"  Content Preview: {policy['document_content'][:100]}...")
        
        return {
            'contract_info': contract_info,
            'contract_policies': contract_policies
        }
    
    async def get_company_supplier_policy(self, policy_type=None, department=None):
        """
        4. Get Company's Supplier Policy - document
        
        This query retrieves internal company policies for supplier management
        """
        query = f"""
            SELECT 
                policy_name,
                policy_type,
                policy_content,
                policy_summary,
                department,
                applies_to_role,
                minimum_order_threshold,
                approval_required,
                escalation_level,
                version,
                effective_date,
                created_by,
                approved_by
            FROM {SCHEMA_NAME}.company_policies
            WHERE is_active = true
        """
        
        params = []
        if policy_type:
            query += " AND policy_type = $1"
            params.append(policy_type)
        
        if department:
            param_num = len(params) + 1
            query += f" AND UPPER(department) = UPPER(${param_num})"
            params.append(department)
        
        query += " ORDER BY policy_type, effective_date DESC"
        
        policies = await self.conn.fetch(query, *params)
        
        logging.info("\n📚 COMPANY SUPPLIER POLICIES")
        if policy_type:
            logging.info(f"Policy Type: {policy_type}")
        if department:
            logging.info(f"Department: {department}")
        logging.info(f"Found {len(policies)} active policies")
        
        for policy in policies:
            threshold = f"${policy['minimum_order_threshold']:,.2f}" if policy['minimum_order_threshold'] else "No limit"
            approval = "Required" if policy['approval_required'] else "Not required"
            
            logging.info(f"\n📋 {policy['policy_name']}")
            logging.info(f"   Type: {policy['policy_type']}")
            logging.info(f"   Department: {policy['department']}")
            logging.info(f"   Threshold: {threshold}")
            logging.info(f"   Approval: {approval}")
            logging.info(f"   Version: {policy['version']}")
            logging.info(f"   Summary: {policy['policy_summary'] or policy['policy_content'][:100]}...")
        
        return policies

async def main():
    """
    Demonstration of Supplier Agent capabilities
    """
    try:
        # Connect to database
        conn = await asyncpg.connect(**POSTGRES_CONFIG)
        agent = SupplierAgent(conn)
        
        logging.info("🤖 Supplier Agent Demo - Enhanced Database Capabilities")
        logging.info("=" * 60)
        
        # Demo 1: Find suppliers for a DIY project request
        logging.info("\n1️⃣  FINDING SUPPLIERS FOR REQUEST")
        suppliers = await agent.find_suppliers_for_request(
            product_category="TOOLS",
            esg_required=True,
            max_lead_time=21,
            min_rating=4.0,
            budget_range=(1000, 50000)
        )
        
        # Demo 2: Get performance history for first supplier found
        if suppliers:
            supplier_id = suppliers[0]['supplier_id']
            logging.info("\n2️⃣  SUPPLIER HISTORY & PERFORMANCE")
            await agent.get_supplier_history_and_performance(supplier_id)
            
            # Demo 3: Get supplier contract
            logging.info("\n3️⃣  SUPPLIER CONTRACT")
            await agent.get_supplier_contract(supplier_id)
        
        # Demo 4: Get company policies
        logging.info("\n4️⃣  COMPANY SUPPLIER POLICIES")
        await agent.get_company_supplier_policy(policy_type="procurement")
        
        await agent.get_company_supplier_policy(policy_type="vendor_approval")
        
        await conn.close()
        
    except Exception as e:
        logging.error(f"Error in supplier agent demo: {e}")

if __name__ == "__main__":
    asyncio.run(main())