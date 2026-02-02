#!/usr/bin/env python3
"""
Phase 2: Historical Data Simulation Script

서버 배포 후 과거 데이터로 ML 배차 시뮬레이션을 실행합니다.

Usage:
    cd /home/user/webapp
    python backend/tests/phase2_simulation.py --date 2026-02-01
    python backend/tests/phase2_simulation.py --start 2026-02-01 --end 2026-02-07
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
import requests
from typing import Optional
from tabulate import tabulate

# API 기본 설정
API_BASE_URL = os.getenv("API_BASE_URL", "http://139.150.11.99:8000")
API_TOKEN = os.getenv("API_TOKEN", None)  # 실제 환경에서 설정


def authenticate(base_url: str) -> Optional[str]:
    """API 인증"""
    # 테스트용: 기본 관리자 계정으로 로그인
    print("🔐 Authenticating...")
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "username": "admin",  # 실제 계정 정보로 수정 필요
                "password": "admin123"
            }
        )
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None


def run_simulation(
    base_url: str,
    token: str,
    target_date: str
) -> dict:
    """단일 날짜 시뮬레이션 실행"""
    
    print(f"\n📊 Simulating dispatch for {target_date}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{base_url}/api/ml-dispatch/simulate",
            params={"target_date": target_date},
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Simulation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        return None


def print_simulation_results(result: dict):
    """시뮬레이션 결과 출력"""
    
    if not result:
        print("❌ No results to display")
        return
    
    print("\n" + "="*80)
    print(f"📅 Date: {result['date']}")
    print("="*80)
    
    # 기본 통계
    print(f"\n📦 Orders:")
    print(f"  - Total: {result['total_orders']}")
    print(f"  - Simulated: {result['simulated_orders']}")
    print(f"  - ML Match Rate: {result['ml_match_rate']:.1%} ({result['ml_matches']}/{result['simulated_orders']})")
    
    # 성능 메트릭
    if 'performance_metrics' in result:
        metrics = result['performance_metrics']
        print(f"\n🎯 Performance Metrics:")
        print(f"  - Average Score: {metrics.get('avg_score', 0):.3f}")
        
        if 'score_distribution' in metrics:
            dist = metrics['score_distribution']
            print(f"  - Score Distribution:")
            print(f"      High (≥0.7): {dist['high']}")
            print(f"      Medium (0.5-0.7): {dist['medium']}")
            print(f"      Low (<0.5): {dist['low']}")
        
        if 'agent_averages' in metrics:
            print(f"  - Agent Averages:")
            for agent, score in metrics['agent_averages'].items():
                print(f"      {agent}: {score:.3f}")
    
    # 상위 10개 비교
    comparisons = result.get('comparisons', [])
    if comparisons:
        print(f"\n🔍 Top 10 Comparisons:")
        
        table_data = []
        for comp in comparisons[:10]:
            ml_rec = comp['ml_recommendation']
            actual = comp.get('actual_dispatch')
            
            row = [
                comp['order_number'],
                comp['temperature_zone'],
                comp['pallet_count'],
                ml_rec['vehicle_code'],
                f"{ml_rec['score']:.3f}",
                actual['vehicle_code'] if actual else "N/A",
                "✅" if comp['match'] else "❌"
            ]
            table_data.append(row)
        
        headers = ["Order", "Temp", "Pallets", "ML Rec", "Score", "Actual", "Match"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


def run_period_simulation(
    base_url: str,
    token: str,
    start_date: str,
    end_date: str
):
    """기간별 시뮬레이션 실행"""
    
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    print(f"\n📅 Period Simulation: {start_date} to {end_date}")
    print("="*80)
    
    current_dt = start_dt
    all_results = []
    
    while current_dt <= end_dt:
        date_str = current_dt.strftime("%Y-%m-%d")
        result = run_simulation(base_url, token, date_str)
        
        if result:
            all_results.append(result)
            print(f"✅ {date_str}: {result['simulated_orders']} orders, {result['ml_match_rate']:.1%} match rate")
        else:
            print(f"❌ {date_str}: Simulation failed")
        
        current_dt += timedelta(days=1)
    
    # 전체 요약
    if all_results:
        print("\n" + "="*80)
        print("📊 Period Summary")
        print("="*80)
        
        total_orders = sum(r['simulated_orders'] for r in all_results)
        total_matches = sum(r['ml_matches'] for r in all_results)
        avg_match_rate = total_matches / total_orders if total_orders > 0 else 0.0
        
        avg_score = sum(
            r['performance_metrics'].get('avg_score', 0)
            for r in all_results
        ) / len(all_results)
        
        print(f"  - Total Days: {len(all_results)}")
        print(f"  - Total Orders: {total_orders}")
        print(f"  - Total Matches: {total_matches}")
        print(f"  - Overall Match Rate: {avg_match_rate:.1%}")
        print(f"  - Average ML Score: {avg_score:.3f}")
        
        # 일별 요약 테이블
        print(f"\n📅 Daily Summary:")
        table_data = []
        for result in all_results:
            row = [
                result['date'],
                result['simulated_orders'],
                f"{result['ml_match_rate']:.1%}",
                f"{result['performance_metrics'].get('avg_score', 0):.3f}"
            ]
            table_data.append(row)
        
        headers = ["Date", "Orders", "Match Rate", "Avg Score"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2: ML Dispatch Historical Simulation"
    )
    
    parser.add_argument(
        "--date",
        type=str,
        help="Target date for simulation (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--start",
        type=str,
        help="Start date for period simulation (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--end",
        type=str,
        help="End date for period simulation (YYYY-MM-DD)"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        default="http://139.150.11.99:8000",
        help="API base URL"
    )
    
    args = parser.parse_args()
    
    # 인증
    token = authenticate(args.url)
    if not token:
        print("\n❌ Cannot proceed without authentication")
        sys.exit(1)
    
    # 시뮬레이션 실행
    if args.date:
        # 단일 날짜
        result = run_simulation(args.url, token, args.date)
        if result:
            print_simulation_results(result)
    
    elif args.start and args.end:
        # 기간별
        run_period_simulation(args.url, token, args.start, args.end)
    
    else:
        print("❌ Please specify either --date or (--start and --end)")
        parser.print_help()
        sys.exit(1)
    
    print("\n✅ Simulation complete!\n")


if __name__ == "__main__":
    main()
