"""
Project: FieldOps Costing Engine
Author: Partner
Purpose: Calculate True Project P&L including billable plugins, product/service split, and billability rate.
"""

import pandas as pd
import math
from datetime import datetime, timedelta

# ============================================================
# CONFIGURATION (Adjust to your company's reality)
# ============================================================

BURDEN_RATE_PER_HOUR = 40.0       # $/hour (wages + benefits + overhead)
TRAVEL_COST_PER_KM = 0.65         # $/km
PLUGIN_MARKUP = 1.35              # 35% markup on billable plugins

# Standard hours for Base Modules (from our Business Model)
BASE_MODULES_STANDARD_HOURS = {
    'CCTV_Small': 4.0,
    'CCTV_Large': 8.0,
    'Shutter': 6.0,
    'Electric_Lock': 2.0,
    'Intercom': 3.0,
    'Alarm': 4.0,
}

# Standard hours for Plugins (from our Plugin Library)
PLUGINS_STANDARD_HOURS = {
    'P-DEMO': 1.5,
    'P-WELD': 2.0,
    'P-PATCH': 1.0,
    'P-CORE': 1.5,
    'P-REMOVE': 1.0,
    'P-RELOCATE': 1.5,
    'P-REWIRE': 3.0,
    'P-SCAFF': 2.0,
    'P-SHUTTLE': 2.0,
    'P-WAITING': 1.0,
    'P-HAUL': 1.5,
    'P-EWASTE': 0.5,
    'P-CLEAN': 0.5,
    'P-TRAIN': 1.0,
    'P-REVISIT': 1.5,
    'P-SURVEY': 1.0,
}


# ============================================================
# CORE COSTING FUNCTIONS
# ============================================================

