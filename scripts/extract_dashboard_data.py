#!/usr/bin/env python3
"""
Extract dashboard data from DPR with Business Plan 2026 targets
"""
import pandas as pd
import msoffcrypto
import io
import os
import json
from datetime import datetime

print("=" * 60)
print("DASHBOARD DATA EXTRACTION - Starting")
print("=" * 60)

# Business Plan 2026 Targets
BUSINESS_PLAN_2026 = {
    'branch': {
        'monthly_targets': {
            'January': 3897736, 'February': 3897736, 'March': 3897736, 'April': 3897736,
            'May': 5242736, 'June': 5242736, 'July': 5242736, 'August': 5242736,
            'September': 5242736, 'October': 5242736, 'November': 5242736, 'December': 5242736
        },
        'ytd_targets': {
            'January': 3897736, 'February': 7795472, 'March': 11693208, 'April': 15590944,
            'May': 19005964, 'June': 25248700, 'July': 30491436, 'August': 35734172,
            'September': 40976908, 'October': 46219644, 'November': 51462380, 'December': 56705116
        }
    },
    'teams': {
        'Kirk': {
            'monthly': 1483000,
            'ytd': {'January': 1483000, 'February': 2966000, 'March': 4449000, 'April': 5932000,
                    'May': 5386875, 'June': 8898000, 'July': 10381000, 'August': 11864000,
                    'September': 13347000, 'October': 14830000, 'November': 16313000, 'December': 17796000}
        },
        'Ivan': {
            'monthly': 585000,
            'ytd': {'January': 585000, 'February': 1170000, 'March': 1755000, 'April': 2340000,
                    'May': 2128125, 'June': 3510000, 'July': 4095000, 'August': 4680000,
                    'September': 5265000, 'October': 5850000, 'November': 6435000, 'December': 7020000}
        },
        'Renz': {
            'monthly': 614400,
            'ytd': {'January': 614400, 'February': 1228800, 'March': 1843200, 'April': 2457600,
                    'May': 2750379, 'June': 3686400, 'July': 4300800, 'August': 4915200,
                    'September': 5529600, 'October': 6144000, 'November': 6758400, 'December': 7372800}
        },
        'Dianne': {
            'monthly': 726192,
            'ytd': {'January': 726192, 'February': 1452384, 'March': 2178576, 'April': 2904768,
                    'May': 2110339, 'June': 4357152, 'July': 5083344, 'August': 5809536,
                    'September': 6535728, 'October': 7261920, 'November': 7988112, 'December': 8714304}
        },
        'Sei': {
            'monthly': 686144,
            'ytd': {'January': 686144, 'February': 1372288, 'March': 2058432, 'April': 2744576,
                    'May': 2496763, 'June': 4117008, 'July': 4803152, 'August': 5489296,
                    'September': 6175440, 'October': 6861584, 'November': 7547728, 'December': 8233872}
        },
        'JP': {
            'monthly': 559000,
            'ytd': {'January': 559000, 'February': 1118000, 'March': 1677000, 'April': 2236000,
                    'May': 2032750, 'June': 3354000, 'July': 3913000, 'August': 4472000,
                    'September': 5031000, 'October': 5590000, 'November': 6149000, 'December': 6708000}
        },
        'AJ': {
            'monthly': 504000,
            'ytd': {'January': 504000, 'February': 1008000, 'March': 1512000, 'April': 2016000,
                    'May': 1833000, 'June': 3024000, 'July': 3528000, 'August': 4032000,
                    'September': 4536000, 'October': 5040000, 'November': 5544000, 'December': 6048000}
        },
        'PDC': {
            'monthly': 585000,
            'ytd': {'January': 585000, 'February': 1170000, 'March': 1755000, 'April': 2340000,
                    'May': 2128125, 'June': 3510000, 'July': 4095000, 'August': 4680000,
                    'September': 5265000, 'October': 5850000, 'November': 6435000, 'December': 7020000}
        }
    }
}

# Get current month
current_month = datetime.now().strftime('%B')
print(f"Current month: {current_month}")

# Get password from environment
password = os.environ.get('DPR_PASSWORD')
if not password:
    raise ValueError("Missing DPR_PASSWORD environment variable")

# Decrypt the DPR file
print("\n[1/6] Decrypting DPR file...")
encrypted_file = open('data/latest_dpr.xlsx', 'rb')
decrypted = io.BytesIO()

file = msoffcrypto.OfficeFile(encrypted_file)
file.load_key(password=password)
file.decrypt(decrypted)
encrypted_file.close()
print("✓ Decryption successful")

