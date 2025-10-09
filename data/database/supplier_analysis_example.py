#!/usr/bin/env python3
"""
DIY Supplier and Procurement Analysis Example

This script demonstrates how to query and analyze DIY supplier and procurement
data in the Zava retail database for enterprise procurement use cases.

Usage:
    python supplier_analysis_example.py

Requirements:
    - PostgreSQL with zava database and retail schema populated with DIY supplier data
    - asyncpg library (pip install asyncpg)
    - Database generated with: python generate_zava_postgres.py
"""

import asyncio
import asyncpg
import logging
from datetime import date, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Database connection configuration
POSTGRES_CONFIG = {
    'host': 'db',  # Change to localhost if running locally
    'port': 5432,
    'user': 'postgres',
    'password': 'P@ssw0rd!',
    'database': 'zava'
}

SCHEMA_NAME = 'retail'

async def create_connection():
    """Create async PostgreSQL connection"""
    try:
        conn = await asyncpg.connect(**POSTGRES_CONFIG)
        logging.info("Connected to PostgreSQL database")
        return conn
    except Exception as e:
        logging.error(f"Failed to connect to PostgreSQL: {e}")
        raise

async def analyze_supplier_performance():
    """Analyze supplier performance metrics"""
    conn = await create_connection()
    
    try:
        logging.info("\n=== SUPPLIER PERFORMANCE ANALYSIS ===")
        
        # Get top performing suppliers
        top_suppliers = await conn.fetch(f"""
            SELECT s.supplier_name, s.supplier_code, s.preferred_vendor,
                   ROUND(AVG(sp.overall_score), 2) as avg_performance,
                   ROUND(AVG(sp.cost_score), 2) as cost_score,
                   ROUND(AVG(sp.quality_score), 2) as quality_score,
                   ROUND(AVG(sp.delivery_score), 2) as delivery_score,
                   COUNT(p.product_id) as products_supplied
            FROM {SCHEMA_NAME}.suppliers s
            JOIN {SCHEMA_NAME}.supplier_performance sp ON s.supplier_id = sp.supplier_id
            LEFT JOIN {SCHEMA_NAME}.products p ON s.supplier_id = p.supplier_id
            WHERE s.active_status = true
            GROUP BY s.supplier_id, s.supplier_name, s.supplier_code, s.preferred_vendor
            ORDER BY avg_performance DESC
            LIMIT 5
        """)
        
        print("\nTop 5 Suppliers by Performance:")
        print(f"{'Supplier':<25} {'Code':<8} {'Pref':<5} {'Overall':<8} {'Cost':<6} {'Quality':<8} {'Delivery':<9} {'Products':<8}")
        print("-" * 85)
        
        for supplier in top_suppliers:
            pref = "Yes" if supplier['preferred_vendor'] else "No"
            print(f"{supplier['supplier_name']:<25} {supplier['supplier_code']:<8} {pref:<5} "
                  f"{supplier['avg_performance']:<8} {supplier['cost_score']:<6} "
                  f"{supplier['quality_score']:<8} {supplier['delivery_score']:<9} {supplier['products_supplied']:<8}")
    
    finally:
        await conn.close()

async def find_bulk_discount_opportunities():
    """Find opportunities for bulk discounts"""
    conn = await create_connection()
    
    try:
        logging.info("\n=== BULK DISCOUNT OPPORTUNITIES ===")
        
        # Find suppliers where pending orders could qualify for bulk discounts
        opportunities = await conn.fetch(f"""
            SELECT s.supplier_name, s.bulk_discount_threshold, s.bulk_discount_percent,
                   COUNT(pr.request_id) as pending_requests,
                   SUM(pr.total_cost) as total_pending_value,
                   CASE 
                     WHEN SUM(pr.total_cost) >= s.bulk_discount_threshold 
                     THEN ROUND(SUM(pr.total_cost) * s.bulk_discount_percent / 100, 2)
                     ELSE 0 
                   END as potential_savings,
                   ROUND(s.bulk_discount_threshold - SUM(pr.total_cost), 2) as amount_needed
            FROM {SCHEMA_NAME}.suppliers s
            JOIN {SCHEMA_NAME}.procurement_requests pr ON s.supplier_id = pr.supplier_id
            WHERE pr.approval_status IN ('Approved', 'Pending') AND s.bulk_discount_percent > 0
            GROUP BY s.supplier_id, s.supplier_name, s.bulk_discount_threshold, s.bulk_discount_percent
            HAVING SUM(pr.total_cost) >= s.bulk_discount_threshold * 0.5  -- At least 50% of threshold
            ORDER BY potential_savings DESC, total_pending_value DESC
        """)
        
        if opportunities:
            print("\nBulk Discount Opportunities:")
            print(f"{'Supplier':<25} {'Threshold':<12} {'Pending':<12} {'Savings':<10} {'Status'}")
            print("-" * 75)
            
            for opp in opportunities:
                savings = opp['potential_savings']
                status = "ELIGIBLE" if savings > 0 else f"Need ${abs(opp['amount_needed']):.0f}"
                
                print(f"{opp['supplier_name']:<25} ${opp['bulk_discount_threshold']:<11,.0f} "
                      f"${opp['total_pending_value']:<11,.0f} ${savings:<9,.0f} {status}")
        else:
            print("No bulk discount opportunities found")
    
    finally:
        await conn.close()

