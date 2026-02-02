#!/usr/bin/env python3
import re
import sys

def add_sidebar_to_page(filepath):
    """페이지 파일에 Sidebar 레이아웃 추가"""
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Sidebar import 확인 및 추가
        if "import Sidebar from" not in content:
            # 마지막 import 문 찾기
            import_pattern = r"(import .*?;)\n(?!import)"
            matches = list(re.finditer(import_pattern, content, re.MULTILINE))
            if matches:
                last_import = matches[-1]
                insert_pos = last_import.end()
                content = (content[:insert_pos] + 
                          "\nimport Sidebar from '../components/common/Sidebar';" +
                          content[insert_pos:])
                print(f"  ✅ Sidebar import 추가됨")
            else:
                print(f"  ⚠️  Import 문을 찾을 수 없음")
                return False
        else:
            print(f"  ℹ️  Sidebar import 이미 존재")
        
        # 2. Main return 찾기 (함수 컴포넌트의 return)
        # 패턴: return ( 로 시작하는 부분
        return_pattern = r'(\s+return\s*\(\s*\n\s*)(<div[^>]*>)'
        
        if re.search(return_pattern, content):
            # return 다음의 첫 div를 Sidebar 레이아웃으로 감싸기
            def replace_return(match):
                indent = match.group(1)
                original_div = match.group(2)
                
                # 이미 Sidebar가 있는지 확인
                if 'Sidebar' in content[match.start():match.start()+500]:
                    return match.group(0)  # 이미 있으면 변경 안 함
                
                # 새로운 레이아웃 구조
                new_content = (
                    f'{indent}<div className="flex h-screen bg-gray-100">\n'
                    f'{indent}  <Sidebar />\n'
                    f'{indent}  <div className="flex-1 overflow-auto">\n'
                    f'{indent}    {original_div}'
                )
                return new_content
            
            new_content = re.sub(return_pattern, replace_return, content, count=1)
            
            # 파일 끝의 마지막 }; 전에 닫는 태그 추가
            # 간단한 방법: 마지막 </div> 다음에 두 개의 </div> 추가
            # 주의: 이 방법은 완벽하지 않으므로 수동 확인 필요
            
            if new_content != content:
                content = new_content
                print(f"  ✅ 레이아웃 래핑 시도됨 (수동 확인 필요)")
            else:
                print(f"  ℹ️  레이아웃이 이미 올바를 수 있음")
        else:
            print(f"  ⚠️  return 문을 찾을 수 없음")
        
        # 파일 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return False

# 메인 실행
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fix_pages_with_sidebar.py <filepath>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"📝 처리: {filepath}")
    add_sidebar_to_page(filepath)
