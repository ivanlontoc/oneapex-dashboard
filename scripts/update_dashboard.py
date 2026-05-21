#!/usr/bin/env python3
"""
Update dashboard HTML with extracted data
"""
import json
import os
from datetime import datetime

print("=" * 60)
print("DASHBOARD HTML UPDATE - Starting")
print("=" * 60)

# Load dashboard data
print("\n[1/3] Loading dashboard data...")
try:
    with open('data/dashboard_data.json', 'r') as f:
        data = json.load(f)
    print("✓ Data loaded successfully")
except FileNotFoundError:
    print("✗ ERROR: dashboard_data.json not found!")
    print("The extraction script must have failed.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"✗ ERROR: Invalid JSON: {e}")
    exit(1)

# Load dashboard template
print("\n[2/3] Loading HTML template...")
try:
    with open('dashboard_template.html', 'r', encoding='utf-8') as f:
        template = f.read()
    print("✓ Template loaded successfully")
except FileNotFoundError:
    print("✗ ERROR: dashboard_template.html not found!")
    exit(1)

# Replace branch totals
print("\n[3/3] Replacing placeholders...")
template = template.replace('{{BRANCH_MTD}}', f"₱{data['branch_mtd']:,.2f}")
template = template.replace('{{BRANCH_YTD}}', f"₱{data['branch_ytd']:,.2f}")
template = template.replace('{{BRANCH_ACTIVE}}', str(data['branch_active']))
template = template.replace('{{BRANCH_MANPOWER}}', str(data['branch_manpower']))
template = template.replace('{{BRANCH_ACTIVITY_RATIO}}', f"{data['branch_activity_ratio']:.1f}%")

# Replace branch targets
template = template.replace('{{BRANCH_MONTHLY_TARGET}}', f"₱{data['branch_monthly_target']:,}")
template = template.replace('{{BRANCH_YTD_TARGET}}', f"₱{data['branch_ytd_target']:,}")
template = template.replace('{{CURRENT_MONTH}}', data['current_month'].upper())

# Replace team placeholders
for team, values in data['teams'].items():
    team_upper = team.upper()
    template = template.replace(f'{{{{{team_upper}_MTD}}}}', f"₱{values['mtd']:,.2f}")
    template = template.replace(f'{{{{{team_upper}_YTD}}}}', f"₱{values['ytd']:,.2f}")
    template = template.replace(f'{{{{{team_upper}_ACTIVE}}}}', str(values['active']))
    template = template.replace(f'{{{{{team_upper}_MANPOWER}}}}', str(values['manpower']))
    template = template.replace(f'{{{{{team_upper}_ACTIVITY}}}}', f"{values['activity_ratio']:.1f}%")
    template = template.replace(f'{{{{{team_upper}_MONTHLY_TARGET}}}}', f"₱{values['monthly_target']:,}")
    template = template.replace(f'{{{{{team_upper}_YTD_TARGET}}}}', f"₱{values['ytd_target']:,}")

# Generate Top Performers HTML
def generate_table_rows(performers, columns):
    """Generate HTML table rows for top performers"""
    if not performers:
        return "<tr><td colspan='5' style='text-align:center;padding:20px;color:#999;'>No data available</td></tr>"
    
    rows = ""
    for i, p in enumerate(performers, 1):
        row = f"<tr><td>{i}</td>"
        for col in columns:
            if col in p:
                if 'APE' in col:
                    row += f"<td>₱{p[col]:,.2f}</td>"
                elif 'CC' in col:
                    row += f"<td>{p[col]:.1f}</td>"
                elif col == 'Active_Recruits':
                    row += f"<td>{int(p[col])}</td>"
                else:
                    row += f"<td>{p[col]}</td>"
        row += "</tr>\n"
        rows += row
    return rows

# Replace top performers
template = template.replace('{{TOP_10_MTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_10_mtd'],
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
))

template = template.replace('{{TOP_20_YTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_20_ytd'],
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
))

template = template.replace('{{TOP_10_ROOKIES_MTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_10_rookies_mtd'],
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
))

template = template.replace('{{TOP_20_ROOKIES_YTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_20_rookies_ytd'],
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
))

template = template.replace('{{TOP_RECRUITERS_MTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_recruiters_mtd'],
    ['Recruiter_Name', 'Team', 'Recruits_MTD_APE', 'Active_Recruits']
))

template = template.replace('{{TOP_RECRUITERS_YTD_ROWS}}', generate_table_rows(
    data['top_performers']['top_recruiters_ytd'],
    ['Recruiter_Name', 'Team', 'Recruits_YTD_APE', 'Active_Recruits']
))

# Update timestamp
template = template.replace('{{UPDATE_DATE}}', data['update_timestamp'])

# Save as index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(template)

print("\n" + "=" * 60)
print("✓ HTML UPDATE COMPLETE")
print("=" * 60)
print(f"Month: {data['current_month']}")
print(f"Branch MTD: ₱{data['branch_mtd']:,.2f} / Target: ₱{data['branch_monthly_target']:,}")
print(f"Branch YTD: ₱{data['branch_ytd']:,.2f} / Target: ₱{data['branch_ytd_target']:,}")
print(f"Active: {data['branch_active']} / Manpower: {data['branch_manpower']}")
print(f"Output: index.html")
print("=" * 60)
