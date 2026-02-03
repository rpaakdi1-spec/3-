"""
주문관리, AI배차최적화, 배차관리 상태 용어 일관성 검증 스크립트
"""

print("=" * 80)
print("상태 용어 일관성 검증")
print("=" * 80)

# 1. OrderStatus (주문 관리)
print("\n📋 1. OrderStatus (주문 관리)")
print("-" * 80)
order_status = {
    'PENDING': '배차대기',
    'ASSIGNED': '배차완료',
    'IN_TRANSIT': '운송중',
    'DELIVERED': '배송완료',
    'CANCELLED': '취소'
}
for key, value in order_status.items():
    print(f"  {key:15} → {value}")

# 2. DispatchStatus (배차 관리)
print("\n📦 2. DispatchStatus (배차 관리)")
print("-" * 80)
dispatch_status = {
    'DRAFT': '임시저장',
    'CONFIRMED': '확정',
    'IN_PROGRESS': '진행중',
    'COMPLETED': '완료',
    'CANCELLED': '취소'
}
for key, value in dispatch_status.items():
    print(f"  {key:15} → {value}")

# 3. 사용자 요청 용어
print("\n🎯 3. 사용자 요청 용어")
print("-" * 80)
requested_terms = [
    '배차대기',
    '배차완료',
    '배송중',
    '배송완료',
    '취소'
]
for term in requested_terms:
    print(f"  - {term}")

# 4. 불일치 분석
print("\n⚠️  4. 불일치 분석")
print("-" * 80)

inconsistencies = []

# OrderStatus vs 요청 용어
if order_status['IN_TRANSIT'] != '배송중':
    inconsistencies.append({
        'module': 'OrderStatus',
        'field': 'IN_TRANSIT',
        'current': order_status['IN_TRANSIT'],
        'requested': '배송중',
        'issue': '용어 불일치'
    })

# DispatchStatus vs 요청 용어
dispatch_not_in_request = []
for key, value in dispatch_status.items():
    if value not in requested_terms and key != 'DRAFT' and key != 'CONFIRMED' and key != 'IN_PROGRESS' and key != 'COMPLETED':
        pass  # 취소는 일치
    
    # 배차 상태의 특수 용어들
    if key == 'DRAFT':
        dispatch_not_in_request.append(f"{key} → {value} (배차 전용)")
    elif key == 'CONFIRMED':
        dispatch_not_in_request.append(f"{key} → {value} (배차 전용)")
    elif key == 'IN_PROGRESS':
        dispatch_not_in_request.append(f"{key} → {value} (배차 전용)")
    elif key == 'COMPLETED':
        inconsistencies.append({
            'module': 'DispatchStatus',
            'field': key,
            'current': value,
            'requested': '배송완료 또는 배차완료',
            'issue': '완료 vs 배송완료 모호'
        })

if inconsistencies:
    print("🔴 발견된 불일치:")
    for i, issue in enumerate(inconsistencies, 1):
        print(f"\n  {i}. {issue['module']}.{issue['field']}")
        print(f"     현재: {issue['current']}")
        print(f"     요청: {issue['requested']}")
        print(f"     문제: {issue['issue']}")
else:
    print("✅ 주요 불일치 없음 (배차 전용 상태 제외)")

# 5. 배차 전용 상태
print("\n📌 5. 배차 관리 전용 상태 (주문과 무관)")
print("-" * 80)
for term in dispatch_not_in_request:
    print(f"  - {term}")

# 6. 매핑 제안
print("\n💡 6. 용어 통일 제안")
print("=" * 80)

print("\n📋 주문 관리 (OrderStatus) - 수정 필요:")
print("-" * 80)
print("  현재: IN_TRANSIT → '운송중'")
print("  제안: IN_TRANSIT → '배송중'")
print("  이유: 사용자 요청 용어와 일치")

print("\n📦 배차 관리 (DispatchStatus) - 현행 유지:")
print("-" * 80)
print("  ✅ DRAFT → '임시저장' (배차 전용)")
print("  ✅ CONFIRMED → '확정' (배차 전용)")
print("  ✅ IN_PROGRESS → '진행중' (배차 전용)")
print("  ⚠️  COMPLETED → '완료' → '배차완료'로 변경 권장")
print("  ✅ CANCELLED → '취소'")

print("\n🎯 통일 후 예상 결과:")
print("-" * 80)
print("주문 상태: 배차대기 → 배차완료 → 배송중 → 배송완료 → 취소")
print("배차 상태: 임시저장 → 확정 → 진행중 → 배차완료 → 취소")

print("\n" + "=" * 80)
print("검증 완료")
print("=" * 80)