def calculate_project_pll(project_data):
    """
    Calculate the complete P&L for a single project.
    
    Input:
        project_data (dict): {
            'project_id': 'P001',
            'base_module': 'CCTV_Small',
            'project_type': 'Installation',  # Installation / Repair / Warranty
            'quoted_product_revenue': 1040.0,
            'quoted_service_revenue': 213.0,
            'product_cogs': 850.0,
            'actual_total_labor_hours': 5.5,  # Sum of all tech hours logged
            'num_visits': 2,
            'distance_km': 25.0,
            'plugins': [  # List of plugin dictionaries
                {
                    'code': 'P-DEMO',
                    'actual_hours': 1.5,
                    'actual_material_cost': 0.0,
                    'billed_amount': 90.0,
                    'is_billable': True,
                    'original_project_id': None,  # If warranty claim, link to original
                },
                {
                    'code': 'P-WELD',
                    'actual_hours': 1.0,
                    'actual_material_cost': 20.0,
                    'billed_amount': 80.0,
                    'is_billable': True,
                    'original_project_id': None,
                }
            ],
            'deposit_date': '2025-01-10',
            'deposit_amount': 500.0,
            'final_payment_date': '2025-02-15',
            'final_payment_amount': 710.0,
        }
    
    Output:
        dict: Full P&L breakdown
    """
    
    # --- 1. Calculate Total Revenue ---
    base_service_revenue = project_data['quoted_service_revenue']
    plugin_revenue = sum([
        p['billed_amount'] for p in project_data['plugins'] 
        if p['is_billable'] and p.get('billed_amount', 0) > 0
    ])
    total_revenue = project_data['quoted_product_revenue'] + base_service_revenue + plugin_revenue
    
    # --- 2. Calculate Total Cost ---
    # 2a. Product Cost
    product_cost = project_data['product_cogs']
    
    # 2b. Base Labor Cost (using standard hours for the base module, not actual)
    #    Why? To compare estimate vs actual variance.
    standard_base_hours = BASE_MODULES_STANDARD_HOURS.get(project_data['base_module'], 0)
    base_labor_cost = standard_base_hours * BURDEN_RATE_PER_HOUR
    
    # 2c. Plugin Actual Cost (labor + materials + subcontractors)
    plugin_labor_cost = sum([
        p['actual_hours'] * BURDEN_RATE_PER_HOUR for p in project_data['plugins']
    ])
    plugin_material_cost = sum([
        p.get('actual_material_cost', 0) for p in project_data['plugins']
    ])
    plugin_subcontractor_cost = sum([
        p.get('subcontractor_cost', 0) for p in project_data['plugins']
    ])
    plugin_total_actual_cost = plugin_labor_cost + plugin_material_cost + plugin_subcontractor_cost
    
    # 2d. Travel Cost
    travel_cost = project_data['num_visits'] * project_data['distance_km'] * TRAVEL_COST_PER_KM
    
    # 2e. Total Cost
    total_cost = product_cost + base_labor_cost + plugin_total_actual_cost + travel_cost
    
    # --- 3. Calculate Profit & Margins ---
    gross_profit = total_revenue - total_cost
    gross_margin = (gross_profit / total_revenue) * 100 if total_revenue > 0 else 0
    
    # Product Margin (Tier 1)
    product_margin = ((project_data['quoted_product_revenue'] - product_cost) / project_data['quoted_product_revenue']) * 100 if project_data['quoted_product_revenue'] > 0 else 0
    
    # Service Margin (Tier 2)
    service_actual_cost = base_labor_cost + travel_cost
    service_revenue = base_service_revenue + plugin_revenue
    service_margin = ((service_revenue - service_actual_cost) / service_revenue) * 100 if service_revenue > 0 else 0
    
    # --- 4. Plugin Billability Rate (KPI) ---
    total_plugins = len(project_data['plugins'])
    billable_plugins = len([p for p in project_data['plugins'] if p.get('is_billable', False)])
    billability_rate = (billable_plugins / total_plugins) * 100 if total_plugins > 0 else 100.0
    
    # --- 5. Cash Flow Metrics ---
    deposit_date = project_data.get('deposit_date')
    final_payment_date = project_data.get('final_payment_date')
    days_to_collect = None
    if deposit_date and final_payment_date:
        if isinstance(deposit_date, str):
            deposit_date = datetime.strptime(deposit_date, '%Y-%m-%d')
        if isinstance(final_payment_date, str):
            final_payment_date = datetime.strptime(final_payment_date, '%Y-%m-%d')
        days_to_collect = (final_payment_date - deposit_date).days
    
    # --- 6. Estimate vs Actual Variance ---
    estimated_labor_cost = standard_base_hours * BURDEN_RATE_PER_HOUR
    actual_labor_cost = project_data.get('actual_total_labor_hours', 0) * BURDEN_RATE_PER_HOUR
    labor_variance = actual_labor_cost - estimated_labor_cost
    
    # --- Return Results ---
    return {
        'project_id': project_data['project_id'],
        
        # Revenue Breakdown
        'product_revenue': project_data['quoted_product_revenue'],
        'base_service_revenue': base_service_revenue,
        'plugin_revenue': plugin_revenue,
        'total_revenue': total_revenue,
        
        # Cost Breakdown
        'product_cost': product_cost,
        'base_labor_cost': base_labor_cost,
        'plugin_actual_cost': plugin_total_actual_cost,
        'plugin_labor_cost': plugin_labor_cost,
        'plugin_material_cost': plugin_material_cost,
        'plugin_subcontractor_cost': plugin_subcontractor_cost,
        'travel_cost': travel_cost,
        'total_cost': total_cost,
        
        # Profit & Margins
        'gross_profit': gross_profit,
        'gross_margin': gross_margin,
        'product_margin': product_margin,
        'service_margin': service_margin,
        
        # Plugin KPIs
        'total_plugins': total_plugins,
        'billable_plugins': billable_plugins,
        'billability_rate': billability_rate,
        
        # Cash Flow
        'deposit_amount': project_data.get('deposit_amount', 0),
        'final_payment_amount': project_data.get('final_payment_amount', 0),
        'days_to_collect': days_to_collect,
        
        # Variance
        'labor_variance': labor_variance,
        'labor_variance_percent': (labor_variance / estimated_labor_cost) * 100 if estimated_labor_cost > 0 else 0,
    }


# ============================================================
# BATCH PROCESSING FOR HISTORICAL PROJECTS
# ============================================================