# Load Production per Agent
print("\n[2/6] Loading Production per Agent sheet...")
df = pd.read_excel(decrypted, sheet_name='Production per Agent', header=None, skiprows=5)
print(f"✓ Loaded {len(df)} rows")

# Load Details Coded for rookies/recruiters
print("\n[3/6] Loading Details Coded sheet...")
decrypted.seek(0)
try:
    df_meridien = pd.read_excel(decrypted, sheet_name='Details Coded', header=None, skiprows=5)
    meridien_available = True
    print(f"✓ Loaded {len(df_meridien)} rows")
except Exception as e:
    print(f"⚠ Details Coded sheet not found: {e}")
    meridien_available = False

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

# Filter active agents
print("\n[4/6] Processing agent data...")
df_filtered = df[
    (df.iloc[:, 3] == 'ACTIVE') &
    (df.iloc[:, 0].astype(str).str.match(r'^\d{8}$'))
].copy()

df_filtered['Agent_ID'] = df_filtered.iloc[:, 0].astype(str)
df_filtered['Agent_Name'] = df_filtered.iloc[:, 1]
df_filtered['MTD_APE'] = pd.to_numeric(df_filtered.iloc[:, 12], errors='coerce').fillna(0)
df_filtered['MTD_CC'] = pd.to_numeric(df_filtered.iloc[:, 13], errors='coerce').fillna(0)
df_filtered['YTD_APE'] = pd.to_numeric(df_filtered.iloc[:, 16], errors='coerce').fillna(0)
df_filtered['YTD_CC'] = pd.to_numeric(df_filtered.iloc[:, 17], errors='coerce').fillna(0)
df_filtered['FWM'] = df_filtered.iloc[:, 27]
df_filtered['Team'] = df_filtered['FWM'].map(fwm_to_team)

print(f"✓ Filtered to {len(df_filtered)} active agents")

# Identify rookies
if meridien_available:
    df_meridien_filtered = df_meridien[
        df_meridien.iloc[:, 1].astype(str).str.match(r'^\d{8}$', na=False)
    ].copy()
    
    df_meridien_filtered['Agent_ID'] = df_meridien_filtered.iloc[:, 1].astype(str)
    df_meridien_filtered['Coding_Date'] = pd.to_datetime(df_meridien_filtered.iloc[:, 16], errors='coerce')
    df_meridien_filtered['Recruiter_ID'] = df_meridien_filtered.iloc[:, 3].astype(str)
    df_meridien_filtered['Is_Rookie'] = df_meridien_filtered['Coding_Date'].dt.year >= 2025
    
    df_filtered = df_filtered.merge(
        df_meridien_filtered[['Agent_ID', 'Is_Rookie', 'Recruiter_ID']], 
        on='Agent_ID', 
        how='left'
    )
    df_filtered['Is_Rookie'] = df_filtered['Is_Rookie'].fillna(False)
else:
    df_filtered['Is_Rookie'] = False
    df_filtered['Recruiter_ID'] = None

# Calculate metrics
print("\n[5/6] Calculating metrics...")
branch_mtd = df_filtered['MTD_APE'].sum()
branch_ytd = df_filtered['YTD_APE'].sum()
active_producers = len(df_filtered[df_filtered['MTD_APE'] > 0])
total_manpower = len(df_filtered)
activity_ratio = (active_producers / total_manpower * 100) if total_manpower > 0 else 0

branch_monthly_target = BUSINESS_PLAN_2026['branch']['monthly_targets'].get(current_month, 0)
branch_ytd_target = BUSINESS_PLAN_2026['branch']['ytd_targets'].get(current_month, 0)

# Team metrics
team_metrics = {}
for team in df_filtered['Team'].dropna().unique():
    team_df = df_filtered[df_filtered['Team'] == team]
    team_active = len(team_df[team_df['MTD_APE'] > 0])
    team_manpower = len(team_df)
    team_activity = (team_active / team_manpower * 100) if team_manpower > 0 else 0
    
    team_monthly_target = BUSINESS_PLAN_2026['teams'][team]['monthly']
    team_ytd_target = BUSINESS_PLAN_2026['teams'][team]['ytd'].get(current_month, 0)
    
    team_metrics[team] = {
        'mtd': round(team_df['MTD_APE'].sum(), 2),
        'ytd': round(team_df['YTD_APE'].sum(), 2),
        'active': team_active,
        'manpower': team_manpower,
        'activity_ratio': round(team_activity, 1),
        'monthly_target': team_monthly_target,
        'ytd_target': team_ytd_target
    }

# Top Performers
top_10_mtd = df_filtered[df_filtered['MTD_APE'] > 0].nlargest(10, 'MTD_APE')[
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
].to_dict('records')