async def esg_compliance_report():
    """Generate ESG compliance report"""
    conn = await create_connection()
    
    try:
        logging.info("\n=== ESG COMPLIANCE REPORT ===")
        
        # ESG compliance analysis
        esg_stats = await conn.fetchrow(f"""
            SELECT 
                COUNT(DISTINCT s.supplier_id) as total_suppliers,
                COUNT(DISTINCT CASE WHEN s.esg_compliant = true THEN s.supplier_id END) as esg_compliant_suppliers,
                COUNT(pr.request_id) as total_requests,
                COUNT(CASE WHEN pr.esg_requirements = true THEN pr.request_id END) as esg_required_requests,
                COUNT(CASE WHEN pr.esg_requirements = true AND s.esg_compliant = true THEN pr.request_id END) as esg_compliant_fulfilled,
                SUM(CASE WHEN pr.esg_requirements = true AND s.esg_compliant = true THEN pr.total_cost ELSE 0 END) as esg_compliant_value
            FROM {SCHEMA_NAME}.suppliers s
            LEFT JOIN {SCHEMA_NAME}.procurement_requests pr ON s.supplier_id = pr.supplier_id
        """)
        
        if esg_stats:
            total_suppliers = esg_stats['total_suppliers']
            esg_suppliers = esg_stats['esg_compliant_suppliers']
            esg_supplier_rate = (esg_suppliers / total_suppliers * 100) if total_suppliers > 0 else 0
            
            esg_requests = esg_stats['esg_required_requests']
            esg_fulfilled = esg_stats['esg_compliant_fulfilled']
            esg_fulfillment_rate = (esg_fulfilled / esg_requests * 100) if esg_requests > 0 else 0
            
            print(f"\nESG Compliance Summary:")
            print(f"ESG Compliant Suppliers:     {esg_suppliers}/{total_suppliers} ({esg_supplier_rate:.1f}%)")
            print(f"ESG Required Requests:       {esg_requests}")
            print(f"ESG Compliant Fulfillment:   {esg_fulfilled}/{esg_requests} ({esg_fulfillment_rate:.1f}%)")
            print(f"ESG Compliant Order Value:   ${esg_stats['esg_compliant_value']:,.2f}")
        
        # List non-ESG suppliers for remediation
        non_esg_suppliers = await conn.fetch(f"""
            SELECT supplier_name, supplier_code, COUNT(p.product_id) as product_count
            FROM {SCHEMA_NAME}.suppliers s
            LEFT JOIN {SCHEMA_NAME}.products p ON s.supplier_id = p.supplier_id
            WHERE s.esg_compliant = false AND s.active_status = true
            GROUP BY s.supplier_id, supplier_name, supplier_code
            ORDER BY product_count DESC
        """)
        
        if non_esg_suppliers:
            print(f"\nNon-ESG Compliant Suppliers (Remediation Needed):")
            print(f"{'Supplier':<25} {'Code':<8} {'Products'}")
            print("-" * 45)
            for supplier in non_esg_suppliers:
                print(f"{supplier['supplier_name']:<25} {supplier['supplier_code']:<8} {supplier['product_count']}")
    
    finally:
        await conn.close()

