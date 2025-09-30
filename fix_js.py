#!/usr/bin/env python3
"""
Fix JavaScript syntax error in real_live_dashboard.py
"""

import re

# Read the file
with open('real_live_dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix JavaScript syntax errors
content = content.replace(
    "const exchangeRate = {stats['exchange_rate_murf']};",
    "const exchangeRate = {stats['exchange_rate_murf']};"
)

content = content.replace(
    "const ktaPrice = {stats['kta_price_usd']};",
    "const ktaPrice = {stats['kta_price_usd']};"
)

# Write back to file
with open('real_live_dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ JavaScript syntax fixed!")
