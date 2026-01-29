"""
실제 UVIS API 테스트 스크립트
"""
import httpx
import json
from datetime import datetime

# UVIS API 설정
UVIS_BASE_URL = "https://s1.u-vis.com/uvisc"
UVIS_SERIAL_KEY = "S1910-3A84-4559--CC4"


def test_issue_access_key():
    """실시간 인증키 발급 테스트"""
    print("\n" + "="*60)
    print("UVIS-001: 실시간 인증키 발급 테스트")
    print("="*60)
    
    url = f"{UVIS_BASE_URL}/InterfaceAction.do"
    params = {
        "method": "GetAccessKeyWithValues",
        "SerialKey": UVIS_SERIAL_KEY
    }
    
    print(f"\n📡 요청 URL: {url}")
    print(f"📋 요청 파라미터: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    try:
        client = httpx.Client(timeout=30.0)
        response = client.get(url, params=params)
        
        print(f"\n✅ 응답 상태: {response.status_code}")
        print(f"📥 응답 헤더:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print(f"\n📦 응답 본문 (원본):")
        print(response.text)
        
        # JSON 파싱 시도
        try:
            data = response.json()
            print(f"\n📊 JSON 파싱 결과:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # 응답이 배열인 경우 첫 번째 항목 사용
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            # 인증키 추출
            access_key = data.get("AccessKey") or data.get("access_key")
            if access_key:
                print(f"\n🔑 인증키 발급 성공: {access_key}")
                return access_key
            else:
                print(f"\n⚠️ 인증키를 찾을 수 없습니다.")
                print(f"응답 키 목록: {list(data.keys())}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSON 파싱 실패: {e}")
            print(f"응답이 JSON 형식이 아닙니다.")
            return None
            
    except httpx.TimeoutException:
        print(f"\n❌ 요청 시간 초과 (30초)")
        return None
    except httpx.RequestError as e:
        print(f"\n❌ 네트워크 오류: {e}")
        return None
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        return None
    finally:
        client.close()


def test_get_gps_data(access_key: str):
    """실시간 운행정보 조회 테스트"""
    print("\n" + "="*60)
    print("UVIS-002: 실시간 운행정보 조회 테스트")
    print("="*60)
    
    url = f"{UVIS_BASE_URL}/SSOAction.do"
    params = {
        "method": "getDeviceAPI",
        "AccessKey": access_key,
        "GUBUN": "01"
    }
    
    print(f"\n📡 요청 URL: {url}")
    print(f"📋 요청 파라미터: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    try:
        client = httpx.Client(timeout=30.0)
        response = client.get(url, params=params)
        
        print(f"\n✅ 응답 상태: {response.status_code}")
        print(f"\n📦 응답 본문 (원본, 처음 2000자):")
        print(response.text[:2000])
        
        # JSON 파싱 시도
        try:
            data = response.json()
            print(f"\n📊 JSON 파싱 성공")
            
            if isinstance(data, list):
                print(f"\n📈 총 {len(data)}건의 GPS 데이터")
                
                # 처음 3개만 출력
                for i, item in enumerate(data[:3]):
                    print(f"\n--- GPS 데이터 #{i+1} ---")
                    print(f"TID_ID: {item.get('TID_ID')}")
                    print(f"CM_NUMBER: {item.get('CM_NUMBER')}")
                    print(f"BI_DATE: {item.get('BI_DATE')}")
                    print(f"BI_TIME: {item.get('BI_TIME')}")
                    print(f"BI_X_POSITION (위도): {item.get('BI_X_POSITION')}")
                    print(f"BI_Y_POSITION (경도): {item.get('BI_Y_POSITION')}")
                    print(f"BI_GPS_SPEED (속도): {item.get('BI_GPS_SPEED')}")
                    print(f"BI_TURN_ONOFF (시동): {item.get('BI_TURN_ONOFF')}")
                    print(f"\n전체 필드:")
                    print(json.dumps(item, indent=2, ensure_ascii=False))
                    
            else:
                print(f"\n📊 GPS 데이터 (단일):")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            return data
            
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSON 파싱 실패: {e}")
            return None
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        return None
    finally:
        client.close()


def test_get_temperature_data(access_key: str):
    """실시간 온도정보 조회 테스트"""
    print("\n" + "="*60)
    print("UVIS-003: 실시간 온도정보 조회 테스트")
    print("="*60)
    
    url = f"{UVIS_BASE_URL}/SSOAction.do"
    params = {
        "method": "getDeviceAPI",
        "AccessKey": access_key,
        "GUBUN": "02"
    }
    
    print(f"\n📡 요청 URL: {url}")
    print(f"📋 요청 파라미터: {json.dumps(params, indent=2, ensure_ascii=False)}")
    
    try:
        client = httpx.Client(timeout=30.0)
        response = client.get(url, params=params)
        
        print(f"\n✅ 응답 상태: {response.status_code}")
        print(f"\n📦 응답 본문 (원본, 처음 2000자):")
        print(response.text[:2000])
        
        # JSON 파싱 시도
        try:
            data = response.json()
            print(f"\n📊 JSON 파싱 성공")
            
            if isinstance(data, list):
                print(f"\n📈 총 {len(data)}건의 온도 데이터")
                
                # 처음 3개만 출력
                for i, item in enumerate(data[:3]):
                    print(f"\n--- 온도 데이터 #{i+1} ---")
                    print(f"TID_ID: {item.get('TID_ID')}")
                    print(f"CM_NUMBER: {item.get('CM_NUMBER')}")
                    print(f"TPL_DATE: {item.get('TPL_DATE')}")
                    print(f"TPL_TIME: {item.get('TPL_TIME')}")
                    print(f"TPL_X_POSITION (위도): {item.get('TPL_X_POSITION')}")
                    print(f"TPL_Y_POSITION (경도): {item.get('TPL_Y_POSITION')}")
                    print(f"TPL_SIGNAL_A (온도A 부호): {item.get('TPL_SIGNAL_A')}")
                    print(f"TPL_DEGREE_A (온도A): {item.get('TPL_DEGREE_A')}")
                    print(f"TPL_SIGNAL_B (온도B 부호): {item.get('TPL_SIGNAL_B')}")
                    print(f"TPL_DEGREE_B (온도B): {item.get('TPL_DEGREE_B')}")
                    print(f"\n전체 필드:")
                    print(json.dumps(item, indent=2, ensure_ascii=False))
                    
            else:
                print(f"\n📊 온도 데이터 (단일):")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
            return data
            
        except json.JSONDecodeError as e:
            print(f"\n⚠️ JSON 파싱 실패: {e}")
            return None
            
    except Exception as e:
        print(f"\n❌ 예외 발생: {e}")
        return None
    finally:
        client.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔍 UVIS API 연동 테스트 시작")
    print(f"⏰ 테스트 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 1. 인증키 발급 테스트
    access_key = test_issue_access_key()
    
    if not access_key:
        print("\n❌ 인증키 발급 실패. 테스트 중단.")
        exit(1)
    
    # 2. GPS 데이터 조회 테스트
    gps_data = test_get_gps_data(access_key)
    
    # 3. 온도 데이터 조회 테스트
    temp_data = test_get_temperature_data(access_key)
    
    print("\n" + "="*60)
    print("✅ UVIS API 연동 테스트 완료")
    print("="*60)
    
    # 요약
    print("\n📊 테스트 요약:")
    print(f"  - 인증키 발급: {'✅ 성공' if access_key else '❌ 실패'}")
    print(f"  - GPS 데이터 조회: {'✅ 성공' if gps_data else '❌ 실패'}")
    print(f"  - 온도 데이터 조회: {'✅ 성공' if temp_data else '❌ 실패'}")
    
    if gps_data and isinstance(gps_data, list):
        print(f"\n📈 GPS 데이터 건수: {len(gps_data)}")
    
    if temp_data and isinstance(temp_data, list):
        print(f"📈 온도 데이터 건수: {len(temp_data)}")
