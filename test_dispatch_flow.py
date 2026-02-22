#!/usr/bin/env python3
"""
배차 플로우 통합 테스트 스크립트

주문관리 → AI배차최적화 → 배차관리 전체 플로우 테스트
"""

import requests
import json
from datetime import date, datetime, timedelta
from typing import Dict, Any, List

# API Base URL
BASE_URL = "http://139.150.11.99/api/v1"
# BASE_URL = "http://localhost:8000/api/v1"  # 로컬 테스트용

# 인증 토큰 (실제 토큰으로 교체 필요)
ACCESS_TOKEN = None


def set_token(token: str):
    """테스트용 토큰 설정"""
    global ACCESS_TOKEN
    ACCESS_TOKEN = token


def get_headers():
    """API 요청 헤더"""
    headers = {"Content-Type": "application/json"}
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"
    return headers


class DispatchFlowTester:
    """배차 플로우 통합 테스트"""
    
    def __init__(self):
        self.test_results = []
        self.created_order_ids = []
        self.created_dispatch_ids = []
        
    def log_result(self, test_name: str, success: bool, message: str, data: Any = None):
        """테스트 결과 기록"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    # ========================================
    # 1. 주문 관리 테스트
    # ========================================
    
    def test_get_orders(self):
        """주문 목록 조회 테스트"""
        print("\n" + "="*60)
        print("1️⃣  주문 관리 테스트")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/orders/",
                headers=get_headers(),
                params={"limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                items = data.get("items", [])
                
                self.log_result(
                    "주문 목록 조회",
                    True,
                    f"총 {total}건의 주문 조회 성공",
                    {"total": total, "sample": items[:3] if items else []}
                )
                return items
            else:
                self.log_result(
                    "주문 목록 조회",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result("주문 목록 조회", False, f"예외 발생: {str(e)}")
            return []
    
    def test_get_pending_orders(self):
        """배차 대기 중인 주문 조회"""
        try:
            response = requests.get(
                f"{BASE_URL}/orders/",
                headers=get_headers(),
                params={"status": "배차대기", "limit": 100}
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                self.log_result(
                    "배차 대기 주문 조회",
                    True,
                    f"배차 대기 중인 주문: {len(items)}건",
                    {"count": len(items), "orders": [o.get("order_number") for o in items[:5]]}
                )
                return items
            else:
                self.log_result(
                    "배차 대기 주문 조회",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result("배차 대기 주문 조회", False, f"예외 발생: {str(e)}")
            return []
    
    def test_create_order(self):
        """테스트 주문 생성"""
        try:
            # 테스트용 주문 데이터
            order_data = {
                "order_number": f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "order_date": date.today().isoformat(),
                "temperature_zone": "냉장",
                "pickup_address": "서울특별시 강남구 테헤란로 427",
                "delivery_address": "서울특별시 송파구 올림픽로 300",
                "pallet_count": 5,
                "weight_kg": 500.0,
                "product_name": "테스트 상품",
                "status": "배차대기",
                "priority": 2
            }
            
            response = requests.post(
                f"{BASE_URL}/orders/",
                headers=get_headers(),
                json=order_data
            )
            
            if response.status_code == 201:
                data = response.json()
                order_id = data.get("id")
                self.created_order_ids.append(order_id)
                
                self.log_result(
                    "테스트 주문 생성",
                    True,
                    f"주문 생성 성공: {data.get('order_number')} (ID: {order_id})",
                    {"id": order_id, "order_number": data.get("order_number")}
                )
                return data
            else:
                self.log_result(
                    "테스트 주문 생성",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("테스트 주문 생성", False, f"예외 발생: {str(e)}")
            return None
    
    # ========================================
    # 2. AI 배차 최적화 테스트
    # ========================================
    
    def test_optimization(self, order_ids: List[int]):
        """배차 최적화 테스트"""
        print("\n" + "="*60)
        print("2️⃣  AI 배차 최적화 테스트")
        print("="*60)
        
        if not order_ids:
            self.log_result(
                "배차 최적화",
                False,
                "최적화할 주문이 없습니다",
                None
            )
            return None
        
        try:
            # 기본 Greedy 알고리즘 테스트
            opt_data = {
                "order_ids": order_ids[:10],  # 최대 10개 주문
                "vehicle_ids": [],  # 빈 배열 = 모든 차량
                "dispatch_date": date.today().isoformat()
            }
            
            print(f"\n🔄 기본 배차 최적화 실행 중... (주문 {len(opt_data['order_ids'])}건)")
            
            response = requests.post(
                f"{BASE_URL}/dispatches/optimize",
                headers=get_headers(),
                json=opt_data
            )
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])
                unassigned = data.get("unassigned_orders", [])
                summary = data.get("summary", {})
                
                self.log_result(
                    "기본 배차 최적화",
                    True,
                    f"최적화 완료: 차량 {len(routes)}대 배차, 미배차 {len(unassigned)}건",
                    {
                        "total_routes": len(routes),
                        "unassigned": len(unassigned),
                        "total_distance": summary.get("total_distance_km", 0),
                        "total_orders": summary.get("total_orders", 0)
                    }
                )
                return data
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2, ensure_ascii=False)
                except:
                    pass
                
                self.log_result(
                    "기본 배차 최적화",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    error_detail
                )
                print(f"\n   상세 에러:\n{error_detail}")
                return None
                
        except Exception as e:
            self.log_result("기본 배차 최적화", False, f"예외 발생: {str(e)}")
            return None
    
    def test_advanced_optimization(self, order_ids: List[int]):
        """고급 배차 최적화 (CVRPTW) 테스트"""
        if not order_ids:
            return None
        
        try:
            opt_data = {
                "order_ids": order_ids[:10],
                "vehicle_ids": [],
                "dispatch_date": date.today().isoformat()
            }
            
            print(f"\n🚀 고급 배차 최적화 (CVRPTW) 실행 중...")
            
            response = requests.post(
                f"{BASE_URL}/dispatches/optimize-cvrptw",
                headers=get_headers(),
                json=opt_data,
                params={
                    "time_limit": 30,
                    "use_time_windows": True,
                    "use_real_routing": False
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get("routes", [])
                summary = data.get("summary", {})
                
                self.log_result(
                    "고급 배차 최적화",
                    True,
                    f"CVRPTW 최적화 완료: 차량 {len(routes)}대 배차",
                    {
                        "total_routes": len(routes),
                        "total_distance": summary.get("total_distance_km", 0),
                        "optimization_status": data.get("optimization_status")
                    }
                )
                return data
            else:
                self.log_result(
                    "고급 배차 최적화",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("고급 배차 최적화", False, f"예외 발생: {str(e)}")
            return None
    
    # ========================================
    # 3. 배차 관리 테스트
    # ========================================
    
    def test_get_dispatches(self):
        """배차 목록 조회 테스트"""
        print("\n" + "="*60)
        print("3️⃣  배차 관리 테스트")
        print("="*60)
        
        try:
            response = requests.get(
                f"{BASE_URL}/dispatches/",
                headers=get_headers(),
                params={"limit": 10}
            )
            
            if response.status_code == 200:
                data = response.json()
                total = data.get("total", 0)
                items = data.get("items", [])
                
                # 상태별 통계
                status_stats = {}
                for item in items:
                    status = item.get("status", "Unknown")
                    status_stats[status] = status_stats.get(status, 0) + 1
                
                self.log_result(
                    "배차 목록 조회",
                    True,
                    f"총 {total}건의 배차 조회 성공",
                    {
                        "total": total,
                        "status_stats": status_stats,
                        "sample": items[:3] if items else []
                    }
                )
                return items
            else:
                self.log_result(
                    "배차 목록 조회",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return []
                
        except Exception as e:
            self.log_result("배차 목록 조회", False, f"예외 발생: {str(e)}")
            return []
    
    def test_dispatch_dashboard(self):
        """배차 대시보드 통계 조회"""
        try:
            response = requests.get(
                f"{BASE_URL}/dispatches/dashboard",
                headers=get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "배차 대시보드",
                    True,
                    "대시보드 통계 조회 성공",
                    {
                        "total_orders": data.get("total_orders"),
                        "pending_orders": data.get("pending_orders"),
                        "active_dispatches": data.get("active_dispatches"),
                        "completed_today": data.get("completed_today"),
                        "available_vehicles": data.get("available_vehicles")
                    }
                )
                return data
            else:
                self.log_result(
                    "배차 대시보드",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("배차 대시보드", False, f"예외 발생: {str(e)}")
            return None
    
    def test_dispatch_confirmation(self, dispatch_ids: List[int]):
        """배차 확정 테스트"""
        if not dispatch_ids:
            return None
        
        try:
            confirm_data = {"dispatch_ids": dispatch_ids}
            
            print(f"\n✅ 배차 확정 실행 중... (배차 {len(dispatch_ids)}건)")
            
            response = requests.post(
                f"{BASE_URL}/dispatches/confirm",
                headers=get_headers(),
                json=confirm_data
            )
            
            if response.status_code == 200:
                data = response.json()
                
                self.log_result(
                    "배차 확정",
                    True,
                    f"배차 확정 완료: 성공 {data.get('confirmed')}건, 실패 {data.get('failed')}건",
                    data
                )
                return data
            else:
                self.log_result(
                    "배차 확정",
                    False,
                    f"API 호출 실패: {response.status_code}",
                    response.text
                )
                return None
                
        except Exception as e:
            self.log_result("배차 확정", False, f"예외 발생: {str(e)}")
            return None
    
    # ========================================
    # 4. 통합 플로우 테스트
    # ========================================
    
    def run_full_test(self):
        """전체 플로우 통합 테스트"""
        print("\n" + "="*80)
        print("🚀 배차 플로우 통합 테스트 시작")
        print("="*80)
        
        # 1. 주문 관리
        orders = self.test_get_orders()
        pending_orders = self.test_get_pending_orders()
        
        # 배차 대기 주문이 없으면 테스트 주문 생성
        if len(pending_orders) == 0:
            print("\n⚠️  배차 대기 주문이 없습니다. 테스트 주문을 생성합니다.")
            new_order = self.test_create_order()
            if new_order:
                pending_orders = [new_order]
        
        # 2. AI 배차 최적화
        if pending_orders:
            order_ids = [o.get("id") for o in pending_orders if o.get("id")]
            
            # 기본 최적화
            opt_result = self.test_optimization(order_ids)
            
            # 고급 최적화
            adv_opt_result = self.test_advanced_optimization(order_ids)
        
        # 3. 배차 관리
        dispatches = self.test_get_dispatches()
        dashboard = self.test_dispatch_dashboard()
        
        # 4. 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약"""
        print("\n" + "="*80)
        print("📊 테스트 결과 요약")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\n총 테스트: {total_tests}개")
        print(f"✅ 성공: {passed_tests}개")
        print(f"❌ 실패: {failed_tests}개")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        
        # 실패한 테스트 상세
        if failed_tests > 0:
            print("\n⚠️  실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        print("\n" + "="*80)


def main():
    """메인 함수"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                 배차 플로우 통합 테스트                      ║
║                                                              ║
║  테스트 순서:                                                ║
║  1. 주문 관리 (목록 조회, 배차 대기 주문, 주문 생성)          ║
║  2. AI 배차 최적화 (기본 알고리즘, 고급 CVRPTW)               ║
║  3. 배차 관리 (목록 조회, 대시보드, 확정)                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    tester = DispatchFlowTester()
    
    # 인증 토큰이 필요한 경우 설정 (현재는 공개 API 테스트)
    # set_token("your_access_token_here")
    
    try:
        tester.run_full_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
