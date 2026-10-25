# 배차 템플릿 CSV 관리 가이드

CSV 파일로 배차 템플릿을 손쉽게 관리하는 시스템입니다.

## 📁 파일 구성

```
/home/user/webapp/  (또는 서버의 /root/uvis/)
├── templates.csv           # 템플릿 데이터 (엑셀/구글시트로 편집 가능)
├── csv_to_sql.py          # CSV → SQL 변환 스크립트
├── apply_templates.sh     # 템플릿 적용 스크립트
└── TEMPLATES_README.md    # 이 문서
```

## 🚀 빠른 시작

### 1️⃣ CSV 파일 편집

`templates.csv` 파일을 엑셀이나 구글 시트로 열어서 편집하세요.

**CSV 형식:**
```csv
템플릿명,상차거래처,하차거래처,카테고리,상차시간,팔레트,온도,상차주소,상차위도,상차경도,하차주소,하차위도,하차경도,하차완료시간,비고
김제 한우물 → 오산센터,한우물,오산동원,새벽배차,06:00,16,냉동,전북 김제시 용지면 부교리 87-10,35.803456,126.878901,경기도 화성시 정남면 가장로 285,37.156789,127.012345,10:00,1공장
```

### 2️⃣ 템플릿 적용

```bash
bash apply_templates.sh
```

또는 다른 CSV 파일 사용:
```bash
bash apply_templates.sh my_routes.csv
```

### 3️⃣ 브라우저에서 확인

http://139.150.11.99/orders → **일괄 등록** → **템플릿 불러오기**

## 📝 CSV 필드 설명

| 필드명 | 필수 | 설명 | 예시 |
|--------|------|------|------|
| 템플릿명 | ✅ | 템플릿 이름 | `김제 한우물 → 오산센터` |
| 상차거래처 | ✅ | 상차지 거래처명 | `한우물` |
| 하차거래처 | ✅ | 하차지 거래처명 | `오산동원` |
| 카테고리 | ✅ | 배차 카테고리 | `새벽배차` / `아침배차` / `오후배차` |
| 상차시간 | ✅ | 상차 시작 시간 | `06:00` |
| 팔레트 | ✅ | 팔레트 수 | `16` |
| 온도 | ✅ | 온도 구분 | `냉동` / `냉장` |
| 상차주소 | ✅ | 상차지 전체 주소 | `전북 김제시 용지면 부교리 87-10` |
| 상차위도 | ✅ | 상차지 위도 | `35.803456` |
| 상차경도 | ✅ | 상차지 경도 | `126.878901` |
| 하차주소 | ✅ | 하차지 전체 주소 | `경기도 화성시 정남면 가장로 285` |
| 하차위도 | ✅ | 하차지 위도 | `37.156789` |
| 하차경도 | ✅ | 하차지 경도 | `127.012345` |
| 하차완료시간 | ✅ | 하차 완료 목표 시간 | `10:00` |
| 비고 | ⬜ | 추가 메모 (선택) | `1공장` / `2공장` |

## 🗺️ 좌표 찾는 방법

### 네이버 지도
1. https://map.naver.com 접속
2. 주소 검색
3. 위치 클릭 → **좌표** 복사
4. 형식: `위도, 경도` (예: `35.803456, 126.878901`)

### 카카오맵
1. https://map.kakao.com 접속
2. 주소 검색
3. **공유** → **위치/좌표** 복사
4. 형식: `위도, 경도`

### Google 지도
1. https://maps.google.com 접속
2. 위치 오른쪽 클릭 → 좌표 클릭
3. 클립보드로 복사

## 💡 자동 계산 항목

다음 항목은 자동으로 계산됩니다:

- **톤수**: 팔레트 수 → 톤수 자동 변환
  - 18팔레트 이상 → 15톤
  - 16팔레트 이상 → 11톤
  - 14팔레트 이상 → 10톤
  - 12팔레트 이상 → 8톤
  - 10팔레트 이상 → 5톤
  - 그 외 → 3톤

- **차량 타입**: `냉동16팔레트`, `냉장18팔레트` 등

- **제품명**: `냉동식품 11톤`, `냉장식품 15톤` 등

- **거래처 코드**: 거래처명 → 영문 대문자 코드
  - `한우물` → `HANWOOMUL`
  - `오산동원` → `OSAN_DONGWON`

## 📊 예시 CSV 데이터

