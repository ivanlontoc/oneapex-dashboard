import json
from datetime import datetime

# Load dashboard data
with open('data/dashboard_data.json', 'r') as f:
    data = json.load(f)

# Load dashboard template
with open('dashboard_template.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Replace branch totals
template = template.replace('{{BRANCH_MTD}}', f"₱{data['branch_mtd']:,.2f}")
template = template.replace('{{BRANCH_YTD}}', f"₱{data['branch_ytd']:,.2f}")
template = template.replace('{{BRANCH_ACTIVE}}', str(data['branch_active']))
template = template.replace('{{BRANCH_MANPOWER}}', str(data['branch_manpower']))
template = template.replace('{{BRANCH_ACTIVITY_RATIO}}', f"{data['branch_activity_ratio']:.1f}%")

# Replace branch targets (NEW - dynamic targets)
template = template.replace('{{BRANCH_MONTHLY_TARGET}}', f"₱{data['branch_monthly_target']:,}")
template = template.replace('{{BRANCH_YTD_TARGET}}', f"₱{data['branch_ytd_target']:,}")
template = template.replace('{{CURRENT_MONTH}}', data['current_month'])

# Replace team placeholders
for team, values in data['teams'].items():
    team_upper = team.upper()
    template = template.replace(f'{{{{{team_upper}_MTD}}}}', f"₱{values['mtd']:,.2f}")
    template = template.replace(f'{{{{{team_upper}_YTD}}}}', f"₱{values['ytd']:,.2f}")
    template = template.replace(f'{{{{{team_upper}_ACTIVE}}}}', str(values['active']))
    template = template.replace(f'{{{{{team_upper}_MANPOWER}}}}', str(values['manpower']))
    template = template.replace(f'{{{{{team_upper}_ACTIVITY}}}}', f"{values['activity_ratio']:.1f}%")
    
    # Replace team targets (NEW - dynamic targets)
    template = template.replace(f'{{{{{team_upper}_MONTHLY_TARGET}}}}', f"₱{values['monthly_target']:,}")
    template = template.replace(f'{{{{{team_upper}_YTD_TARGET}}}}', f"₱{values['ytd_target']:,}")

# Generate Top Performers HTML
def generate_table_rows(performers, columns):
    """Generate HTML table rows for top performers"""
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
        row += "</tr>"
        rows += row
    return rows if rows else "<tr><td colspan='10' style='text-align:center;'>No data available</td></tr>"

# Top 10 MTD
top_10_mtd_rows = generate_table_rows(
    data['top_performers']['top_10_mtd'],
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
)
template = template.replace('{{TOP_10_MTD_ROWS}}', top_10_mtd_rows)

# Top 20 YTD
top_20_ytd_rows = generate_table_rows(
    data['top_performers']['top_20_ytd'],
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
)
template = template.replace('{{TOP_20_YTD_ROWS}}', top_20_ytd_rows)

# Top 10 Rookies MTD
top_10_rookies_mtd_rows = generate_table_rows(
    data['top_performers']['top_10_rookies_mtd'],
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
)
template = template.replace('{{TOP_10_ROOKIES_MTD_ROWS}}', top_10_rookies_mtd_rows)

# Top 20 Rookies YTD
top_20_rookies_ytd_rows = generate_table_rows(
    data['top_performers']['top_20_rookies_ytd'],
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
)
template = template.replace('{{TOP_20_ROOKIES_YTD_ROWS}}', top_20_rookies_ytd_rows)

# Top Recruiters MTD
top_recruiters_mtd_rows = generate_table_rows(
    data['top_performers']['top_recruiters_mtd'],
    ['Recruiter_Name', 'Team', 'Recruits_MTD_APE', 'Active_Recruits']
)
template = template.replace('{{TOP_RECRUITERS_MTD_ROWS}}', top_recruiters_mtd_rows)

# Top Recruiters YTD
top_recruiters_ytd_rows = generate_table_rows(
    data['top_performers']['top_recruiters_ytd'],
    ['Recruiter_Name', 'Team', 'Recruits_YTD_APE', 'Active_Recruits']
)
template = template.replace('{{TOP_RECRUITERS_YTD_ROWS}}', top_recruiters_ytd_rows)

# Update timestamp
template = template.replace('{{UPDATE_DATE}}', data['update_timestamp'])

# Save as index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(template)

print("Dashboard HTML updated successfully!")
print(f"Current Month: {data['current_month']}")
print(f"Branch metrics:")
print(f"  - MTD: ₱{data['branch_mtd']:,.2f} / Target: ₱{data['branch_monthly_target']:,}")
print(f"  - YTD: ₱{data['branch_ytd']:,.2f} / Target: ₱{data['branch_ytd_target']:,}")
print(f"  - Active: {data['branch_active']}")
print(f"  - Manpower: {data['branch_manpower']}")
print(f"  - Activity: {data['branch_activity_ratio']:.1f}%")
print(f"Top Performers sections generated:")
print(f"  - Top 10 MTD: {len(data['top_performers']['top_10_mtd'])} producers")
print(f"  - Top 20 YTD: {len(data['top_performers']['top_20_ytd'])} producers")
