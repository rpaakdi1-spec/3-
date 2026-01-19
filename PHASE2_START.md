# 🚀 Phase 2 Pilot 시작 - Week 1

**시작일**: 2026-01-19  
**현재 진행**: Week 1 - Day 1  
**완료 작업**: 실제 규모 테스트 데이터 생성

---

## ✅ 완료된 작업 (Day 1)

### 1. Phase 2 계획 수립
- **문서**: PHASE2_PLAN.md
- **기간**: 8주 (2026-01-19 ~ 2026-03-15)
- **주요 목표**:
  - 실제 규모 테스트 (40대 / 110건)
  - 고급 VRP 알고리즘 (CVRPTW)
  - Samsung UVIS 연동
  - 실시간 대시보드

### 2. 실제 규모 테스트 데이터 생성 ✅
**위치**: `/backend/data/test_data/`

#### 생성된 파일:
- `clients_phase2.xlsx`: 100개 거래처
- `vehicles_phase2.xlsx`: 40대 차량
- `drivers_phase2.xlsx`: 40명 운전자
- `orders_phase2.xlsx`: 110건 주문

#### 데이터 분포:

**차량 (40대)**
```
온도대별:
- 냉동 차량: 18대 (45%)
  └─ 5톤: 10대, 3.5톤: 8대
  └─ 팔레트 용량: 12-14 / 8-10개
  
- 냉장 차량: 16대 (40%)
  └─ 5톤: 9대, 3.5톤: 7대
  └─ 팔레트 용량: 12-14 / 8-10개
  
- 상온 차량: 6대 (15%)
  └─ 5톤: 4대, 3.5톤: 2대
  └─ 팔레트 용량: 12-14 / 8-10개
```

**주문 (110건)**
```
온도대별:
- 냉동: 50건 (45%)
- 냉장: 44건 (40%)
- 상온: 16건 (15%)

팔레트 수별:
- 소량 (1-3 팔레트): 40건
- 중량 (4-7 팔레트): 50건
- 대량 (8-12 팔레트): 20건

시간대별:
- 오전 (08:00-12:00): 40건
- 오후 (13:00-17:00): 50건
- 야간 (18:00-22:00): 20건
```

**거래처 (100개)**
```
지역별:
- 서울: 약 50개
  └─ 강남, 강서, 송파, 서초, 마포, 성동, 광진 등
  
- 경기: 약 50개
  └─ 고양, 성남, 수원 등

구분:
- 상차/하차 양쪽: 33%
- 상차만: 33%
- 하차만: 34%
```

---

## 📊 Phase 1 vs Phase 2 비교

| 항목 | Phase 1 PoC | Phase 2 Pilot | 증가율 |
|------|-------------|---------------|--------|
| 차량 수 | 5대 | 40대 | **8배** |
| 주문 수 | 20건 | 110건 | **5.5배** |
| 거래처 수 | 10개 | 100개 | **10배** |
| 배차 복잡도 | 낮음 | **높음** | - |
| 알고리즘 | Greedy | **CVRPTW** | - |
| 거리 계산 | Haversine | **Naver API** | - |
| GPS 추적 | 없음 | **UVIS 연동** | - |

---

## 🎯 다음 작업 (Week 1 - Day 2-7)

### 우선순위 1: Naver Directions API 연동 (Day 2-4)
```python
# NaverMapService 확장
- get_directions(): 경로 탐색
- get_distance_matrix(): 거리 행렬 생성
- get_route_geometry(): 경로 좌표 조회
- batch_processing(): 배치 처리 최적화
```

**목표**:
- Haversine 직선거리 → 실제 도로 거리
- 소요 시간 정확도 향상
- 경로 시각화 준비

### 우선순위 2: 고급 VRP 알고리즘 구현 (Day 5-7)
```python
# DispatchOptimizationService 고도화
- CVRPTW 기본 구조
- 제약 조건:
  * Hard: 용량, 온도대, 시간창
  * Soft: 거리, 균등 배분
- 검색 전략: PATH_CHEAPEST_ARC
- 메타휴리스틱: GUIDED_LOCAL_SEARCH
```

**목표**:
- 배차 최적화율 85% 이상
- 실행 시간 < 30초 (40대/110건)
- 현실적인 경로 생성

---

## 📂 프로젝트 구조 (Phase 2)

