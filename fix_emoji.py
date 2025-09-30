#!/usr/bin/env python3

import re

def fix_emoji_in_file():
    with open('real_live_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace all emoji with text
    replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '🔄': '[REFRESH]',
        '📊': '[DATA]',
        '🔍': '[DEBUG]',
        '💾': '[SAVE]',
        '⚠️': '[WARNING]',
        '🔗': '[LINK]',
        '❤️': '[LOVE]'
    }

    for emoji, text in replacements.items():
        content = content.replace(emoji, text)

    with open('real_live_dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print('All emoji replaced with text')

if __name__ == "__main__":
    fix_emoji_in_file()
