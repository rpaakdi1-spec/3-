"""
성능 벤치마크 스크립트
- 다양한 규모의 배차 최적화 테스트
- 실행 시간, 메모리 사용량, 최적화 품질 측정
"""

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import time
import psutil
import json
from datetime import datetime, date
from typing import Dict, Any, List
from loguru import logger

from app.core.database import SessionLocal
from app.models.order import Order, OrderStatus
from app.models.vehicle import Vehicle, VehicleStatus
from app.services.cvrptw_service import AdvancedDispatchOptimizationService
from app.services.dispatch_optimization_service import DispatchOptimizationService


class PerformanceBenchmark:
    """성능 벤치마크 도구"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.results = []
        
    def get_memory_usage(self) -> float:
        """현재 메모리 사용량 (MB)"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    async def benchmark_scenario(
        self,
        scenario_name: str,
        order_count: int,
        vehicle_count: int,
        algorithm: str,
        use_time_windows: bool = True,
        use_real_routing: bool = False,
        time_limit: int = 30
    ) -> Dict[str, Any]:
        """
        벤치마크 시나리오 실행
        
        Args:
            scenario_name: 시나리오 이름
            order_count: 주문 수
            vehicle_count: 차량 수
            algorithm: 'greedy' or 'cvrptw'
            use_time_windows: 시간 제약 사용
            use_real_routing: Naver API 사용
            time_limit: 최대 실행 시간 (초)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"시나리오: {scenario_name}")
        logger.info(f"주문: {order_count}건, 차량: {vehicle_count}대")
        logger.info(f"알고리즘: {algorithm.upper()}, 시간 제약: {use_time_windows}, 실제 경로: {use_real_routing}")
        logger.info(f"{'='*60}\n")
        
        # 주문 및 차량 조회
        orders = self.db.query(Order).filter(
            Order.status == OrderStatus.PENDING
        ).limit(order_count).all()
        
        if len(orders) < order_count:
            logger.warning(f"주문 부족: {len(orders)}건 (요청: {order_count}건)")
            order_count = len(orders)
        
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.status == VehicleStatus.AVAILABLE
        ).limit(vehicle_count).all()
        
        if len(vehicles) < vehicle_count:
            logger.warning(f"차량 부족: {len(vehicles)}대 (요청: {vehicle_count}대)")
            vehicle_count = len(vehicles)
        
        order_ids = [o.id for o in orders]
        vehicle_ids = [v.id for v in vehicles]
        
        # 메모리 측정 시작
        mem_before = self.get_memory_usage()
        
        # 시간 측정 시작
        start_time = time.time()
        
        try:
            # 알고리즘 실행
            if algorithm == 'greedy':
                optimizer = DispatchOptimizationService(self.db)
                result = await optimizer.optimize_dispatch(
                    order_ids=order_ids,
                    vehicle_ids=vehicle_ids,
                    dispatch_date=str(date.today())
                )
            else:  # cvrptw
                optimizer = AdvancedDispatchOptimizationService(self.db)
                result = await optimizer.optimize_dispatch_cvrptw(
                    order_ids=order_ids,
                    vehicle_ids=vehicle_ids,
                    dispatch_date=str(date.today()),
                    time_limit_seconds=time_limit,
                    use_time_windows=use_time_windows,
                    use_real_routing=use_real_routing
                )
            
            # 시간 측정 종료
            execution_time = time.time() - start_time
            
            # 메모리 측정 종료
            mem_after = self.get_memory_usage()
            mem_used = mem_after - mem_before
            
            # 결과 분석
            success = result.get('success', False)
            total_dispatches = result.get('total_dispatches', 0)
            total_distance_km = result.get('total_distance_km', 0)
            
            # 최적화율 계산 (간단한 baseline 대비)
            baseline_distance = order_count * 50  # 가정: 주문당 평균 50km
            optimization_rate = (1 - total_distance_km / baseline_distance) * 100 if baseline_distance > 0 else 0
            
            benchmark_result = {
                'timestamp': datetime.now().isoformat(),
                'scenario': scenario_name,
                'algorithm': algorithm,
                'order_count': order_count,
                'vehicle_count': vehicle_count,
                'use_time_windows': use_time_windows,
                'use_real_routing': use_real_routing,
                'time_limit': time_limit,
                'success': success,
                'execution_time_sec': round(execution_time, 2),
                'memory_used_mb': round(mem_used, 2),
                'total_dispatches': total_dispatches,
                'total_distance_km': round(total_distance_km, 2),
                'optimization_rate': round(optimization_rate, 2),
                'avg_orders_per_vehicle': round(order_count / total_dispatches, 2) if total_dispatches > 0 else 0,
                'temperature_zones': result.get('temperature_zones', [])
            }
            
            logger.success(f"✓ 실행 완료: {execution_time:.2f}초")
            logger.info(f"  - 메모리: {mem_used:.2f} MB")
            logger.info(f"  - 배차: {total_dispatches}개")
            logger.info(f"  - 거리: {total_distance_km:.2f} km")
            logger.info(f"  - 최적화율: {optimization_rate:.2f}%")
            
            self.results.append(benchmark_result)
            return benchmark_result
            
        except Exception as e:
            logger.error(f"✗ 벤치마크 실패: {e}")
            execution_time = time.time() - start_time
            
            error_result = {
                'timestamp': datetime.now().isoformat(),
                'scenario': scenario_name,
                'algorithm': algorithm,
                'order_count': order_count,
                'vehicle_count': vehicle_count,
                'success': False,
                'execution_time_sec': round(execution_time, 2),
                'error': str(e)
            }
            
            self.results.append(error_result)
            return error_result
    
    async def run_all_benchmarks(self):
        """모든 벤치마크 시나리오 실행"""
        logger.info("\n" + "="*80)
        logger.info("성능 벤치마크 시작")
        logger.info("="*80 + "\n")
        
        scenarios = [
            # 소규모 테스트
            {
                'name': '소규모 - Greedy',
                'order_count': 20,
                'vehicle_count': 5,
                'algorithm': 'greedy',
                'use_time_windows': False,
                'use_real_routing': False,
                'time_limit': 10
            },
            {
                'name': '소규모 - CVRPTW (Haversine)',
                'order_count': 20,
                'vehicle_count': 5,
                'algorithm': 'cvrptw',
                'use_time_windows': True,
                'use_real_routing': False,
                'time_limit': 10
            },
            
            # 중규모 테스트
            {
                'name': '중규모 - Greedy',
                'order_count': 50,
                'vehicle_count': 20,
                'algorithm': 'greedy',
                'use_time_windows': False,
                'use_real_routing': False,
                'time_limit': 20
            },
            {
                'name': '중규모 - CVRPTW (Haversine)',
                'order_count': 50,
                'vehicle_count': 20,
                'algorithm': 'cvrptw',
                'use_time_windows': True,
                'use_real_routing': False,
                'time_limit': 20
            },
            
            # 대규모 테스트
            {
                'name': '대규모 - Greedy',
                'order_count': 110,
                'vehicle_count': 40,
                'algorithm': 'greedy',
                'use_time_windows': False,
                'use_real_routing': False,
                'time_limit': 30
            },
            {
                'name': '대규모 - CVRPTW (Haversine)',
                'order_count': 110,
                'vehicle_count': 40,
                'algorithm': 'cvrptw',
                'use_time_windows': True,
                'use_real_routing': False,
                'time_limit': 30
            },
            
            # Naver API 테스트 (선택적 - 비용 발생)
            # {
            #     'name': '중규모 - CVRPTW (Naver API)',
            #     'order_count': 50,
            #     'vehicle_count': 20,
            #     'algorithm': 'cvrptw',
            #     'use_time_windows': True,
            #     'use_real_routing': True,
            #     'time_limit': 60
            # },
        ]
        
        for scenario in scenarios:
            await self.benchmark_scenario(**scenario)
            await asyncio.sleep(2)  # 시나리오 간 쿨다운
        
        # 결과 요약
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """벤치마크 결과 요약 출력"""
        logger.info("\n" + "="*80)
        logger.info("벤치마크 결과 요약")
        logger.info("="*80 + "\n")
        
        # 테이블 헤더
        header = f"{'시나리오':<30} {'주문':<6} {'차량':<6} {'시간(s)':<10} {'메모리(MB)':<12} {'배차':<6} {'거리(km)':<10}"
        logger.info(header)
        logger.info("-" * 80)
        
        # 결과 출력
        for result in self.results:
            if result['success']:
                row = (
                    f"{result['scenario']:<30} "
                    f"{result['order_count']:<6} "
                    f"{result['vehicle_count']:<6} "
                    f"{result['execution_time_sec']:<10.2f} "
                    f"{result.get('memory_used_mb', 0):<12.2f} "
                    f"{result['total_dispatches']:<6} "
                    f"{result['total_distance_km']:<10.2f}"
                )
                logger.info(row)
            else:
                logger.error(f"{result['scenario']:<30} FAILED: {result.get('error', 'Unknown')}")
        
        logger.info("\n" + "="*80)
        
        # 알고리즘 비교
        logger.info("\n알고리즘 비교 (대규모 기준)")
        greedy_large = next((r for r in self.results if '대규모 - Greedy' in r['scenario'] and r['success']), None)
        cvrptw_large = next((r for r in self.results if '대규모 - CVRPTW' in r['scenario'] and r['success']), None)
        
        if greedy_large and cvrptw_large:
            logger.info(f"\nGreedy:")
            logger.info(f"  - 실행 시간: {greedy_large['execution_time_sec']:.2f}초")
            logger.info(f"  - 배차 수: {greedy_large['total_dispatches']}개")
            logger.info(f"  - 총 거리: {greedy_large['total_distance_km']:.2f} km")
            
            logger.info(f"\nCVRPTW:")
            logger.info(f"  - 실행 시간: {cvrptw_large['execution_time_sec']:.2f}초")
            logger.info(f"  - 배차 수: {cvrptw_large['total_dispatches']}개")
            logger.info(f"  - 총 거리: {cvrptw_large['total_distance_km']:.2f} km")
            
            time_diff = ((cvrptw_large['execution_time_sec'] - greedy_large['execution_time_sec']) / greedy_large['execution_time_sec'] * 100)
            distance_diff = ((greedy_large['total_distance_km'] - cvrptw_large['total_distance_km']) / greedy_large['total_distance_km'] * 100)
            
            logger.info(f"\n개선율:")
            logger.info(f"  - 실행 시간: {time_diff:+.1f}% (느림)" if time_diff > 0 else f"  - 실행 시간: {abs(time_diff):.1f}% (빠름)")
            logger.info(f"  - 총 거리: {distance_diff:+.1f}% (개선)")
    
    def save_results(self):
        """결과를 JSON 파일로 저장"""
        output_dir = Path(__file__).parent.parent / "data" / "benchmarks"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_dir / f"benchmark_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        logger.success(f"\n✓ 벤치마크 결과 저장: {filename}")
    
    def cleanup(self):
        """리소스 정리"""
        self.db.close()


async def main():
    """메인 실행 함수"""
    benchmark = PerformanceBenchmark()
    
    try:
        await benchmark.run_all_benchmarks()
    except Exception as e:
        logger.error(f"벤치마크 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()
    finally:
        benchmark.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
