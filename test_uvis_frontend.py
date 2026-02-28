#!/usr/bin/env python3
"""
Test script to verify UVIS Fleet Stats API response and component logic
"""
import json
import urllib.request
import sys

def fetch_api(url):
    """Fetch JSON data from API"""
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def analyze_stats(data):
    """Analyze fleet stats data"""
    if not data:
        return
    
    print("\n=== API Response Analysis ===")
    print(f"Total Vehicles: {data.get('total_vehicles', 0)}")
    print(f"Active Vehicles (API field): {data.get('active_vehicles', 0)}")
    print(f"Total Distance: {data.get('total_distance_km', 0)} km")
    print(f"Vehicle Stats Count: {len(data.get('vehicle_stats', []))}")
    
    vehicle_stats = data.get('vehicle_stats', [])
    
    if not vehicle_stats:
        print("\n⚠️  WARNING: No vehicle_stats returned!")
        return
    
    # Component logic: engineOnCount = vehicles with engine_on_ratio > 50
    engine_on_count = sum(1 for v in vehicle_stats if v.get('engine_on_ratio', 0) > 50)
    
    # Component logic: avgSpeed calculation
    avg_speeds = [v.get('avg_speed_kmh', 0) for v in vehicle_stats]
    avg_speed = sum(avg_speeds) / len(avg_speeds) if avg_speeds else 0
    
    # Component logic: maxSpeed calculation
    max_speeds = [v.get('max_speed_kmh', 0) for v in vehicle_stats]
    max_speed = max(max_speeds) if max_speeds else 0
    
    print("\n=== Component Calculated Values ===")
    print(f"운행 중 차량 (engine_on_ratio > 50): {engine_on_count} / {data.get('total_vehicles', 0)}대")
    print(f"총 주행 거리: {data.get('total_distance_km', 0):.1f} km")
    print(f"평균 속도: {avg_speed:.1f} km/h")
    print(f"최고 속도: {max_speed:.1f} km/h")
    
    print("\n=== Engine On Ratio Distribution ===")
    ratio_ranges = {
        '0-10%': 0,
        '11-30%': 0,
        '31-50%': 0,
        '51-70%': 0,
        '71-90%': 0,
        '91-100%': 0
    }
    
    for v in vehicle_stats:
        ratio = v.get('engine_on_ratio', 0)
        if ratio <= 10:
            ratio_ranges['0-10%'] += 1
        elif ratio <= 30:
            ratio_ranges['11-30%'] += 1
        elif ratio <= 50:
            ratio_ranges['31-50%'] += 1
        elif ratio <= 70:
            ratio_ranges['51-70%'] += 1
        elif ratio <= 90:
            ratio_ranges['71-90%'] += 1
        else:
            ratio_ranges['91-100%'] += 1
    
    for range_name, count in ratio_ranges.items():
        print(f"  {range_name}: {count} vehicles")
    
    print("\n=== Sample Vehicle Data (first 5) ===")
    for i, v in enumerate(vehicle_stats[:5], 1):
        print(f"{i}. Vehicle {v.get('vehicle_id')} ({v.get('vehicle_plate')})")
        print(f"   Distance: {v.get('total_distance_km', 0):.2f} km")
        print(f"   Max Speed: {v.get('max_speed_kmh', 0):.1f} km/h")
        print(f"   Avg Speed: {v.get('avg_speed_kmh', 0):.1f} km/h")
        print(f"   Engine On: {v.get('engine_on_ratio', 0):.1f}%")
        print(f"   Data Points: {v.get('data_points', 0)}")

if __name__ == '__main__':
    # Test different date ranges
    base_url = "http://localhost:8000/api/v1/vehicles/analytics/fleet"
    
    test_cases = [
        ("Today (2026-02-28)", "2026-02-28", "2026-02-28"),
        ("Yesterday (2026-02-27)", "2026-02-27", "2026-02-27"),
        ("Last 7 days", "2026-02-21", "2026-02-28"),
    ]
    
    for name, start, end in test_cases:
        url = f"{base_url}?start_date={start}&end_date={end}"
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"URL: {url}")
        print('='*60)
        
        data = fetch_api(url)
        if data:
            analyze_stats(data)
