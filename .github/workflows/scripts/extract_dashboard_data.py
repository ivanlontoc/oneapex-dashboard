#!/usr/bin/env python3
"""
Extract Dashboard Data from DPR
================================

Extracts all necessary data from the DPR and saves to JSON for dashboard generation.
"""

import pandas as pd
import msoffcrypto
import io
import json
import os
from datetime import datetime

# Configuration
DPR_FILE = 'latest_dpr.xlsx'
DPR_PASSWORD = os.environ.get('DPR_PASSWORD', '1003304119940326')
OUTPUT_FILE = 'data/dashboard_data.json'

# FWM to Team mapping (v11)
FWM_TO_TEAM = {
    'John Kirk Montano Grospe': 'Kirk',
    'John Paul Perido Mitra': 'JP',
    ' FWM - Direct - Ivan Arnaiz Lontoc': 'Ivan',
    'Alyssa Joyce Del Rosario Maningding': 'AJ',
    'Dianne Mae Tortosion Pestanas': 'Dianne',
    'Renelyn Desiree David Ramirez': 'Renz',
    'J R Seimone Montano Grospe': 'Sei',
    'Princess Diane De Guzman Cheng': 'PDC'
}

# Business Plan 2026 Targets
TEAM_BP_MAY = {
    'Ivan': 456000, 'Kirk': 672000, 'AJ': 675000, 'JP': 828000,
    'Renz': 614400, 'Dianne': 726192, 'Sei': 686144, 'PDC': 585000
}

TEAM_BP_YTD = {
    'Kirk': 3224516, 'Ivan': 1618065, 'Sei': 2216633, 'JP': 3010065,
    'AJ': 3115161, 'Dianne': 2110339, 'Renz': 2750379, 'PDC': 960806
}

BP_BRANCH_MAY = 5242736
BP_BRANCH_YTD = 19005964


def load_dpr(dpr_path, password):
    """Load and decrypt DPR file."""
    print(f"📂 Loading DPR: {dpr_path}")
    
    with open(dpr_path, 'rb') as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=password)
        decrypted = io.BytesIO()
        office_file.decrypt(decrypted)
        decrypted.seek(0)
        df = pd.read_excel(decrypted, sheet_name='Production per Agent', header=None, skiprows=5)
    
    print("✅ DPR loaded and decrypted")
    return df


def extract_data(df):
    """Extract all dashboard data from DPR."""
    print("🔍 Extracting dashboard data...")
    
    # Map columns (v11 mapping)
    df['AGENT_ID'] = df[1].astype(str).str.strip()
    df['AGENT_NAME'] = df[2]
    df['STATUS'] = df[4]
    df['MAY_MTD'] = pd.to_numeric(df[13], errors='coerce').fillna(0)
    df['MAY_CC'] = pd.to_numeric(df[14], errors='coerce').fillna(0)
    df['YTD'] = pd.to_numeric(df[17], errors='coerce').fillna(0)
    df['YTD_CC'] = pd.to_numeric(df[18], errors='coerce').fillna(0)
    df['FWM'] = df[28]
    
    # Filter to active agents
    df_agents = df[df['AGENT_ID'].str.match(r'^\d{8}$', na=False)].copy()
    df_active = df_agents[df_agents['STATUS'] == 'ACTIVE'].copy()
    
    # Map teams
    df_active['TEAM'] = df_active['FWM'].map(FWM_TO_TEAM)
    
    # Branch totals
    branch_data = {
        'mtd': float(df_active['MAY_MTD'].sum()),
        'ytd': float(df_active['YTD'].sum()),
        'active': int(len(df_active[df_active['MAY_MTD'] > 0])),
        'manpower': int(len(df_active)),
        'cases_mtd': float(df_active['MAY_CC'].sum()),
        'cases_ytd': float(df_active['YTD_CC'].sum())
    }
    
    print(f"   Branch MTD: ₱{branch_data['mtd']:,.0f}")
    print(f"   Active Producers: {branch_data['active']}")
    
    # Team data
    teams_data = []
    for team_name, bp_may in TEAM_BP_MAY.items():
        team_df = df_active[df_active['TEAM'] == team_name]
        
        mtd = float(team_df['MAY_MTD'].sum())
        ytd = float(team_df['YTD'].sum())
        active = int(len(team_df[team_df['MAY_MTD'] > 0]))
        manpower = int(len(team_df))
        
        # Producers list
        producers = []
        for idx, row in team_df.iterrows():
            producers.append({
                'name': row['AGENT_NAME'],
                'id': row['AGENT_ID'],
                'mtd': float(row['MAY_MTD']),
                'ytd': float(row['YTD']),
                'cases_mtd': float(row['MAY_CC']),
                'cases_ytd': float(row['YTD_CC'])
            })
        
        teams_data.append({
            'name': team_name,
            'mtd': mtd,
            'ytd': ytd,
            'bp_may': bp_may,
            'bp_ytd': TEAM_BP_YTD[team_name],
            'progress': (mtd / bp_may * 100) if bp_may > 0 else 0,
            'pacing': (ytd / TEAM_BP_YTD[team_name] * 100) if TEAM_BP_YTD[team_name] > 0 else 0,
            'active': active,
            'manpower': manpower,
            'producers': sorted(producers, key=lambda x: x['mtd'], reverse=True)
        })
        
        print(f"   Team {team_name}: ₱{mtd:,.0f} MTD ({active}/{manpower} active)")
    
    # Sort teams by progress
    teams_data = sorted(teams_data, key=lambda x: x['progress'], reverse=True)
    
    dashboard_data = {
        'branch': branch_data,
        'teams': teams_data,
        'bp_branch_may': BP_BRANCH_MAY,
        'bp_branch_ytd': BP_BRANCH_YTD,
        'as_of_date': datetime.now().strftime('%B %d, %Y'),
        'generated_at': datetime.now().isoformat()
    }
    
    print("✅ Data extraction complete")
    return dashboard_data


def save_data(data, output_path):
    """Save dashboard data to JSON file."""
    print(f"💾 Saving data to: {output_path}")
    
    # Create data dir
