#!/usr/bin/env python3
"""Remove duplicate functions from main.cpp that are now in request_handler.cpp"""

import re

# Read main.cpp
with open('src/main.cpp', 'r') as f:
    lines = f.readlines()

# Functions to remove (with their line ranges)
# calculateSentiment: 49-81
# scoreLead: 84-179
# detectPhishing: 181-307
# extractJsonField: 309-319

# Keep track of what to keep
output = []
skip_until = -1

for i, line in enumerate(lines, 1):
    # Skip lines if we're in a function to remove
    if skip_until > 0 and i <= skip_until:
        continue

    # Check if we're starting a function to remove
    if i == 49:  # calculateSentiment starts
        skip_until = 81
        continue
    elif i == 84:  # scoreLead starts
        skip_until = 179
        continue
    elif i == 181:  # detectPhishing starts
        skip_until = 307
        continue
    elif i == 309:  # extractJsonField starts
        skip_until = 319
        continue

    # Keep this line
    output.append(line)

# Write cleaned main.cpp
with open('src/main.cpp', 'w') as f:
    f.writelines(output)

print("Removed duplicate functions from main.cpp")
print(f"Original: {len(lines)} lines")
print(f"Cleaned: {len(output)} lines")
print(f"Removed: {len(lines) - len(output)} lines")