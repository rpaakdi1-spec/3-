"""
성능 벤치마크 및 최적화 스크립트
- Phase 2 테스트 데이터 업로드
- 벤치마크 실행
- 결과 분석 및 최적화 제안
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd
from sqlalchemy.orm import Session
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, init_db
from app.models.client import Client
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.services.excel_upload_service import ExcelUploadService
from app.services.dispatch_optimization_service import DispatchOptimizationService
from app.services.cvrptw_service import AdvancedDispatchOptimizationService


def upload_test_data():
    """Phase 2 테스트 데이터 업로드"""
    logger.info("Starting test data upload...")
    
    db = SessionLocal()
    try:
        # 기존 데이터 확인
        client_count = db.query(Client).count()
        vehicle_count = db.query(Vehicle).count()
        order_count = db.query(Order).count()
        
        logger.info(f"Current data: {client_count} clients, {vehicle_count} vehicles, {order_count} orders")
        
        # 테스트 데이터 경로
        test_data_dir = Path(__file__).parent.parent / "data" / "test_data"
        
        clients_file = test_data_dir / "clients_phase2.xlsx"
        vehicles_file = test_data_dir / "vehicles_phase2.xlsx"
        drivers_file = test_data_dir / "drivers_phase2.xlsx"
        orders_file = test_data_dir / "orders_phase2.xlsx"
        
        # 거래처 업로드
        if clients_file.exists():
            logger.info(f"Uploading clients from {clients_file}...")
            with open(clients_file, 'rb') as f:
                file_content = f.read()
            result = ExcelUploadService.upload_clients(db, file_content, auto_geocode=False)
            logger.info(f"Clients uploaded: {result}")
        
        # 차량 업로드
        if vehicles_file.exists():
            logger.info(f"Uploading vehicles from {vehicles_file}...")
            with open(vehicles_file, 'rb') as f:
                file_content = f.read()
            result = ExcelUploadService.upload_vehicles(db, file_content)
            logger.info(f"Vehicles uploaded: {result}")
        
        # 운전자 업로드 (drivers 테이블이 있다면)
        # if drivers_file.exists():
        #     logger.info(f"Uploading drivers from {drivers_file}...")
        #     with open(drivers_file, 'rb') as f:
        #         file_content = f.read()
        #     result = ExcelUploadService.upload_drivers(db, file_content)
        #     logger.info(f"Drivers uploaded: {result}")
        
        # 주문 업로드
        if orders_file.exists():
            logger.info(f"Uploading orders from {orders_file}...")
            with open(orders_file, 'rb') as f:
                file_content = f.read()
            result = ExcelUploadService.upload_orders(db, file_content)
            logger.info(f"Orders uploaded: {result}")
        
        # 최종 확인
        client_count = db.query(Client).count()
        vehicle_count = db.query(Vehicle).count()
        order_count = db.query(Order).count()
        
        logger.info(f"Final data: {client_count} clients, {vehicle_count} vehicles, {order_count} orders")
        
        return {
            'clients': client_count,
            'vehicles': vehicle_count,
            'orders': order_count
        }
        
    finally:
        db.close()


async def run_benchmark_greedy():
    """Greedy 알고리즘 벤치마크"""
    logger.info("Running Greedy algorithm benchmark...")
    
    db = SessionLocal()
    try:
        # 배차 대기 중인 주문 조회
        orders = db.query(Order).filter(Order.status == 'PENDING').all()
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
        orders = db.query(Order).filter(Order.status == 'PENDING').all()
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
        total_distance = sum(d['total_distance_km'] for d in dispatch_result['dispatches'])
        total_orders = sum(len(d['orders']) for d in dispatch_result['dispatches'])
        
        logger.info(f"  Total Distance: {total_distance:.2f} km")
        logger.info(f"  Total Orders Assigned: {total_orders}")
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
            speed_improvement = (greedy['execution_time'] - cvrptw['execution_time']) / greedy['execution_time'] * 100
            
            greedy_total_distance = sum(d['total_distance_km'] for d in greedy['result']['dispatches'])
            cvrptw_total_distance = sum(d['total_distance_km'] for d in cvrptw['result']['dispatches'])
            distance_improvement = (greedy_total_distance - cvrptw_total_distance) / greedy_total_distance * 100
            
            logger.info(f"  Speed: CVRPTW is {abs(speed_improvement):.1f}% {'faster' if speed_improvement > 0 else 'slower'} than Greedy")
            logger.info(f"  Distance: CVRPTW is {abs(distance_improvement):.1f}% {'better' if distance_improvement > 0 else 'worse'} than Greedy")
            logger.info(f"  Quality: CVRPTW provides more optimal routes with constraint satisfaction")
        
        logger.info("="*80)


def generate_optimization_report(results: list, output_file: str = "benchmark_report.json"):
    """최적화 보고서 생성"""
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'benchmarks': results,
        'recommendations': []
    }
    
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
    
    # 1. 테스트 데이터 업로드
    logger.info("\n[Step 1/4] Uploading test data...")
    data_stats = upload_test_data()
    logger.info(f"Test data uploaded: {data_stats}")
    
    # 2. Greedy 벤치마크
    logger.info("\n[Step 2/4] Running Greedy benchmark...")
    greedy_result = await run_benchmark_greedy()
    
    # 3. CVRPTW 벤치마크 (Haversine)
    logger.info("\n[Step 3/4] Running CVRPTW benchmark (Haversine)...")
    cvrptw_haversine = await run_benchmark_cvrptw(time_limit=30, use_real_routing=False)
    
    # 4. CVRPTW 벤치마크 (Real Routing) - 선택적
    # logger.info("\n[Step 4/4] Running CVRPTW benchmark (Real Routing)...")
    # cvrptw_real = await run_benchmark_cvrptw(time_limit=30, use_real_routing=True)
    
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
