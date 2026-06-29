#!/bin/bash
# CSV 템플릿을 데이터베이스에 적용하는 스크립트

set -e

CSV_FILE="${1:-templates.csv}"
SQL_FILE="/tmp/generated_templates.sql"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ CSV 파일을 찾을 수 없습니다: $CSV_FILE"
    echo "사용법: bash apply_templates.sh [CSV파일경로]"
    exit 1
fi

echo "📋 CSV 파일 읽는 중: $CSV_FILE"
echo ""

# CSV -> SQL 변환
python3 csv_to_sql.py "$CSV_FILE" > "$SQL_FILE"

echo "✅ SQL 파일 생성 완료: $SQL_FILE"
echo ""

# 미리보기
echo "📄 생성된 SQL 미리보기 (처음 50줄):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
head -n 50 "$SQL_FILE"
echo "..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 확인
echo "🚀 데이터베이스에 적용하시겠습니까?"
echo "   명령어: docker compose exec -T db psql -U uvis_user -d uvis_db < $SQL_FILE"
echo ""
read -p "계속하시겠습니까? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 데이터베이스에 적용 중..."
    docker compose exec -T db psql -U uvis_user -d uvis_db < "$SQL_FILE"
    echo ""
    echo "✅ 템플릿 적용 완료!"
    echo ""
    echo "🌐 브라우저에서 확인: http://139.150.11.99/orders"
    echo "   - 일괄 등록 버튼 클릭"
    echo "   - 템플릿 불러오기 선택"
    echo "   - 거래처 및 템플릿 선택"
else
    echo "❌ 취소되었습니다."
    echo "   SQL 파일 확인: cat $SQL_FILE"
fi
