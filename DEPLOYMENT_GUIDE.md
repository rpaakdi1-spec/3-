# 📦 CSV 템플릿 관리 시스템 배포 가이드

## ✅ 생성된 파일

```
/home/user/webapp/
├── csv_to_sql.py          # CSV → SQL 변환 스크립트
├── templates.csv          # 샘플 템플릿 데이터
├── apply_templates.sh     # 템플릿 적용 스크립트
├── TEMPLATES_README.md    # 사용자 가이드
└── DEPLOYMENT_GUIDE.md    # 이 문서
```

## 🚀 서버 배포 방법

### 1️⃣ 파일을 서버로 복사

```bash
# 로컬에서 실행
scp csv_to_sql.py templates.csv apply_templates.sh TEMPLATES_README.md \
    root@139.150.11.99:/root/uvis/
```

또는 한 번에 tar로 묶어서:

```bash
cd /home/user/webapp
tar -czf template_manager.tar.gz csv_to_sql.py templates.csv apply_templates.sh TEMPLATES_README.md
scp template_manager.tar.gz root@139.150.11.99:/root/uvis/
ssh root@139.150.11.99 'cd /root/uvis && tar -xzf template_manager.tar.gz'
```

### 2️⃣ 서버에서 실행 권한 부여

```bash
ssh root@139.150.11.99
cd /root/uvis
chmod +x csv_to_sql.py apply_templates.sh
```

### 3️⃣ 템플릿 적용

```bash
cd /root/uvis
bash apply_templates.sh
# 또는 직접 적용:
python3 csv_to_sql.py templates.csv | docker compose exec -T db psql -U uvis_user -d uvis_db
```

## 📝 현재 템플릿 목록

| 템플릿명 | 상차거래처 | 하차거래처 | 카테고리 | 시간 | 팔레트 | 온도 | 하차완료 |
|---------|-----------|-----------|---------|------|--------|------|----------|
| 김제 한우물 → 오산센터 | 한우물 | 오산동원 | 새벽배차 | 06:00 | 16p | 냉동 | 10:00 |
| 정읍 부엉이 → 백암 웰빙 | 정읍 부엉이 | 백암 웰빙 | 아침배차 | 08:30 | 16p | 냉동 | 13:30 |
| 목우촌 오후배차 1 | 목우촌 | 목우촌 안성센터 | 오후배차 | 13:00 | 18p | 냉동 | 17:00 |

## 🧪 테스트 절차

### 1. CSV → SQL 변환 테스트

```bash
python3 csv_to_sql.py templates.csv > /tmp/test.sql
cat /tmp/test.sql | head -n 50
```

### 2. 데이터베이스 확인

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    id,
    client_name AS 거래처,
    name AS 템플릿명,
    category AS 카테고리,
    template_data->'dispatches'->0->>'time' AS 시간,
    template_data->'dispatches'->0->>'pallet_count' AS 팔레트,
    template_data->'dispatches'->0->>'temperature' AS 온도
FROM dispatch_form_templates
ORDER BY client_name, name;"
```

### 3. 브라우저 테스트

1. http://139.150.11.99/orders 접속
2. **일괄 등록** 버튼 클릭
3. **템플릿 불러오기** 선택
4. 거래처 선택: **한우물**
5. 템플릿 선택: **김제 한우물 → 오산센터**
6. 자동 입력 확인:
   - 상차지: `전북 김제시 용지면 부교리 87-10`
   - 하차지: `경기도 화성시 정남면 가장로 285`
   - 배차 정보: `**3/5(목)한우물 새벽배차**\n06:00 / 냉동16p`
7. **파싱하기** 클릭
8. 파싱 결과 확인:
   - 날짜: 2026-03-06
   - 시간: 06:00
   - 품목: 냉동식품 11톤
   - 팔레트: 16p
   - 온도: 냉동
   - 상차지: 전북 김제시 용지면 부교리 87-10 (좌표 표시)
   - 하차지: 경기도 화성시 정남면 가장로 285 (좌표 표시)
9. **1건 등록하기** 클릭
10. 성공 메시지 확인
11. **AI 배차** 테스트:
    - 방금 등록한 배차 선택
    - **AI 배차** 버튼 클릭
    - 거리 약 230km, 예상 시간 3-4시간 표시 확인
    - 적합 차량 목록 표시 확인

## 📊 새 템플릿 추가 예시

### templates.csv에 행 추가:

```csv
김제 한우물 → 부산센터,한우물,부산 냉장,아침배차,08:00,18,냉장,전북 김제시 용지면 부교리 87-10,35.803456,126.878901,부산광역시 강서구 명지동 123,35.123456,129.012345,13:00,2공장
```

### 적용:

```bash
bash apply_templates.sh
```

## 🔧 유지보수 명령어

### 전체 템플릿 조회

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT id, client_name, name, category
FROM dispatch_form_templates
ORDER BY client_name, name;"
```

