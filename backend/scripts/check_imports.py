#!/usr/bin/env python3
import sys, re
from pathlib import Path

FORBIDDEN = [
    (r'from app\.core\.auth import get_current_user', 'Use: from app.api.auth import'),
    (r'from app\.core\.security import get_current_user', 'Use: from app.api.auth import'),
    (r'from app\.database import', 'Use: from app.core.database import'),
    (r'from app\.models\.temperature_alert import', 'Use: from app.models.vehicle_location import'),
]

errors = []
for py_file in Path('backend/app').rglob('*.py'):
    content = py_file.read_text()
    for pattern, msg in FORBIDDEN:
        if re.search(pattern, content):
            print(f"❌ {py_file}: {msg}")
            errors.append(py_file)

sys.exit(1 if errors else 0)
