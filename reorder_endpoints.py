#!/usr/bin/env python3
"""
Reorder endpoints in dispatch_rules.py to fix routing issue.
Move /conflicts endpoint before /{rule_id} endpoint.
"""

file_path = '/home/user/webapp/backend/app/api/v1/endpoints/dispatch_rules.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the conflicts endpoint block
conflicts_start = None
conflicts_end = None

for i, line in enumerate(lines):
    if '@router.get("/conflicts")' in line:
        conflicts_start = i
    elif conflicts_start is not None and conflicts_end is None:
        # Find the end of the function (next @router or next def at same indentation)
        if (line.startswith('@router.') or 
            (line.startswith('def ') and not line.startswith('    def'))):
            conflicts_end = i
            break

# If we didn't find an end, it goes to the end of file
if conflicts_start is not None and conflicts_end is None:
    conflicts_end = len(lines)

# Extract the conflicts block
conflicts_block = lines[conflicts_start:conflicts_end]

# Find the /{rule_id} endpoint
rule_id_line = None
for i, line in enumerate(lines):
    if '@router.get("/{rule_id}"' in line:
        rule_id_line = i
        break

if conflicts_start is not None and rule_id_line is not None and conflicts_start > rule_id_line:
    print(f"Moving conflicts endpoint from line {conflicts_start+1} to before line {rule_id_line+1}")
    
    # Remove the conflicts block from its original position
    new_lines = lines[:conflicts_start] + lines[conflicts_end:]
    
    # Find the new position for /{rule_id} after removal
    rule_id_line_new = None
    for i, line in enumerate(new_lines):
        if '@router.get("/{rule_id}"' in line:
            rule_id_line_new = i
            break
    
    # Insert the conflicts block before /{rule_id}
    # Add two blank lines for readability
    final_lines = (new_lines[:rule_id_line_new] + 
                   conflicts_block + 
                   ['\n'] +
                   new_lines[rule_id_line_new:])
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(final_lines)
    
    print(f"✅ Successfully moved /conflicts endpoint to line {rule_id_line_new+1}")
    print(f"   File: {file_path}")
    
else:
    if conflicts_start is None:
        print("❌ Could not find /conflicts endpoint")
    elif rule_id_line is None:
        print("❌ Could not find /{rule_id} endpoint")
    else:
        print("✅ /conflicts is already before /{rule_id}, no changes needed")