```
webapp/
├── backend/
│   ├── app/
│   │   ├── api/              # API 엔드포인트
│   │   ├── core/             # 설정, DB
│   │   ├── models/           # 데이터 모델
│   │   ├── schemas/          # Pydantic 스키마
│   │   └── services/         # 비즈니스 로직
│   │       ├── excel_template_service.py
│   │       ├── excel_upload_service.py
│   │       ├── naver_map_service.py      ← 확장 예정
│   │       ├── dispatch_optimization_service.py ← 고도화 예정
│   │       └── uvis_service.py           ← 신규 생성 예정
│   ├── data/
│   │   ├── templates/        # Excel 템플릿
│   │   └── test_data/        # 테스트 데이터 ✅ NEW
│   └── scripts/              # 유틸리티 스크립트 ✅ NEW
│       ├── generate_phase2_data.py
│       └── generate_test_data.py
├── frontend/
│   └── src/
│       ├── components/       # React 컴포넌트
│       └── services/         # API 클라이언트
├── docs/
│   ├── PHASE1_COMPLETE.md
│   └── PHASE2_PLAN.md        ✅ NEW
└── tests/                    # 테스트 (Phase 2)
```

---

## 🔧 개발 환경

### 백엔드 (Python)
```bash
cd /home/user/webapp/backend
source venv/bin/activate

# 테스트 데이터 생성
python scripts/generate_phase2_data.py

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 프론트엔드 (Node.js)
```bash
cd /home/user/webapp/frontend
npm install
npm run dev
```

### 실행 중인 서비스
- 백엔드: https://8000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai
- 프론트엔드: https://3002-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai

---

## 📈 Week 1 목표 (일정)

### Day 1 (2026-01-19) ✅
- [x] Phase 2 계획 수립
- [x] 테스트 데이터 생성 (40/110/100)

### Day 2-4 (2026-01-20 ~ 2026-01-22)
- [ ] Naver Directions API 연동
- [ ] 거리 매트릭스 생성
- [ ] 배치 처리 최적화
- [ ] 캐싱 전략 구현

### Day 5-7 (2026-01-23 ~ 2026-01-25)
- [ ] OR-Tools CVRPTW 기본 구조
- [ ] 제약 조건 정의
- [ ] Distance Callback 함수
- [ ] 초기 테스트 (5대/20건)

---

## 📊 성능 목표

### 배차 최적화
- **실행 시간**: < 30초 (40대/110건)
- **최적화율**: > 85% (수동 배차 대비)
- **공차율 감소**: > 50%

### API 성능
- **응답 시간**: < 200ms (95 percentile)
- **처리량**: > 100 req/sec

### 시스템 안정성
- **가용성**: > 99.5%
- **에러율**: < 1%

---

## 🎓 학습 자료

### Week 1 관련 기술
- [Google OR-Tools VRP Guide](https://developers.google.com/optimization/routing/vrp)
- [Naver Directions API](https://api.ncloud-docs.com/docs/ai-naver-mapsdirections5)
- [CVRPTW 알고리즘](https://en.wikipedia.org/wiki/Vehicle_routing_problem)

### 참고 논문
- "Vehicle Routing Problem with Time Windows" (Solomon, 1987)
- "The Vehicle Routing Problem" (Toth & Vigo, 2002)

---

## 💡 이번 주 핵심 과제

### 1. 실제 경로 vs 직선거리
```python
# Before (Phase 1)
distance_km = haversine(lat1, lon1, lat2, lon2)

# After (Phase 2)
distance_km, duration_min = naver_map_service.get_directions(
    start=(lat1, lon1),
    goal=(lat2, lon2)
)
```

### 2. 거리 행렬 캐싱
```python
# 100개 거래처 → 10,000개 경로 조합
# 매번 API 호출 → 비용/시간 증가
# 해결: Redis 캐싱 (24시간)

cache_key = f"distance:{client1_id}:{client2_id}"
redis.setex(cache_key, 86400, json.dumps(result))
```

### 3. VRP 알고리즘 고도화
```python
# Phase 1: Greedy (간단, 빠름, 정확도 낮음)
# Phase 2: CVRPTW (복잡, 느림, 정확도 높음)

# OR-Tools 파라미터 튜닝:
- first_solution_strategy
- local_search_metaheuristic  
- time_limit_seconds
- solution_limit
```

---

## 🔐 보안 고려사항

### API 키 관리
- Naver Map API: .env 파일
- UVIS API: 환경 변수
- Redis: 비밀번호 설정

### 데이터 보호
- 테스트 데이터: 실제 정보 제외
- 로그: 민감 정보 마스킹
- 백업: 암호화 저장

---

## 📞 지원

### Git 저장소
```bash
cd /home/user/webapp
git log --oneline | head -5
```

최근 커밋:
- e094a2f: feat: Generate Phase 2 test data
- 2675513: docs: Add comprehensive deployment status guide
- 75f5b07: fix: Configure Vite to allow sandbox hosts

### 문의
- Phase 2 계획서: `PHASE2_PLAN.md`
- 테스트 데이터: `backend/data/test_data/`
- 생성 스크립트: `backend/scripts/generate_phase2_data.py`

---

**작성일**: 2026-01-19  
**작성자**: AI Development Team  
**다음 업데이트**: Week 1 Day 7 (2026-01-25)  
**상태**: 🚀 In Progress

---

*"Phase 1의 기반 위에 Phase 2의 혁신을 쌓아가겠습니다."*