```csv
템플릿명,상차거래처,하차거래처,카테고리,상차시간,팔레트,온도,상차주소,상차위도,상차경도,하차주소,하차위도,하차경도,하차완료시간,비고
김제 한우물 → 오산센터,한우물,오산동원,새벽배차,06:00,16,냉동,전북 김제시 용지면 부교리 87-10,35.803456,126.878901,경기도 화성시 정남면 가장로 285,37.156789,127.012345,10:00,1공장
김제 한우물 → 부산센터,한우물,부산 냉장,아침배차,08:00,18,냉장,전북 김제시 용지면 부교리 87-10,35.803456,126.878901,부산광역시 강서구 명지동 123,35.123456,129.012345,13:00,2공장
정읍 부엉이 → 백암 웰빙,정읍 부엉이,백암 웰빙,아침배차,08:30,16,냉동,전북 정읍시 망제동 503-1,35.577812,126.856789,용인시 처인구 백암면 가창리 435-12,37.223456,127.345678,13:30,
목우촌 오후배차 1,목우촌,목우촌 안성센터,오후배차,13:00,18,냉동,전북 김제시 금산면 용산리 9-13,35.812345,126.923456,경기도 안성시 양성면 양성로 376-106,37.056789,127.234567,17:00,식육18톤
```

## 🔧 고급 사용법

### 직접 SQL 생성 (미리보기)

```bash
python3 csv_to_sql.py templates.csv > /tmp/preview.sql
cat /tmp/preview.sql
```

### 데이터베이스에 직접 적용

```bash
python3 csv_to_sql.py templates.csv | docker compose exec -T db psql -U uvis_user -d uvis_db
```

### 특정 템플릿만 추가

새 CSV 파일 생성 후:
```bash
bash apply_templates.sh new_template.csv
```

## 🗄️ 데이터베이스 관리

### 전체 템플릿 목록 조회

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT 
    id,
    client_name AS 거래처,
    name AS 템플릿명,
    category AS 카테고리,
    template_data->'dispatches'->0->>'time' AS 시간,
    template_data->'dispatches'->0->>'pallet_count' AS 팔레트
FROM dispatch_form_templates
ORDER BY client_name, name;"
```

### 특정 거래처 템플릿 조회

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT * FROM dispatch_form_templates
WHERE client_name = '한우물';"
```

### 템플릿 삭제

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
DELETE FROM dispatch_form_templates
WHERE name = '김제 한우물 → 오산센터'
  AND client_name = '한우물';"
```

### 템플릿 비활성화 (삭제하지 않고 숨기기)

```bash
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
UPDATE dispatch_form_templates
SET is_active = false
WHERE name = '김제 한우물 → 오산센터';"
```

## 🔄 워크플로우 권장사항

### Google Sheets 사용 시

1. **Google Sheets에서 템플릿 관리**
   - 여러 사람이 동시 편집 가능
   - 변경 이력 자동 추적
   - 주석/메모 추가 가능

2. **CSV 다운로드**
   - 파일 → 다운로드 → CSV (.csv)

3. **서버에 업로드**
   ```bash
   scp templates.csv root@139.150.11.99:/root/uvis/
   ```

4. **적용**
   ```bash
   ssh root@139.150.11.99
   cd /root/uvis
   bash apply_templates.sh
   ```

### 로컬 Excel 사용 시

1. **Excel에서 `templates.csv` 편집**
   - UTF-8 인코딩 유지 필수!
   - 다른 이름으로 저장 → CSV UTF-8

2. **서버에 복사 후 적용**
   ```bash
   scp templates.csv root@139.150.11.99:/root/uvis/
   ssh root@139.150.11.99 'cd /root/uvis && bash apply_templates.sh'
   ```

## 🐛 트러블슈팅

### 문제: "파일을 찾을 수 없습니다"

```bash
# 현재 디렉토리 확인
pwd
# 파일 목록 확인
ls -la templates.csv
# 절대 경로로 실행
bash apply_templates.sh /root/uvis/templates.csv
```

### 문제: "인코딩 오류"

CSV 파일을 **UTF-8 인코딩**으로 저장했는지 확인하세요.

**Excel:**
- 다른 이름으로 저장 → **CSV UTF-8 (쉼표로 분리)**

**구글 시트:**
- 파일 → 다운로드 → **CSV (.csv)** (자동으로 UTF-8)

### 문제: "좌표가 정확하지 않음"

AI 배차 시 거리 계산이 이상하다면:
1. 네이버/카카오맵에서 정확한 좌표 재확인
2. 위도/경도 순서 확인 (위도가 먼저!)
3. 소수점 6자리까지 입력

### 문제: "템플릿이 UI에 표시되지 않음"

```bash
# 데이터베이스 확인
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
SELECT name, client_name, is_active
FROM dispatch_form_templates
WHERE client_name = '한우물';"

# is_active가 false면 활성화
docker compose exec -T db psql -U uvis_user -d uvis_db -c "
UPDATE dispatch_form_templates
SET is_active = true
WHERE client_name = '한우물';"
```

## 📞 지원

문제 발생 시:
1. CSV 파일 확인: `cat templates.csv`
2. 생성된 SQL 확인: `cat /tmp/generated_templates.sql`
3. 데이터베이스 로그: `docker compose logs db --tail=50`
4. 백엔드 로그: `docker compose logs backend --tail=50`

---

**작성일**: 2026-03-05
**버전**: 1.0.0