top_20_ytd = df_filtered[df_filtered['YTD_APE'] > 0].nlargest(20, 'YTD_APE')[
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
].to_dict('records')

df_rookies = df_filtered[df_filtered['Is_Rookie'] == True]
top_10_rookies_mtd = df_rookies[df_rookies['MTD_APE'] > 0].nlargest(10, 'MTD_APE')[
    ['Agent_Name', 'Team', 'MTD_APE', 'MTD_CC']
].to_dict('records')

top_20_rookies_ytd = df_rookies[df_rookies['YTD_APE'] > 0].nlargest(20, 'YTD_APE')[
    ['Agent_Name', 'Team', 'YTD_APE', 'YTD_CC']
].to_dict('records')

# Top Recruiters
if meridien_available and 'Recruiter_ID' in df_filtered.columns:
    recruits_mtd = df_filtered[df_filtered['MTD_APE'] > 0].copy()
    recruiter_mtd = recruits_mtd.groupby('Recruiter_ID').agg({
        'MTD_APE': 'sum',
        'Agent_ID': 'count'
    }).reset_index()
    recruiter_mtd.columns = ['Recruiter_ID', 'Recruits_MTD_APE', 'Active_Recruits']
    
    agent_id_to_name = df_filtered.set_index('Agent_ID')['Agent_Name'].to_dict()
    recruiter_mtd['Recruiter_Name'] = recruiter_mtd['Recruiter_ID'].map(agent_id_to_name)
    
    agent_id_to_team = df_filtered.set_index('Agent_ID')['Team'].to_dict()
    recruiter_mtd['Team'] = recruiter_mtd['Recruiter_ID'].map(agent_id_to_team)
    
    top_recruiters_mtd = recruiter_mtd[recruiter_mtd['Recruits_MTD_APE'] > 0].nlargest(10, 'Recruits_MTD_APE')[
        ['Recruiter_Name', 'Team', 'Recruits_MTD_APE', 'Active_Recruits']
    ].to_dict('records')
    
    recruits_ytd = df_filtered[df_filtered['YTD_APE'] > 0].copy()
    recruiter_ytd = recruits_ytd.groupby('Recruiter_ID').agg({
        'YTD_APE': 'sum',
        'Agent_ID': 'count'
    }).reset_index()
    recruiter_ytd.columns = ['Recruiter_ID', 'Recruits_YTD_APE', 'Active_Recruits']
    recruiter_ytd['Recruiter_Name'] = recruiter_ytd['Recruiter_ID'].map(agent_id_to_name)
    recruiter_ytd['Team'] = recruiter_ytd['Recruiter_ID'].map(agent_id_to_team)
    
    top_recruiters_ytd = recruiter_ytd[recruiter_ytd['Recruits_YTD_APE'] > 0].nlargest(10, 'Recruits_YTD_APE')[
        ['Recruiter_Name', 'Team', 'Recruits_YTD_APE', 'Active_Recruits']
    ].to_dict('records')
else:
    top_recruiters_mtd = []
    top_recruiters_ytd = []

# Create output JSON
output_data = {
    'branch_mtd': round(branch_mtd, 2),
    'branch_ytd': round(branch_ytd, 2),
    'branch_active': active_producers,
    'branch_manpower': total_manpower,
    'branch_activity_ratio': round(activity_ratio, 1),
    'branch_monthly_target': branch_monthly_target,
    'branch_ytd_target': branch_ytd_target,
    'current_month': current_month,
    'teams': team_metrics,
    'top_performers': {
        'top_10_mtd': top_10_mtd,
        'top_20_ytd': top_20_ytd,
        'top_10_rookies_mtd': top_10_rookies_mtd,
        'top_20_rookies_ytd': top_20_rookies_ytd,
        'top_recruiters_mtd': top_recruiters_mtd,
        'top_recruiters_ytd': top_recruiters_ytd
    },
    'update_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
}

# Save to JSON
print("\n[6/6] Saving data...")
os.makedirs('data', exist_ok=True)
with open('data/dashboard_data.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("\n" + "=" * 60)
print("✓ EXTRACTION COMPLETE")
print("=" * 60)
print(f"Month: {current_month}")
print(f"Branch MTD: ₱{branch_mtd:,.2f} / Target: ₱{branch_monthly_target:,}")
print(f"Branch YTD: ₱{branch_ytd:,.2f} / Target: ₱{branch_ytd_target:,}")
print(f"Active: {active_producers} / Manpower: {total_manpower} / Activity: {activity_ratio:.1f}%")
print(f"Teams processed: {len(team_metrics)}")
print(f"Top performers: {len(top_10_mtd)} MTD, {len(top_20_ytd)} YTD")
print("=" * 60)
