import json
from datetime import datetime

# Load extracted data
with open('data/dashboard_data.json', 'r') as f:
    data = json.load(f)

# Load dashboard template
with open('dashboard_template.html', 'r') as f:
    html = f.read()

# Replace placeholders
html = html.replace('{{BRANCH_MTD}}', f"₱{data['branch']['mtd']:,.0f}")
html = html.replace('{{BRANCH_YTD}}', f"₱{data['branch']['ytd']:,.0f}")
html = html.replace('{{ACTIVE_COUNT}}', str(data['branch']['active']))
html = html.replace('{{UPDATE_DATE}}', datetime.now().strftime('%B %d, %Y'))

# Update team data (if template has team placeholders)
for team, values in data['teams'].items():
    html = html.replace(f'{{{{TEAM_{team.upper()}_MTD}}}}', f"₱{values['MAY_MTD']:,.0f}")
    html = html.replace(f'{{{{TEAM_{team.upper()}_YTD}}}}', f"₱{values['YTD']:,.0f}")

# Save updated dashboard
with open('index.html', 'w') as f:
    f.write(html)

print("✅ Dashboard updated successfully!")
print(f"   Branch MTD: ₱{data['branch']['mtd']:,.0f}")
print(f"   Branch YTD: ₱{data['branch']['ytd']:,.0f}")
print(f"   Active Producers: {data['branch']['active']}")
