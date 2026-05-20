import pandas as pd
import json
import os
import msoffcrypto
import io

# Load DPR file
dpr_path = 'data/latest_dpr.xlsx'
password = os.environ['DPR_PASSWORD']

# Decrypt if needed
with open(dpr_path, 'rb') as f:
    office_file = msoffcrypto.OfficeFile(f)
    office_file.load_key(password=password)
    decrypted = io.BytesIO()
    office_file.decrypt(decrypted)
    decrypted.seek(0)
    df = pd.read_excel(decrypted, sheet_name='Production per Agent', header=None, skiprows=5)

print("✅ DPR file loaded and decrypted")

# Column mapping (v11)
df['AGENT_ID'] = df[1].astype(str).str.strip()
df['AGENT_NAME'] = df[2]
df['STATUS'] = df[4]
df['MAY_MTD'] = pd.to_numeric(df[13], errors='coerce').fillna(0)
df['MAY_CC'] = pd.to_numeric(df[14], errors='coerce').fillna(0)
df['YTD'] = pd.to_numeric(df[17], errors='coerce').fillna(0)
df['YTD_CC'] = pd.to_numeric(df[18], errors='coerce').fillna(0)
df['FWM'] = df[28]

# Filter active agents
df_agents = df[df['AGENT_ID'].str.match(r'^\d{8}$', na=False)].copy()
df_active = df_agents[df_agents['STATUS'] == 'ACTIVE'].copy()

# FWM to Team mapping
fwm_to_team = {
    'John Kirk Montano Grospe': 'Kirk',
    'John Paul Perido Mitra': 'JP',
    ' FWM - Direct - Ivan Arnaiz Lontoc': 'Ivan',
    'Alyssa Joyce Del Rosario Maningding': 'AJ',
    'Dianne Mae Tortosion Pestanas': 'Dianne',
    'Renelyn Desiree David Ramirez': 'Renz',
    'J R Seimone Montano Grospe': 'Sei',
    'Princess Diane De Guzman Cheng': 'PDC'
}

df_active['TEAM'] = df_active['FWM'].map(fwm_to_team)

# Calculate branch totals
branch_mtd = df_active['MAY_MTD'].sum()
branch_ytd = df_active['YTD'].sum()
active_count = len(df_active[df_active['MAY_MTD'] > 0])

# Team totals
team_data = df_active.groupby('TEAM').agg({
    'MAY_MTD': 'sum',
    'YTD': 'sum'
}).round(0).to_dict('index')

# Top producers
top_mtd = df_active.nlargest(10, 'MAY_MTD')[['AGENT_NAME', 'TEAM', 'MAY_MTD']].to_dict('records')
top_ytd = df_active.nlargest(20, 'YTD')[['AGENT_NAME', 'TEAM', 'YTD']].to_dict('records')

# Save extracted data
output_data = {
    'branch': {
        'mtd': float(branch_mtd),
        'ytd': float(branch_ytd),
        'active': int(active_count)
    },
    'teams': team_data,
    'top_mtd': top_mtd,
    'top_ytd': top_ytd
}

os.makedirs('data', exist_ok=True)
with open('data/dashboard_data.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("✅ Data extracted and saved to data/dashboard_data.json")