def batch_analyze_projects(projects_data):
    """
    Run the costing engine on a list of projects and return a DataFrame.
    
    Input:
        projects_data (list of dicts): Each dict as per calculate_project_pll input.
    
    Output:
        pd.DataFrame: All P&L results with 2x2 grid classification.
    """
    results = []
    for proj in projects_data:
        result = calculate_project_pll(proj)
        
        # Add 2x2 Grid Classification
        margin = result['gross_margin']
        billability = result['billability_rate']
        
        if margin >= 20 and billability >= 90:
            quadrant = "🏆 Premium Integrator"
        elif margin >= 20 and billability < 90:
            quadrant = "⚠️ Leaking Gold (High Base Margin, Low Billability)"
        elif margin < 20 and billability >= 90:
            quadrant = "📈 Strategy Project (Low Base, Saved by Plugins)"
        else:
            quadrant = "💀 Disaster Project (Low Base + Low Billability)"
        
        result['quadrant'] = quadrant
        result['is_profitable'] = margin >= 0
        results.append(result)
    
    return pd.DataFrame(results)


# ============================================================
# DEMO / TESTING
# ============================================================

if __name__ == "__main__":
    
    # Sample Project 1: Healthy Installation with billable plugins
    project_1 = {
        'project_id': 'P001',
        'base_module': 'CCTV_Small',
        'project_type': 'Installation',
        'quoted_product_revenue': 1040.0,
        'quoted_service_revenue': 213.0,
        'product_cogs': 850.0,
        'actual_total_labor_hours': 5.5,
        'num_visits': 2,
        'distance_km': 25.0,
        'plugins': [
            {'code': 'P-DEMO', 'actual_hours': 1.5, 'actual_material_cost': 0.0, 'billed_amount': 90.0, 'is_billable': True, 'subcontractor_cost': 0.0},
            {'code': 'P-WELD', 'actual_hours': 1.0, 'actual_material_cost': 20.0, 'billed_amount': 80.0, 'is_billable': True, 'subcontractor_cost': 0.0},
        ],
        'deposit_date': '2025-01-10',
        'deposit_amount': 500.0,
        'final_payment_date': '2025-02-15',
        'final_payment_amount': 710.0,
    }
    
    # Sample Project 2: Disaster - Unbillable plugins, low margin
    project_2 = {
        'project_id': 'P002',
        'base_module': 'Shutter',
        'project_type': 'Installation',
        'quoted_product_revenue': 2200.0,
        'quoted_service_revenue': 450.0,
        'product_cogs': 1600.0,
        'actual_total_labor_hours': 9.0,
        'num_visits': 3,
        'distance_km': 40.0,
        'plugins': [
            {'code': 'P-CORE', 'actual_hours': 2.0, 'actual_material_cost': 30.0, 'billed_amount': 0.0, 'is_billable': False, 'subcontractor_cost': 0.0},  # Warranty / forgot to bill
            {'code': 'P-REMOVE', 'actual_hours': 1.5, 'actual_material_cost': 0.0, 'billed_amount': 0.0, 'is_billable': False, 'subcontractor_cost': 0.0},
        ],
        'deposit_date': '2025-01-15',
        'deposit_amount': 600.0,
        'final_payment_date': '2025-03-01',
        'final_payment_amount': 550.0,
    }
    
    # Run batch analysis
    projects_list = [project_1, project_2]
    df_results = batch_analyze_projects(projects_list)
    
    print("=" * 80)
    print("PROJECT P&L ANALYSIS")
    print("=" * 80)
    
    # Display selected columns
    display_cols = ['project_id', 'total_revenue', 'total_cost', 'gross_profit', 'gross_margin', 
                    'product_margin', 'service_margin', 'billability_rate', 'quadrant', 'days_to_collect']
    print(df_results[display_cols].to_string(index=False))
    
    print("\n" + "=" * 80)
    print("2x2 GRID SUMMARY")
    print("=" * 80)
    print(df_results.groupby('quadrant').size().to_string())
    
    print("\n" + "=" * 80)
    print("KEY FINDINGS")
    print("=" * 80)
    print(f"Average Gross Margin: {df_results['gross_margin'].mean():.1f}%")
    print(f"Average Billability Rate: {df_results['billability_rate'].mean():.1f}%")
    print(f"Profitable Projects: {df_results['is_profitable'].sum()} / {len(df_results)}")