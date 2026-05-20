#!/usr/bin/env python3
"""
Update Dashboard HTML
=====================

Reads dashboard data from JSON and generates updated index.html
"""

import json
import os
from datetime import datetime

# Configuration
DATA_FILE = 'data/dashboard_data.json'
TEMPLATE_FILE = 'dashboard_template.html'
OUTPUT_FILE = 'index.html'


def load_data(data_path):
    """Load dashboard data from JSON."""
    print(f"📂 Loading data from: {data_path}")
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    print("✅ Data loaded successfully")
    return data


def load_template(template_path):
    """Load HTML template."""
    print(f"📄 Loading template: {template_path}")
    
    with open(template_path, 'r') as f:
        template = f.read()
    
    print("✅ Template loaded")
    return template


def update_html(template, data):
    """Update HTML template with dashboard data."""
    print("🔄 Updating HTML with new data...")
    
    # Replace the data placeholder
    data_json = json.dumps(data, indent=2)
    html = template.replace('DASHBOARD_DATA_PLACEHOLDER', data_json)
    
    print("✅ HTML updated")
    return html


def save_html(html, output_path):
    """Save updated HTML to file."""
    print(f"💾 Saving HTML to: {output_path}")
    
    with open(output_path, 'w') as f:
        f.write(html)
    
    print("✅ HTML saved successfully")


def update_metadata(data):
    """Update latest_update.json with metadata."""
    os.makedirs('data', exist_ok=True)
    
    metadata = {
        'last_update': datetime.now().isoformat(),
        'as_of_date': data['as_of_date'],
        'branch_mtd': data['branch']['mtd'],
        'branch_ytd': data['branch']['ytd'],
        'active_producers': data['branch']['active'],
        'manpower': data['branch']['manpower']
    }
    
    with open('data/latest_update.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("✅ Metadata updated")


def main():
    """Main execution function."""
    print("="*60)
    print("ONE APEX - UPDATE DASHBOARD HTML")
    print("="*60)
    print()
    
    try:
        # Load data
        data = load_data(DATA_FILE)
        
        # Load template
        template = load_template(TEMPLATE_FILE)
        
        # Update HTML
        html = update_html(template, data)
        
        # Save HTML
        save_html(html, OUTPUT_FILE)
        
        # Update metadata
        update_metadata(data)
        
        print()
        print("="*60)
        print("✅ DASHBOARD HTML UPDATE COMPLETE")
        print("="*60)
        print(f"Branch MTD: ₱{data['branch']['mtd']:,.0f}")
        print(f"Active: {data['branch']['active']} producers")
        print(f"Output: {OUTPUT_FILE}")
        print(f"As of: {data['as_of_date']}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
