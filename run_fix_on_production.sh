#!/bin/bash
# 프로덕션 서버에서 실행할 전체 스크립트

cd /root/uvis

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Phase 9 - PDF Field Mapping Fix                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Add Dict import
echo "=== Step 1: Add Dict import ==="
sed -i 's/from typing import Optional$/from typing import Optional, Dict/' backend/app/api/v1/reports.py

# Step 2: Add transformation functions
echo "=== Step 2: Add transformation functions ==="
# router 정의 바로 전에 변환 함수 추가
cat > /tmp/transform_functions.py << 'EOF'

# Field transformation functions for PDF template compatibility
def transform_summary_for_pdf(summary: Dict) -> Dict:
    """Transform backend summary fields to PDF template fields"""
    return {
        "total_revenue": summary.get("total_revenue", 0),
        "total_invoiced": summary.get("invoiced_amount", 0),
        "total_paid": summary.get("collected_amount", 0),
        "total_outstanding": summary.get("total_receivables", 0),
        "payment_rate": summary.get("collection_rate", 0),
        "overdue_count": summary.get("overdue_count", 0),
        "overdue_amount": summary.get("overdue_receivables", 0),
        "pending_settlement_amount": summary.get("pending_settlements", 0),
        "cash_in": summary.get("cash_in", 0),
        "cash_out": summary.get("cash_out", 0),
        "net_cash_flow": summary.get("net_cash_flow", 0),
    }

def transform_trends_for_pdf(trends: list) -> list:
    """Transform backend trends to PDF template format"""
    return [
        {
            "month": t.get("month", ""),
            "revenue": t.get("revenue", 0),
            "invoiced": t.get("invoiced", 0),
            "paid": t.get("paid", 0),
            "outstanding": t.get("outstanding", 0),
            "payment_rate": t.get("payment_rate", 0),
        }
        for t in trends
    ]

def transform_clients_for_pdf(clients: list) -> list:
    """Transform backend top clients to PDF template format"""
    return [
        {
            "client_name": c.get("client_name", ""),
            "total_revenue": c.get("total_amount", 0),
            "invoiced": c.get("total_amount", 0),
            "paid": c.get("paid_amount", 0),
            "outstanding": c.get("outstanding_amount", 0),
        }
        for c in clients
    ]

EOF

# router 정의 찾아서 그 전에 삽입
line_num=$(grep -n "^router = APIRouter" backend/app/api/v1/reports.py | cut -d: -f1)
if [ -n "$line_num" ]; then
    # 해당 라인 전에 삽입
    head -n $((line_num - 1)) backend/app/api/v1/reports.py > /tmp/reports_part1.py
    cat /tmp/transform_functions.py >> /tmp/reports_part1.py
    tail -n +${line_num} backend/app/api/v1/reports.py >> /tmp/reports_part1.py
    mv /tmp/reports_part1.py backend/app/api/v1/reports.py
    echo "✅ Transformation functions added before line $line_num"
else
    echo "❌ Could not find router definition"
    exit 1
fi

# Step 3: Modify PDF generation call
echo ""
echo "=== Step 3: Modify PDF generation to use transformations ==="

# PDF 엔드포인트에서 pdf_generator 호출 부분 찾기
python3 << 'PYSCRIPT'
import re

# Read the file
with open('backend/app/api/v1/reports.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the PDF generation call
pattern = r'([ \t]+)# Generate PDF\s*\n\s*pdf_bytes = pdf_generator\.generate_financial_dashboard_pdf\(\s*summary=summary,\s*monthly_trends=monthly_trends,\s*top_clients=top_clients,\s*start_date=start_date,\s*end_date=end_date\s*\)'

replacement = r'''\1# Transform data for PDF template
\1transformed_summary = transform_summary_for_pdf(summary)
\1transformed_trends = transform_trends_for_pdf(monthly_trends)
\1transformed_clients = transform_clients_for_pdf(top_clients)
\1
\1# Generate PDF
\1pdf_bytes = pdf_generator.generate_financial_dashboard_pdf(
\1    summary=transformed_summary,
\1    monthly_trends=transformed_trends,
\1    top_clients=transformed_clients,
\1    start_date=start_date,
\1    end_date=end_date
\1)'''

content_new = re.sub(pattern, replacement, content, flags=re.MULTILINE)

# Write back
with open('backend/app/api/v1/reports.py', 'w', encoding='utf-8') as f:
    f.write(content_new)

print("✅ PDF generation call updated")
PYSCRIPT

# Step 4: Verify
echo ""
echo "=== Step 4: Verify changes ==="
echo ""
echo "--- Dict import:"
grep "from typing import" backend/app/api/v1/reports.py | head -2

echo ""
echo "--- Transformation functions:"
grep "def transform_" backend/app/api/v1/reports.py

echo ""
echo "--- PDF uses transformations:"
grep -A 3 "transformed_summary = transform_summary_for_pdf" backend/app/api/v1/reports.py

echo ""
echo "✅ All modifications complete!"
echo ""

# Step 5: Rebuild and restart
echo "=== Step 5: Rebuild backend ==="
docker-compose build backend

echo ""
echo "=== Step 6: Restart backend ==="
docker-compose up -d backend --force-recreate

echo ""
echo "=== Step 7: Wait for backend to start ==="
sleep 30

echo ""
echo "=== Step 8: Test Phase 9 ==="
./test_phase9_reports.sh

