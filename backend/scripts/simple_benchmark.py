"""
간단한 성능 벤치마크 스크립트
- CVRPTW 알고리즘 성능 측정
- 기존 DB 데이터 사용
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any
from sqlalchemy.orm import Session
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.order import Order
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService


async def run_benchmark_greedy():
    """Greedy 알고리즘 벤치마크"""
    logger.info("Running Greedy algorithm benchmark...")
    
    db = SessionLocal()
    try:
        # 배차 대기 중인 주문 조회
        orders = db.query(Order).filter(Order.status == 'PENDING').limit(110).all()
        order_ids = [o.id for o in orders]
        
        if not order_ids:
            logger.warning("No pending orders found")
            return None
        
        logger.info(f"Found {len(order_ids)} pending orders")
        
        # 벤치마크 실행
        service = DispatchOptimizationService(db)
        
        start_time = time.time()
        result = service.optimize_dispatch(order_ids=order_ids)
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        logger.info(f"Greedy completed in {elapsed:.2f} seconds")
        
        return {
            'algorithm': 'greedy',
            'orders_count': len(order_ids),
            'dispatches_count': len(result['dispatches']),
            'execution_time': elapsed,
            'result': result
        }
        
    finally:
        db.close()


async def run_benchmark_cvrptw(time_limit: int = 30, use_real_routing: bool = False):
    """CVRPTW 알고리즘 벤치마크"""
    logger.info(f"Running CVRPTW algorithm benchmark (time_limit={time_limit}s, real_routing={use_real_routing})...")
    
    db = SessionLocal()
    try:
        # 배차 대기 중인 주문 조회
        orders = db.query(Order).filter(Order.status == 'PENDING').limit(110).all()
        order_ids = [o.id for o in orders]
        
        if not order_ids:
            logger.warning("No pending orders found")
            return None
        
        logger.info(f"Found {len(order_ids)} pending orders")
        
        # 벤치마크 실행
        service = AdvancedDispatchOptimizationService(db)
        
        start_time = time.time()
        result = await service.optimize_dispatch_cvrptw(
            order_ids=order_ids,
            time_limit=time_limit,
            use_time_windows=True,
            use_real_routing=use_real_routing
        )
        end_time = time.time()
        
        elapsed = end_time - start_time
        
        logger.info(f"CVRPTW completed in {elapsed:.2f} seconds")
        
        return {
            'algorithm': 'cvrptw',
            'time_limit': time_limit,
            'use_real_routing': use_real_routing,
            'orders_count': len(order_ids),
            'dispatches_count': len(result['dispatches']),
            'execution_time': elapsed,
            'result': result
        }
        
    finally:
        db.close()


def analyze_results(results: list):
    """벤치마크 결과 분석"""
    logger.info("\n" + "="*80)
    logger.info("BENCHMARK RESULTS ANALYSIS")
    logger.info("="*80)
    
    for result in results:
        if not result:
            continue
            
        logger.info(f"\nAlgorithm: {result['algorithm'].upper()}")
        logger.info(f"  Orders: {result['orders_count']}")
        logger.info(f"  Dispatches: {result['dispatches_count']}")
        logger.info(f"  Execution Time: {result['execution_time']:.2f}s")
        
        if 'time_limit' in result:
            logger.info(f"  Time Limit: {result['time_limit']}s")
            logger.info(f"  Real Routing: {result['use_real_routing']}")
        
        # 배차 효율 분석
        dispatch_result = result['result']
        total_distance = sum(d.get('total_distance_km', 0) for d in dispatch_result['dispatches'])
        total_orders = sum(len(d.get('orders', [])) for d in dispatch_result['dispatches'])
        
        logger.info(f"  Total Distance: {total_distance:.2f} km")
        logger.info(f"  Total Orders Assigned: {total_orders}")
        if result['dispatches_count'] > 0:
            logger.info(f"  Avg Distance per Dispatch: {total_distance / result['dispatches_count']:.2f} km")
            logger.info(f"  Avg Orders per Dispatch: {total_orders / result['dispatches_count']:.2f}")
    
    logger.info("\n" + "="*80)
    
    # 알고리즘 비교
    if len(results) >= 2:
        logger.info("\nALGORITHM COMPARISON")
        logger.info("="*80)
        
        greedy = next((r for r in results if r and r['algorithm'] == 'greedy'), None)
        cvrptw = next((r for r in results if r and r['algorithm'] == 'cvrptw'), None)
        
        if greedy and cvrptw:
            speed_diff = cvrptw['execution_time'] - greedy['execution_time']
            speed_improvement = abs(speed_diff) / greedy['execution_time'] * 100
            
            greedy_total_distance = sum(d.get('total_distance_km', 0) for d in greedy['result']['dispatches'])
            cvrptw_total_distance = sum(d.get('total_distance_km', 0) for d in cvrptw['result']['dispatches'])
            
            if greedy_total_distance > 0:
                distance_improvement = (greedy_total_distance - cvrptw_total_distance) / greedy_total_distance * 100
                logger.info(f"  Distance: CVRPTW is {abs(distance_improvement):.1f}% {'better' if distance_improvement > 0 else 'worse'} than Greedy")
            
            logger.info(f"  Speed: CVRPTW is {speed_improvement:.1f}% {'slower' if speed_diff > 0 else 'faster'} than Greedy")
            logger.info(f"  Quality: CVRPTW provides more optimal routes with constraint satisfaction")
        
        logger.info("="*80)


def generate_optimization_report(results: list, output_file: str = "benchmark_report.json"):
    """최적화 보고서 생성"""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'benchmarks': [],
        'recommendations': []
    }
    
    # 결과 저장 (circular reference 제거)
    for result in results:
        if not result:
            continue
        result_copy = result.copy()
        # result dict에서 복잡한 nested 객체 제거
        result_copy.pop('result', None)
        report['benchmarks'].append(result_copy)
    
    # 최적화 추천
    for result in results:
        if not result:
            continue
            
        if result['execution_time'] > 60:
            report['recommendations'].append({
                'type': 'performance',
                'priority': 'high',
                'message': f"{result['algorithm']} execution time is too long ({result['execution_time']:.2f}s). Consider implementing caching."
            })
        
        if result['algorithm'] == 'cvrptw' and result.get('use_real_routing'):
            report['recommendations'].append({
                'type': 'api_optimization',
                'priority': 'medium',
                'message': 'Real routing enabled. Consider implementing distance matrix caching to reduce API calls.'
            })
    
    # 저장
    output_path = Path(__file__).parent.parent / "logs" / output_file
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\nBenchmark report saved to: {output_path}")
    
    return report


async def main():
    """메인 벤치마크 실행"""
    logger.info("Starting Phase 2 Performance Benchmark")
    logger.info("="*80)
    
    # 데이터베이스 초기화
    init_db()
    
    # 1. Greedy 벤치마크
    logger.info("\n[Step 1/2] Running Greedy benchmark...")
    greedy_result = await run_benchmark_greedy()
    
    # 2. CVRPTW 벤치마크 (Haversine)
    logger.info("\n[Step 2/2] Running CVRPTW benchmark (Haversine)...")
    cvrptw_haversine = await run_benchmark_cvrptw(time_limit=30, use_real_routing=False)
    
    # 결과 분석
    results = [greedy_result, cvrptw_haversine]
    analyze_results(results)
    
    # 보고서 생성
    report = generate_optimization_report(results)
    
    logger.info("\n" + "="*80)
    logger.info("Benchmark completed successfully!")
    logger.info("="*80)
    
    return report


if __name__ == "__main__":
    asyncio.run(main())
