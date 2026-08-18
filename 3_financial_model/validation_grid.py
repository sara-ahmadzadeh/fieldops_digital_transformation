"""
Validation Grid: 2x2 Profitability vs. Billability Matrix
File: validation_grid.py
Purpose: Plot historical projects on the 2x2 grid to identify patterns.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_2x2_grid(df_results, output_file='2x2_grid.png'):
    """
    Generate the 2x2 grid visualization.
    
    Input:
        df_results: DataFrame from batch_analyze_projects()
        output_file: Path to save the image.
    """
    
    # Define quadrant boundaries
    margin_threshold = 20  # 20% Gross Margin
    billability_threshold = 90  # 90% Billability Rate
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    colors = {
        '🏆 Premium Integrator': 'green',
        '⚠️ Leaking Gold': 'orange',
        '📈 Strategy Project': 'blue',
        '💀 Disaster Project': 'red'
    }
    
    for quadrant, color in colors.items():
        subset = df_results[df_results['quadrant'] == quadrant]
        ax.scatter(subset['billability_rate'], subset['gross_margin'], 
                   color=color, label=quadrant, s=100, alpha=0.7, edgecolors='black')
    
    # Add quadrant lines
    ax.axvline(x=billability_threshold, color='black', linestyle='--', alpha=0.5)
    ax.axhline(y=margin_threshold, color='black', linestyle='--', alpha=0.5)
    
    # Labels
    ax.set_xlabel('Plugin Billability Rate (%)', fontsize=12)
    ax.set_ylabel('Gross Margin (%)', fontsize=12)
    ax.set_title('2x2 Profitability Grid', fontsize=16)
    
    # Quadrant annotations
    ax.text(95, 35, '🏆 Premium Integrator', fontsize=10, ha='center', va='center', 
            bbox=dict(facecolor='lightgreen', alpha=0.3))
    ax.text(80, 35, '⚠️ Leaking Gold', fontsize=10, ha='center', va='center',
            bbox=dict(facecolor='lightyellow', alpha=0.3))
    ax.text(95, 10, '📈 Strategy Project', fontsize=10, ha='center', va='center',
            bbox=dict(facecolor='lightblue', alpha=0.3))
    ax.text(80, 10, '💀 Disaster Project', fontsize=10, ha='center', va='center',
            bbox=dict(facecolor='lightcoral', alpha=0.3))
    
    # Axis limits
    ax.set_xlim(50, 105)
    ax.set_ylim(-10, 50)
    
    # Grid and legend
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.show()
    
    print(f"✅ 2x2 Grid saved to: {output_file}")
    
    # Print summary statistics
    print("\n" + "=" * 60)
    print("PROJECT DISTRIBUTION BY QUADRANT")
    print("=" * 60)
    print(df_results['quadrant'].value_counts().to_string())
    print("\n" + "=" * 60)


def generate_findings_report(df_results):
    """
    Generate a plain-English findings report.
    """
    avg_margin = df_results['gross_margin'].mean()
    avg_billability = df_results['billability_rate'].mean()
    profitable_count = df_results['is_profitable'].sum()
    total_count = len(df_results)
    
    print("\n" + "=" * 60)
    print("FINDINGS REPORT")
    print("=" * 60)
    print(f"📊 Average Gross Margin: {avg_margin:.1f}%")
    print(f"📊 Average Billability Rate: {avg_billability:.1f}%")
    print(f"📊 Profitable Projects: {profitable_count} / {total_count} ({profitable_count/total_count*100:.0f}%)")
    
    # Identify problem quadrant
    problem_count = len(df_results[df_results['quadrant'] == '💀 Disaster Project'])
    if problem_count > 0:
        print(f"\n⚠️ Alert: {problem_count} projects are in the 'Disaster' quadrant.")
        print("   These projects have low margin AND low billability.")
        print("   Recommendation: Review these projects to identify root causes.")
    
    # Identify leakage
    leakage_count = len(df_results[df_results['quadrant'] == '⚠️ Leaking Gold'])
    if leakage_count > 0:
        print(f"\n💰 Opportunity: {leakage_count} projects have high margin but low billability.")
        print("   Recommendation: Train technicians to always issue change orders for extra work.")
    
    print("\n" + "=" * 60)


# ============================================================
# EXAMPLE USAGE
# ============================================================

if __name__ == "__main__":
    
    # Load your historical projects from CSV or Excel
    # df = pd.read_csv('historical_projects.csv')
    
    # Or use the sample data from earlier (simulated)
    from costing_engine import batch_analyze_projects
    
    # Sample data (replace with your actual data extraction)
    sample_projects = [
        {
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
        },
        # Add more projects...
    ]
    
    df_results = batch_analyze_projects(sample_projects)
    
    # Generate the 2x2 grid
    generate_2x2_grid(df_results, '2x2_grid.png')
    
    # Generate findings report
    generate_findings_report(df_results)