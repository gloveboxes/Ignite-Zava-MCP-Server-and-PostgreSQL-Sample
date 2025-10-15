-- Supplier Contract Details View
-- This view provides a comprehensive view of supplier contract information
-- including calculated fields for contract expiry and renewal status.

CREATE OR REPLACE VIEW retail.vw_supplier_contract_details AS
SELECT 
    s.supplier_id,
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
FROM retail.suppliers s
LEFT JOIN retail.supplier_contracts sc ON s.supplier_id = sc.supplier_id
WHERE (sc.contract_status = 'active' OR sc.contract_status IS NULL);

-- Grant appropriate permissions based on existing database setup
-- The database creates a 'store_manager' role with SELECT permissions on all retail schema tables
-- Views inherit permissions from the underlying tables, so store_manager will automatically have access

-- If you need to grant permissions to additional roles:
-- GRANT SELECT ON retail.vw_supplier_contract_details TO store_manager;
-- GRANT SELECT ON retail.vw_supplier_contract_details TO read_only_role;
-- GRANT SELECT ON retail.vw_supplier_contract_details TO application_role;

-- Note: The database uses Row Level Security (RLS) policies
-- Super Manager UUID (00000000-0000-0000-0000-000000000000) has access to all rows
-- Other users are restricted by RLS policies based on their rls_user_id

-- Example usage:
-- SELECT * FROM retail.vw_supplier_contract_details WHERE supplier_id = 1;
-- SELECT * FROM retail.vw_supplier_contract_details WHERE renewal_due_soon = true;
-- SELECT * FROM retail.vw_supplier_contract_details WHERE days_until_expiry < 30;