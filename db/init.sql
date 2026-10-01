-- ==============================================================================
-- Atlas Distribution S.A. - Enterprise Database Architecture (SRV-DB-01)
-- Engine: PostgreSQL 16 Enterprise Cluster
-- Schemas: identity, crm, logistics, security_audit
-- Compliance Scope: GDPR / RGPD (Art. 33/34), PCI-DSS 3.4 (Masked Card Tokens)
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. SCHEMAS INITIALIZATION
-- ------------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS identity;
CREATE SCHEMA IF NOT EXISTS crm;
CREATE SCHEMA IF NOT EXISTS logistics;
CREATE SCHEMA IF NOT EXISTS security_audit;

-- ------------------------------------------------------------------------------
-- 2. IDENTITY SCHEMA (Authentication, Service Accounts, RBAC)
-- ------------------------------------------------------------------------------
CREATE TABLE identity.roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO identity.roles (role_name, description) VALUES
    ('SYSTEM_ADMIN', 'Full cluster administrative access'),
    ('SERVICE_AUTOMATION', 'Service account for automated data backups and ETL pipelines'),
    ('WEB_APPLICATION', 'Application service account for public-facing store backend'),
    ('SECURITY_ANALYST', 'Read-only access for forensic inspection and threat hunting'),
    ('LOGISTICS_OPERATOR', 'Warehouse and shipping management access');

CREATE TABLE identity.service_accounts (
    account_id SERIAL PRIMARY KEY,
    account_name VARCHAR(50) NOT NULL UNIQUE,
    role_id INT REFERENCES identity.roles(role_id),
    api_key_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    allowed_cidr CIDR DEFAULT '172.28.30.0/24',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO identity.service_accounts (account_name, role_id, api_key_hash, allowed_cidr) VALUES
    ('svc-backup', 2, crypt('BackupSecret2026!', gen_salt('bf', 10)), '172.28.30.0/24'),
    ('svc-web-gateway', 3, crypt('AtlasWebProxyKey2026!', gen_salt('bf', 10)), '172.28.10.0/24'),
    ('svc-warehouse-sync', 5, crypt('WarehouseSyncToken99!', gen_salt('bf', 10)), '172.28.20.0/24');

-- ------------------------------------------------------------------------------
-- 3. CRM SCHEMA (Customer Accounts, PII, High-Risk Target for Exfiltration)
-- ------------------------------------------------------------------------------
CREATE TABLE crm.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_uuid UUID DEFAULT uuid_generate_v4() NOT NULL UNIQUE,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    phone_primary VARCHAR(35),
    phone_secondary VARCHAR(35),
    billing_street VARCHAR(255) NOT NULL,
    billing_city VARCHAR(100) NOT NULL,
    billing_postal_code VARCHAR(20) NOT NULL,
    billing_country VARCHAR(60) DEFAULT 'France',
    password_hash VARCHAR(255) NOT NULL,
    credit_card_masked VARCHAR(20),
    credit_card_token UUID DEFAULT uuid_generate_v4(),
    kyc_verified BOOLEAN DEFAULT TRUE,
    account_status VARCHAR(25) DEFAULT 'ACTIVE',
    loyalty_points INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed 40,000 realistic synthetic customer records matching the incident scenario
INSERT INTO crm.customers (
    first_name, last_name, email, phone_primary, billing_street,
    billing_city, billing_postal_code, password_hash, credit_card_masked, created_at
)
SELECT
    (ARRAY['Jean', 'Pierre', 'Michel', 'Alain', 'Nicolas', 'Alexandre', 'Thomas', 'Sophie', 'Marie', 'Camille'])[1 + (seq % 10)],
    (ARRAY['Dupont', 'Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy'])[1 + (seq % 10)],
    'client.' || seq || '@' || (ARRAY['atlas-client.fr', 'corporate.eu', 'mail-hub.com', 'pro-commerce.net'])[1 + (seq % 4)],
    '+33 6 ' || lpad((seq % 99999999)::text, 8, '0'),
    (seq % 850 + 1) || ' Avenue des Champs, Immeuble ' || (ARRAY['A', 'B', 'C', 'D'])[1 + (seq % 4)],
    (ARRAY['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Bordeaux', 'Nantes', 'Strasbourg', 'Lille', 'Rennes', 'Montpellier'])[1 + (seq % 10)],
    lpad((seq % 95000 + 1000)::text, 5, '0'),
    '$2y$12$e8YkZg7k7c0P9yM' || substr(md5(seq::text), 1, 38),
    '****-****-****-' || lpad((seq % 9999)::text, 4, '0'),
    NOW() - (seq || ' minutes')::interval
FROM generate_series(1, 40000) AS seq;

-- ------------------------------------------------------------------------------
-- 4. LOGISTICS SCHEMA (Supply Chain, Warehouse Orders, Stock)
-- ------------------------------------------------------------------------------
CREATE TABLE logistics.warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    warehouse_code VARCHAR(20) NOT NULL UNIQUE,
    location_name VARCHAR(100) NOT NULL,
    capacity_pallets INT NOT NULL,
    is_operational BOOLEAN DEFAULT TRUE
);