### 특정 템플릿 상세 조회

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    name,
    client_name,
    category,
    description,
    template_data::text,
    is_active,
    created_at
FROM dispatch_form_templates
WHERE client_name = '한우물'
  AND name = '김제 한우물 → 오산센터';"
```

### 템플릿 삭제

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
DELETE FROM dispatch_form_templates
WHERE name = '김제 한우물 → 오산센터'
  AND client_name = '한우물';"
```

### 템플릿 비활성화

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
UPDATE dispatch_form_templates
SET is_active = false
WHERE name = '김제 한우물 → 오산센터'
  AND client_name = '한우물';"
```

### 거래처 좌표 확인

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT name, client_type, address, latitude, longitude, geocoded
FROM clients
WHERE name IN ('한우물', '오산동원', '정읍 부엉이', '백암 웰빙')
ORDER BY name;"
```

## 🐛 트러블슈팅

### 문제: 템플릿이 로드되지 않음

```bash
# 1. 데이터베이스 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT name, client_name, is_active FROM dispatch_form_templates;"

# 2. 백엔드 로그 확인
docker compose logs backend --tail=50 | grep -E "template|템플릿"

# 3. 브라우저 DevTools Network 탭 확인
# GET /api/v1/dispatch-form/templates 응답 확인
```

### 문제: 파싱이 0건으로 나옴

```bash
# 1. 템플릿 데이터 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    name,
    template_data->'dispatches'->0->>'vehicle_type' AS vehicle_type
FROM dispatch_form_templates
WHERE client_name = '한우물';"

# 예상 결과: vehicle_type = "냉동16팔레트"

# 2. 파싱 API 직접 테스트
curl -X POST http://localhost/api/v1/orders/parse-batch-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "text":"**3/5(목)한우물 새벽배차**\n06:00 / 냉동16p",
    "pickup_address":"전북 김제시 용지면 부교리 87-10",
    "delivery_address":"경기도 화성시 정남면 가장로 285"
  }' | python3 -m json.tool
```

### 문제: AI 배차 시 좌표 없음 오류

```bash
# 1. 거래처 좌표 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT name, address, latitude, longitude, geocoded
FROM clients
WHERE name = '한우물' OR name = '오산동원';"

# 2. 주문 좌표 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    id,
    order_number,
    pickup_address,
    pickup_latitude,
    pickup_longitude,
    delivery_address,
    delivery_latitude,
    delivery_longitude
FROM orders
ORDER BY created_at DESC
LIMIT 5;"

# 3. NULL 좌표 업데이트
docker compose exec -T db psql -U uvis_user -d uvis_db <<EOF
UPDATE orders 
SET pickup_latitude = 35.803456, pickup_longitude = 126.878901
WHERE pickup_address LIKE '%부교리%' 
  AND (pickup_latitude IS NULL OR pickup_longitude IS NULL);

UPDATE orders 
SET delivery_latitude = 37.156789, delivery_longitude = 127.012345
WHERE delivery_address LIKE '%가장로 285%'
  AND (delivery_latitude IS NULL OR delivery_longitude IS NULL);
EOF
```

## 📞 지원

문제 발생 시 확인 사항:

1. **CSV 파일 인코딩**: UTF-8 확인
2. **좌표 형식**: 소수점 6자리 (예: 35.803456)
3. **데이터베이스 연결**: `docker compose ps | grep db`
4. **백엔드 상태**: `docker compose ps | grep backend`
5. **로그 확인**: 
   ```bash
   docker compose logs backend --tail=100 | grep -E "ERROR|파싱|template"
   ```

---

**작성일**: 2026-03-05  
**버전**: 1.0.0
