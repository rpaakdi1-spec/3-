#!/bin/bash
# ====================================================================
# UVIS 데이터베이스 전체 스키마 생성 스크립트 실행
# ====================================================================

echo "🔧 UVIS 데이터베이스 기본 테이블 생성 중..."
echo "==============================================="
echo ""

# 1. SQL 파일을 컨테이너로 복사
echo "=== 1. SQL 파일 복사 ==="
docker cp create_all_base_tables.sql uvis-db:/tmp/
if [ $? -eq 0 ]; then
    echo "✅ SQL 파일 복사 완료"
else
    echo "❌ SQL 파일 복사 실패"
    exit 1
fi
echo ""

# 2. SQL 스크립트 실행
echo "=== 2. 기본 테이블 생성 중 ==="
docker exec uvis-db psql -U uvis_user -d uvis -f /tmp/create_all_base_tables.sql
if [ $? -eq 0 ]; then
    echo "✅ 기본 테이블 생성 완료"
else
    echo "❌ 기본 테이블 생성 실패"
    exit 1
fi
echo ""

# 3. 생성된 테이블 확인
echo "=== 3. 생성된 테이블 목록 ==="
docker exec uvis-db psql -U uvis_user -d uvis -c "\dt" | grep -E "users|notifications|dispatches|vehicles|orders|drivers|clients"
echo ""

# 4. 핵심 테이블 존재 확인
echo "=== 4. 핵심 테이블 확인 ==="
for table in users notifications dispatches vehicles orders drivers clients; do
    result=$(docker exec uvis-db psql -U uvis_user -d uvis -t -c "SELECT to_regclass('public.$table');" | tr -d ' ')
    if [ "$result" = "$table" ]; then
        echo "✅ $table 테이블 존재"
    else
        echo "❌ $table 테이블 없음"
    fi
done
echo ""

# 5. 이제 dispatch_rules 마이그레이션 적용
echo "=== 5. dispatch_rules 마이그레이션 적용 ==="
docker exec uvis-backend alembic upgrade phase10_001
if [ $? -eq 0 ]; then
    echo "✅ dispatch_rules 마이그레이션 완료"
else
    echo "⚠️ dispatch_rules 마이그레이션 실패 (이미 존재할 수 있음)"
fi
echo ""

# 6. 시뮬레이션 마이그레이션 적용
echo "=== 6. 시뮬레이션 마이그레이션 적용 ==="
docker exec uvis-backend alembic upgrade phase11c_simulations
if [ $? -eq 0 ]; then
    echo "✅ 시뮬레이션 마이그레이션 완료"
else
    echo "⚠️ 시뮬레이션 마이그레이션 실패"
fi
echo ""

# 7. 템플릿 데이터 마이그레이션 적용
echo "=== 7. 템플릿 데이터 마이그레이션 적용 ==="
docker exec uvis-backend alembic upgrade phase11c_templates_data
if [ $? -eq 0 ]; then
    echo "✅ 템플릿 데이터 마이그레이션 완료"
else
    echo "⚠️ 템플릿 데이터 마이그레이션 실패"
fi
echo ""

# 8. 사용자 전화번호 마이그레이션 적용
echo "=== 8. 사용자 전화번호 마이그레이션 적용 ==="
docker exec uvis-backend alembic upgrade a6eb2e22dbd2
if [ $? -eq 0 ]; then
    echo "✅ 사용자 전화번호 마이그레이션 완료"
else
    echo "⚠️ 사용자 전화번호 마이그레이션 실패 (이미 phone 컬럼 존재)"
fi
echo ""

# 9. 최종 마이그레이션 상태 확인
echo "=== 9. 최종 마이그레이션 상태 ==="
docker exec uvis-backend alembic current
echo ""

# 10. 백엔드 재시작
echo "=== 10. 백엔드 재시작 ==="
docker-compose restart backend
echo "⏳ 백엔드 시작 대기 중 (10초)..."
sleep 10
echo ""

# 11. 헬스체크
echo "=== 11. 헬스체크 ==="
docker logs uvis-backend --tail 20 | grep -E "ERROR|WARNING|startup complete|ProgrammingError"
echo ""

# 12. 테스트 요청
echo "=== 12. API 테스트 ==="
echo "🔗 헬스체크: http://localhost:8000/api/v1/health"
curl -s http://localhost:8000/api/v1/health | jq . || echo "헬스체크 응답 없음"
echo ""

echo "🔗 배차 규칙 목록: http://localhost:8000/api/v1/dispatch-rules"
curl -s http://localhost:8000/api/v1/dispatch-rules | jq . || echo "배차 규칙 API 응답 없음"
echo ""

# 13. 최종 테이블 개수
echo "=== 13. 최종 데이터베이스 상태 ==="
table_count=$(docker exec uvis-db psql -U uvis_user -d uvis -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
echo "📊 총 테이블 개수: $table_count"
echo ""

echo "==============================================="
echo "✅ 데이터베이스 스키마 생성 완료!"
echo "==============================================="
echo ""
echo "🎯 다음 단계:"
echo "1. 브라우저에서 http://139.150.11.99/dispatch-rules 접속"
echo "2. 규칙 추가/수정/삭제 테스트"
echo "3. PUT 요청이 rule_update 래퍼를 사용하는지 확인"
echo ""