INSERT INTO logistics.warehouses (warehouse_code, location_name, capacity_pallets) VALUES
    ('WH-PARIS-NORTH', 'Roissy Logistics Platform', 45000),
    ('WH-LYON-SOUTH', 'Saint-Quentin Fallavier Hub', 35000),
    ('WH-MARSEILLE-PORT', 'Fos-sur-Mer Intermodal Depot', 60000);

CREATE TABLE logistics.orders (
    order_id SERIAL PRIMARY KEY,
    order_number VARCHAR(64) NOT NULL UNIQUE,
    customer_id INT REFERENCES crm.customers(customer_id),
    warehouse_id INT REFERENCES logistics.warehouses(warehouse_id),
    order_status VARCHAR(30) DEFAULT 'PROCESSING',
    total_amount_eur NUMERIC(10, 2) NOT NULL,
    shipping_tracking_number VARCHAR(100),
    order_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO logistics.orders (order_number, customer_id, warehouse_id, total_amount_eur, shipping_tracking_number)
SELECT
    'ORD-2026-' || lpad(seq::text, 6, '0'),
    (seq % 40000) + 1,
    (seq % 3) + 1,
    (seq % 450) + 19.99,
    'FR-TRACK-' || md5(seq::text)
FROM generate_series(1, 5000) AS seq;

-- ------------------------------------------------------------------------------
-- 5. SECURITY AUDIT SCHEMA (Forensic Logging, PGAudit Emulation)
-- ------------------------------------------------------------------------------
CREATE TABLE security_audit.query_audit_log (
    audit_id SERIAL PRIMARY KEY,
    event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_user VARCHAR(64) DEFAULT SESSION_USER,
    client_addr INET,
    client_port INT,
    command_tag VARCHAR(64),
    target_table VARCHAR(128),
    rows_affected INT,
    query_preview TEXT,
    alert_level VARCHAR(20) DEFAULT 'NORMAL'
);

-- Trigger to record bulk exfiltration attempts on crm.customers
CREATE OR REPLACE FUNCTION security_audit.flag_bulk_access()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO security_audit.query_audit_log (
        session_user, client_addr, command_tag, target_table, rows_affected, query_preview, alert_level
    ) VALUES (
        SESSION_USER, inet_client_addr(), 'SELECT', 'crm.customers', 1,
        'High-volume customer records query detected', 'CRITICAL_EXFIL'
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------------------------
-- 6. INDEXING AND RETRIEVAL OPTIMIZATION
-- ------------------------------------------------------------------------------
CREATE INDEX idx_customers_email ON crm.customers(email);
CREATE INDEX idx_customers_uuid ON crm.customers(customer_uuid);
CREATE INDEX idx_orders_number ON logistics.orders(order_number);
CREATE INDEX idx_orders_customer ON logistics.orders(customer_id);

-- Legacy Compatibility View for Web Tier (SRV-WEB-01 db.php compatibility)
CREATE OR REPLACE VIEW public.customers AS
    SELECT 
        customer_id AS id,
        customer_uuid,
        first_name || ' ' || last_name AS full_name,
        email,
        phone_primary AS phone,
        billing_street || ', ' || billing_postal_code || ' ' || billing_city AS shipping_address,
        password_hash,
        substr(credit_card_masked, 16, 4) AS credit_card_last4,
        account_status,
        created_at
    FROM crm.customers;

GRANT USAGE ON SCHEMA identity, crm, logistics, security_audit TO atlas_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA identity, crm, logistics, security_audit, public TO atlas_admin;
