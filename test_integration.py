#!/usr/bin/env python3
"""
통합 테스트 스크립트
모든 Phase의 API 엔드포인트를 검증합니다.
"""

import requests
import json
from typing import Dict, List, Tuple

# 테스트 대상 서버
BASE_URL = "http://139.150.11.99:8000"
API_PREFIX = "/api/v1"

# 테스트 결과 저장
test_results: List[Dict] = []


def test_endpoint(
    method: str,
    endpoint: str,
    phase: str,
    description: str,
    auth_required: bool = True,
    expected_status: int = 401  # 인증 필요 시 기본 401
) -> Dict:
    """단일 엔드포인트 테스트"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            response = requests.request(method, url, timeout=5)
        
        status_code = response.status_code
        
        # 인증이 필요한 경우 401 또는 403이면 정상
        if auth_required and status_code in [401, 403]:
            result = "✅ PASS"
            message = f"인증 필요 ({status_code})"
        # 인증이 필요 없는 경우 200~299면 정상
        elif not auth_required and 200 <= status_code < 300:
            result = "✅ PASS"
            message = f"정상 응답 ({status_code})"
        # 404는 엔드포인트 미존재
        elif status_code == 404:
            result = "❌ FAIL"
            message = "엔드포인트 미존재 (404)"
        # 500번대는 서버 에러
        elif status_code >= 500:
            result = "❌ FAIL"
            message = f"서버 에러 ({status_code})"
        else:
            result = "⚠️ WARN"
            message = f"예상치 못한 응답 ({status_code})"
        
        test_info = {
            "phase": phase,
            "endpoint": endpoint,
            "description": description,
            "method": method,
            "status_code": status_code,
            "result": result,
            "message": message
        }
        
        print(f"{result} [{phase}] {method} {endpoint} - {message}")
        
        return test_info
        
    except requests.exceptions.Timeout:
        test_info = {
            "phase": phase,
            "endpoint": endpoint,
            "description": description,
            "method": method,
            "status_code": 0,
            "result": "❌ FAIL",
            "message": "타임아웃"
        }
        print(f"❌ FAIL [{phase}] {method} {endpoint} - 타임아웃")
        return test_info
        
    except Exception as e:
        test_info = {
            "phase": phase,
            "endpoint": endpoint,
            "description": description,
            "method": method,
            "status_code": 0,
            "result": "❌ FAIL",
            "message": f"에러: {str(e)}"
        }
        print(f"❌ FAIL [{phase}] {method} {endpoint} - {str(e)}")
        return test_info


def run_tests():
    """모든 테스트 실행"""
    print("=" * 80)
    print("통합 테스트 시작: 모든 Phase API 엔드포인트 검증")
    print("=" * 80)
    print()
    
    # Health check (인증 불필요)
    print("🔍 Health Check")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/health", "Core", "헬스체크", auth_required=False, expected_status=200))
    print()
    
    # Phase 10: Smart Dispatch Rule Engine
    print("🔍 Phase 10: Smart Dispatch Rule Engine")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/dispatch-rules", "Phase 10", "배차 규칙 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/dispatch-rules/categories", "Phase 10", "규칙 카테고리"))
    print()
    
    # Phase 11-C: Rule Simulation
    print("🔍 Phase 11-C: Rule Simulation")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/simulations", "Phase 11-C", "시뮬레이션 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/simulations/statistics", "Phase 11-C", "시뮬레이션 통계"))
    print()
    
    # Phase 11-B: Traffic Information Integration
    print("🔍 Phase 11-B: Traffic Information Integration")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/traffic/current", "Phase 11-B", "실시간 교통 정보"))
    test_results.append(test_endpoint("POST", f"{API_PREFIX}/routes/optimize", "Phase 11-B", "경로 최적화"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/traffic/alerts", "Phase 11-B", "교통 알림"))
    print()
    
    # Phase 12: Integrated Dispatch (Naver Map + GPS + AI)
    print("🔍 Phase 12: Integrated Dispatch")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/integrated-dispatch/vehicles/tracking", "Phase 12", "실시간 차량 추적"))
    test_results.append(test_endpoint("POST", f"{API_PREFIX}/auto-dispatch/optimize", "Phase 12", "AI 자동 배차"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/naver-map/geocode", "Phase 12", "Naver 지오코딩"))
    print()
    
    # Phase 13-14: IoT Sensor Monitoring + Predictive Maintenance
    print("🔍 Phase 13-14: IoT & Predictive Maintenance")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/iot/sensors", "Phase 13-14", "IoT 센서 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/iot/sensors/realtime", "Phase 13-14", "실시간 센서 데이터"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/iot/maintenance/predictions", "Phase 13-14", "예측 유지보수"))
    print()
    
    # Phase 15: ML Auto-Learning
    print("🔍 Phase 15: ML Auto-Learning")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/ml-autolearning/experiments", "Phase 15", "ML 실험 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/ml-autolearning/training-data/statistics", "Phase 15", "학습 데이터 통계"))
    test_results.append(test_endpoint("POST", f"{API_PREFIX}/ml-autolearning/training/start", "Phase 15", "학습 시작"))
    print()
    
    # Phase 16: Driver App Enhancement
    print("🔍 Phase 16: Driver App Enhancement")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/driver/notifications", "Phase 16", "드라이버 알림"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/driver/performance/statistics", "Phase 16", "드라이버 성과 통계"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/driver/chat/rooms", "Phase 16", "채팅방 목록"))
    print()
    
    # 기타 Core API
    print("🔍 Core APIs")
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/orders", "Core", "주문 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/dispatches", "Core", "배차 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/vehicles", "Core", "차량 목록"))
    test_results.append(test_endpoint("GET", f"{API_PREFIX}/clients", "Core", "고객 목록"))
    print()
    
    # 결과 요약
    print("=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    
    total = len(test_results)
    passed = len([r for r in test_results if r["result"] == "✅ PASS"])
    failed = len([r for r in test_results if r["result"] == "❌ FAIL"])
    warned = len([r for r in test_results if r["result"] == "⚠️ WARN"])
    
    print(f"전체: {total}개")
    print(f"✅ 통과: {passed}개 ({passed/total*100:.1f}%)")
    print(f"❌ 실패: {failed}개 ({failed/total*100:.1f}%)")
    print(f"⚠️ 경고: {warned}개 ({warned/total*100:.1f}%)")
    print()
    
    # 실패한 테스트 상세
    if failed > 0:
        print("=" * 80)
        print("❌ 실패한 테스트 상세")
        print("=" * 80)
        for result in test_results:
            if result["result"] == "❌ FAIL":
                print(f"[{result['phase']}] {result['method']} {result['endpoint']}")
                print(f"  → {result['message']}")
        print()
    
    # 결과를 JSON 파일로 저장
    with open("/home/user/webapp/test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print("결과가 test_results.json에 저장되었습니다.")
    print()
    
    return passed, failed, warned


if __name__ == "__main__":
    run_tests()