async def procurement_workflow_analysis():
    """Analyze procurement workflow efficiency"""
    conn = await create_connection()
    
    try:
        logging.info("\n=== PROCUREMENT WORKFLOW ANALYSIS ===")
        
        # Analyze approval times and bottlenecks
        workflow_stats = await conn.fetch(f"""
            SELECT 
                approval_status,
                urgency_level,
                COUNT(*) as request_count,
                ROUND(AVG(total_cost), 2) as avg_value,
                ROUND(SUM(total_cost), 2) as total_value,
                ROUND(AVG(CASE WHEN approved_at IS NOT NULL 
                               THEN EXTRACT(DAYS FROM (approved_at - request_date)) 
                               ELSE NULL END), 1) as avg_approval_days
            FROM {SCHEMA_NAME}.procurement_requests
            GROUP BY approval_status, urgency_level
            ORDER BY approval_status, 
                     CASE urgency_level 
                         WHEN 'Critical' THEN 1 
                         WHEN 'High' THEN 2 
                         WHEN 'Normal' THEN 3 
                         WHEN 'Low' THEN 4 
                     END
        """)
        
        print("\nProcurement Request Status by Urgency:")
        print(f"{'Status':<12} {'Urgency':<8} {'Count':<6} {'Avg Value':<12} {'Total Value':<14} {'Avg Days'}")
        print("-" * 75)
        
        for stat in workflow_stats:
            avg_days = stat['avg_approval_days'] if stat['avg_approval_days'] else "N/A"
            print(f"{stat['approval_status']:<12} {stat['urgency_level']:<8} {stat['request_count']:<6} "
                  f"${stat['avg_value']:<11,.0f} ${stat['total_value']:<13,.0f} {avg_days}")
        
        # Find overdue requests
        overdue_requests = await conn.fetch(f"""
            SELECT pr.request_number, pr.requester_name, pr.department, 
                   pr.urgency_level, pr.total_cost, pr.request_date,
                   s.supplier_name, pr.approval_status
            FROM {SCHEMA_NAME}.procurement_requests pr
            JOIN {SCHEMA_NAME}.suppliers s ON pr.supplier_id = s.supplier_id
            WHERE pr.approval_status = 'Pending' 
              AND pr.request_date < CURRENT_DATE - INTERVAL '7 days'
            ORDER BY pr.urgency_level DESC, pr.request_date
            LIMIT 10
        """)
        
        if overdue_requests:
            print(f"\nOverdue Requests (>7 days pending):")
            print(f"{'Request #':<12} {'Requester':<15} {'Dept':<8} {'Urgency':<8} {'Value':<10} {'Days Pending'}")
            print("-" * 75)
            
            for req in overdue_requests:
                days_pending = (date.today() - req['request_date']).days
                print(f"{req['request_number']:<12} {req['requester_name']:<15} {req['department']:<8} "
                      f"{req['urgency_level']:<8} ${req['total_cost']:<9,.0f} {days_pending}")
    
    finally:
        await conn.close()

async def supplier_lead_time_analysis():
    """Analyze supplier lead times vs requirements"""
    conn = await create_connection()
    
    try:
        logging.info("\n=== SUPPLIER LEAD TIME ANALYSIS ===")
        
        # Compare supplier lead times with request requirements
        lead_time_analysis = await conn.fetch(f"""
            SELECT s.supplier_name, s.lead_time_days as supplier_lead_time,
                   COUNT(pr.request_id) as total_requests,
                   ROUND(AVG(EXTRACT(DAYS FROM (pr.required_by_date - pr.request_date))), 1) as avg_required_lead_time,
                   COUNT(CASE WHEN EXTRACT(DAYS FROM (pr.required_by_date - pr.request_date)) < s.lead_time_days 
                              THEN 1 END) as tight_deadlines,
                   COUNT(CASE WHEN pr.urgency_level IN ('High', 'Critical') THEN 1 END) as urgent_requests
            FROM {SCHEMA_NAME}.suppliers s
            JOIN {SCHEMA_NAME}.procurement_requests pr ON s.supplier_id = pr.supplier_id
            WHERE pr.required_by_date IS NOT NULL
            GROUP BY s.supplier_id, s.supplier_name, s.lead_time_days
            HAVING COUNT(pr.request_id) > 0
            ORDER BY tight_deadlines DESC, urgent_requests DESC
        """)
        
        print("\nSupplier Lead Time vs Request Requirements:")
        print(f"{'Supplier':<25} {'Supplier LT':<12} {'Avg Req LT':<12} {'Tight Deadlines':<15} {'Urgent Reqs'}")
        print("-" * 80)
        
        for analysis in lead_time_analysis:
            tight_pct = (analysis['tight_deadlines'] / analysis['total_requests'] * 100) if analysis['total_requests'] > 0 else 0
            print(f"{analysis['supplier_name']:<25} {analysis['supplier_lead_time']:<12} "
                  f"{analysis['avg_required_lead_time']:<12} {analysis['tight_deadlines']} ({tight_pct:.0f}%)"
                  f"{'':<6} {analysis['urgent_requests']}")
    
    finally:
        await conn.close()

async def main():
    """Run all supplier and procurement analyses"""
    try:
        await analyze_supplier_performance()
        await find_bulk_discount_opportunities()
        await esg_compliance_report()
        await procurement_workflow_analysis()
        await supplier_lead_time_analysis()
        
        logging.info("\n=== ANALYSIS COMPLETE ===")
        logging.info("Use this data to optimize procurement decisions, improve supplier relationships,")
        logging.info("and implement intelligent multi-agent procurement automation.")
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())