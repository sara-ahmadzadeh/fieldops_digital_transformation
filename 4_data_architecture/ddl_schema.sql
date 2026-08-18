-- ============================================================
-- DATABASE SCHEMA: FieldOps Digital Transformation
-- PostgreSQL / MySQL Compatible
-- ============================================================

-- 1. CUSTOMERS TABLE
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    segment VARCHAR(50) CHECK (segment IN ('Residential', 'Commercial', 'Industrial', 'Government')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. PROJECTS TABLE (Master Record)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_code VARCHAR(20) UNIQUE NOT NULL,
    customer_id UUID NOT NULL REFERENCES customers(id),
    
    -- Classification
    base_module VARCHAR(50) CHECK (base_module IN ('CCTV_Small', 'CCTV_Large', 'Shutter', 'Electric_Lock', 'Intercom', 'Alarm')),
    project_type VARCHAR(20) CHECK (project_type IN ('Installation', 'Repair', 'Warranty')),
    
    -- Financials (Quoted / Estimated)
    quoted_product_revenue DECIMAL(12,2) NOT NULL,  -- Price of hardware sold
    quoted_service_revenue DECIMAL(12,2) NOT NULL,  -- Price of labor/travel quoted
    product_cogs DECIMAL(12,2) NOT NULL,            -- Cost of Goods Sold (what we paid)
    
    -- Actuals (Calculated after project closes)
    actual_total_cost DECIMAL(12,2),                 -- Calculated: Labor + Travel + Plugins Actual
    actual_total_revenue DECIMAL(12,2),              -- Calculated: Quoted + Plugin Billings
    gross_profit DECIMAL(12,2),                      -- Calculated: Revenue - Cost
    gross_margin DECIMAL(5,2),                       -- Calculated: (Profit / Revenue) * 100
    
    -- Deposit & Payment Tracking
    deposit_received_date DATE,
    deposit_amount DECIMAL(12,2),
    invoice_sent_date DATE,
    final_payment_received_date DATE,
    final_payment_amount DECIMAL(12,2),
    
    -- Metadata
    status VARCHAR(20) CHECK (status IN ('Quote', 'Survey', 'Active', 'Testing', 'Closed', 'Warranty')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

-- 3. SITE SURVEYS TABLE
CREATE TABLE site_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    
    -- Site Conditions (Triggers for plugins)
    wall_structure VARCHAR(30) CHECK (wall_structure IN ('Drywall', 'Brick', 'Reinforced_Concrete', 'Steel_Girder')),
    ceiling_height DECIMAL(4,2),  -- meters
    access_restriction VARCHAR(30) CHECK (access_restriction IN ('Open', 'Key_Required', 'Security_Clearance', 'After_Hours')),
    existing_infrastructure VARCHAR(30) CHECK (existing_infrastructure IN ('Modern_Wiring', 'Old_No_Neutral', 'No_Power', 'Unstable_WiFi')),
    debris_responsibility VARCHAR(30) CHECK (debris_responsibility IN ('Client_Provides_Skip', 'Company_Must_Haul')),
    
    survey_date DATE NOT NULL,
    technician_notes TEXT
);

-- 4. ACTIVITIES LOG (Technician Time Tracking)
CREATE TABLE activities_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    technician_name VARCHAR(100) NOT NULL,
    
    -- Time Tracking
    activity_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    total_hours DECIMAL(4,2) GENERATED ALWAYS AS (EXTRACT(EPOCH FROM (end_time - start_time)) / 3600) STORED,
    
    -- Layer Classification (1-5)
    layer_id INT CHECK (layer_id BETWEEN 1 AND 5),
    is_rework BOOLEAN DEFAULT FALSE,
    
    -- Travel
    visit_number INT,
    distance_km DECIMAL(6,2),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. PLUGINS CATALOG (Master Reference)
CREATE TABLE plugins_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plugin_code VARCHAR(20) UNIQUE NOT NULL,
    plugin_name_fa VARCHAR(100) NOT NULL,
    category VARCHAR(50) CHECK (category IN ('Structural', 'Electrical', 'Logistics', 'Disposal', 'Human')),
    standard_extra_hours DECIMAL(4,2) NOT NULL,
    required_tool VARCHAR(100),
    consumable_cost DECIMAL(10,2) DEFAULT 0
);

-- 6. PROJECT PLUGINS (Junction Table - Actual Occurrences)
CREATE TABLE project_plugins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    plugin_id UUID NOT NULL REFERENCES plugins_catalog(id),
    
    -- Actual Execution
    actual_duration DECIMAL(4,2) NOT NULL,  -- Actual hours spent
    actual_material_cost DECIMAL(10,2) DEFAULT 0,
    subcontractor_cost DECIMAL(10,2) DEFAULT 0,
    
    -- Billing
    billed_amount DECIMAL(12,2),             -- What we charged the client (NULL if not billed)
    is_billable BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Reference to original project if this is a warranty claim
    original_project_id UUID REFERENCES projects(id),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. MATERIALS CONSUMPTION
CREATE TABLE materials_consumed (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    product_name VARCHAR(200) NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED,
    is_warranty_replacement BOOLEAN DEFAULT FALSE,
    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. INVOICES & PAYMENTS
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    invoice_number VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    paid_amount DECIMAL(12,2) DEFAULT 0,
    balance_due DECIMAL(12,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    payment_status VARCHAR(20) CHECK (payment_status IN ('Unpaid', 'Partial', 'Paid', 'Overdue')),
    due_date DATE,
    paid_at DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_projects_customer ON projects(customer_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_dates ON projects(created_at, closed_at);
CREATE INDEX idx_activities_project ON activities_log(project_id);
CREATE INDEX idx_project_plugins_project ON project_plugins(project_id);
CREATE INDEX idx_materials_project ON materials_consumed(project_id);
CREATE INDEX idx_invoices_project ON invoices(project_id);

-- ============================================================
-- SAMPLE DATA INSERTS (For testing)
-- ============================================================
-- See /sample_data/ folder for mock data scripts.