#!/usr/bin/env python3
"""
Complete Layout Fix Script
- Removes all Layout imports from page files
- Removes all Layout wrapper tags from pages
- Fixes OrdersPage.tsx syntax errors
- Ensures clean JSX structure
"""

import os
import re
from pathlib import Path

def fix_orders_page(file_path):
    """Fix OrdersPage.tsx syntax errors"""
    print(f"\n🔧 Fixing {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the line with ")}" followed by ");"
    # This indicates wrong closing - should be "</>" instead
    lines = content.split('\n')
    
    modified = False
    for i, line in enumerate(lines):
        # Look for the problematic pattern near the end
        if i >= len(lines) - 10:  # Check last 10 lines
            # Fix: ")}\n  );" should be "</>\n  );"
            if line.strip() == ')}' and i + 1 < len(lines) and lines[i+1].strip().startswith(');'):
                lines[i] = line.replace(')}', ' </>')
                modified = True
                print(f"  ✓ Fixed line {i+1}: Changed '}}' to '</>'")    
    if modified:
        content = '\n'.join(lines)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Fixed {file_path}")
        return True
    else:
        print(f"  ℹ️  No changes needed for {file_path}")
        return False

def remove_layout_from_page(file_path):
    """Remove Layout imports and wrapper tags from a page file"""
    print(f"\n🔍 Checking {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modified = False
    
    # 1. Remove Layout import statements
    import_patterns = [
        r"import\s+Layout\s+from\s+['\"].*?Layout['\"];\s*\n?",
        r"import\s+\{\s*Layout\s*\}\s+from\s+['\"].*?['\"];\s*\n?",
    ]
    
    for pattern in import_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            modified = True
            print(f"  ✓ Removed Layout import")
    
    # 2. Remove <Layout> wrapper tags
    # Find and remove <Layout> and corresponding </Layout>
    if '<Layout>' in content or '<Layout ' in content:
        # Simple case: <Layout>...</Layout>
        content = re.sub(r'<Layout>\s*', '', content)
        content = re.sub(r'\s*</Layout>', '', content)
        modified = True
        print(f"  ✓ Removed <Layout> wrapper tags")
    
    # 3. Remove Sidebar imports if they exist
    sidebar_patterns = [
        r"import\s+Sidebar\s+from\s+['\"].*?Sidebar['\"];\s*\n?",
        r"import\s+\{\s*Sidebar\s*\}\s+from\s+['\"].*?['\"];\s*\n?",
    ]
    
    for pattern in sidebar_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            modified = True
            print(f"  ✓ Removed Sidebar import")
    
    # 4. Remove <Sidebar /> usage
    if '<Sidebar' in content:
        content = re.sub(r'<Sidebar\s*/>\s*\n?', '', content)
        content = re.sub(r'<Sidebar>\s*</Sidebar>\s*\n?', '', content)
        modified = True
        print(f"  ✓ Removed <Sidebar /> usage")
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Updated {file_path}")
        return True
    else:
        print(f"  ℹ️  No Layout/Sidebar found in {file_path}")
        return False

def main():
    print("=" * 60)
    print("🚀 Complete Layout Refactoring Script")
    print("=" * 60)
    
    # Get the frontend pages directory
    pages_dir = Path('frontend/src/pages')
    
    if not pages_dir.exists():
        print(f"\n❌ Error: Directory {pages_dir} not found!")
        print("   Please run this script from the project root.")
        return
    
    # Exceptions - these should NOT have Layout removed
    exceptions = ['LoginPage.tsx', 'TrackingPage.tsx']
    
    # Process all .tsx files in pages directory
    tsx_files = list(pages_dir.glob('*.tsx'))
    print(f"\n📂 Found {len(tsx_files)} page files")
    
    fixed_count = 0
    skipped_count = 0
    
    for file_path in sorted(tsx_files):
        file_name = file_path.name
        
        # Skip exceptions
        if file_name in exceptions:
            print(f"\n⏭️  Skipping {file_name} (exception)")
            skipped_count += 1
            continue
        
        # Special handling for OrdersPage
        if file_name == 'OrdersPage.tsx':
            if fix_orders_page(file_path):
                fixed_count += 1
            continue
        
        # Remove Layout from all other pages
        if remove_layout_from_page(file_path):
            fixed_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Layout Refactoring Complete!")
    print("=" * 60)
    print(f"📊 Statistics:")
    print(f"   - Total files processed: {len(tsx_files)}")
    print(f"   - Files modified: {fixed_count}")
    print(f"   - Files skipped: {skipped_count}")
    print(f"   - No changes needed: {len(tsx_files) - fixed_count - skipped_count}")
    print()
    print("🎯 Next Steps:")
    print("   1. Review changes: git diff frontend/src/pages/")
    print("   2. Build frontend: cd frontend && npm run build")
    print("   3. Test in browser")
    print()

if __name__ == '__main__':
    main()
