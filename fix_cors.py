"""
Temporary script to modify the Django settings to enable CORS for development.
Run this with: python fix_cors.py
"""

import os
import re

# The settings file to modify
settings_file = 'backend/settings.py'

# Read the current settings file
with open(settings_file, 'r') as file:
    content = file.read()

# Modify the CORS settings to allow all origins during development
cors_pattern = r"CORS_ALLOW_ALL_ORIGINS = os\.getenv\(\"CORS_ALLOW_ALL_ORIGINS\", \"false\"\)\.lower\(\) == \"true\""
cors_replacement = "CORS_ALLOW_ALL_ORIGINS = True  # Modified for local development"

# Make the changes
modified_content = re.sub(cors_pattern, cors_replacement, content)

# Write the modified content back to the file
with open(settings_file, 'w') as file:
    file.write(modified_content)

print(f"✅ Updated {settings_file} to allow all origins for CORS during development.")
print("Restart your Django server for changes to take effect.")
print("Run: python manage.py runserver") 