-- Production database initialization script
-- Replace placeholders with actual values before running

-- Create the database
CREATE DATABASE hospital_metrics_prod_0900f37a
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create the user with limited privileges
CREATE USER hospital_metrics_y1e8wgay WITH PASSWORD '0CM%D#ZKyHcX6#PgoY3wo9!S5lEQZI0Y';

-- Connect to the new database
\c hospital_metrics_prod_0900f37a

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set up schema
CREATE SCHEMA IF NOT EXISTS hospital_metrics;

-- Grant privileges
ALTER DATABASE hospital_metrics_prod_0900f37a OWNER TO hospital_metrics_y1e8wgay;
GRANT ALL PRIVILEGES ON DATABASE hospital_metrics_prod_0900f37a TO hospital_metrics_y1e8wgay;
GRANT ALL PRIVILEGES ON SCHEMA hospital_metrics TO hospital_metrics_y1e8wgay;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA hospital_metrics TO hospital_metrics_y1e8wgay;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA hospital_metrics TO hospital_metrics_y1e8wgay;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA hospital_metrics
    GRANT ALL PRIVILEGES ON TABLES TO hospital_metrics_y1e8wgay;
ALTER DEFAULT PRIVILEGES IN SCHEMA hospital_metrics
    GRANT ALL PRIVILEGES ON SEQUENCES TO hospital_metrics_y1e8wgay;

-- Configure connection limits and security
ALTER USER hospital_metrics_y1e8wgay WITH CONNECTION LIMIT 100;
ALTER USER hospital_metrics_y1e8wgay SET statement_timeout = '30s';
ALTER USER hospital_metrics_y1e8wgay SET idle_in_transaction_session_timeout = '60s';

-- Force SSL connections for this user
ALTER USER hospital_metrics_y1e8wgay SET ssl = on;

-- Additional security settings
ALTER DATABASE hospital_metrics_prod_0900f37a SET ssl = on;
ALTER DATABASE hospital_metrics_prod_0900f37a SET statement_timeout = '30s';
ALTER DATABASE hospital_metrics_prod_0900f37a SET idle_in_transaction_session_timeout = '60s';

-- Create a read-only user for reporting (optional)
CREATE USER hospital_metrics_readonly WITH PASSWORD 'generate_different_secure_password';
GRANT CONNECT ON DATABASE hospital_metrics_prod_0900f37a TO hospital_metrics_readonly;
GRANT USAGE ON SCHEMA hospital_metrics TO hospital_metrics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA hospital_metrics TO hospital_metrics_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA hospital_metrics
    GRANT SELECT ON TABLES TO hospital_metrics_readonly;
