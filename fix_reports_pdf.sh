#!/bin/bash
set -e

cd /root/uvis

echo "=== Step 1: Add Dict import ==="
# Dict 추가
sed -i 's/from typing import Optional/from typing import Optional, Dict/' backend/app/api/v1/reports.py

echo "=== Step 2: Add transformation functions after imports ==="
# router 정의 바로 전에 변환 함수 추가
sed -i '/^router = APIRouter/i\
# Field transformation functions for PDF template compatibility\
def transform_summary_for_pdf(summary: Dict) -> Dict:\
    """Transform backend summary fields to PDF template fields"""\
    return {\
        "total_revenue": summary.get("total_revenue", 0),\
        "total_invoiced": summary.get("invoiced_amount", 0),\
        "total_paid": summary.get("collected_amount", 0),\
        "total_outstanding": summary.get("total_receivables", 0),\
        "payment_rate": summary.get("collection_rate", 0),\
        "overdue_count": summary.get("overdue_count", 0),\
        "overdue_amount": summary.get("overdue_receivables", 0),\
        "pending_settlement_amount": summary.get("pending_settlements", 0),\
        "cash_in": summary.get("cash_in", 0),\
        "cash_out": summary.get("cash_out", 0),\
        "net_cash_flow": summary.get("net_cash_flow", 0),\
    }\
\
def transform_trends_for_pdf(trends: list) -> list:\
    """Transform backend trends to PDF template format"""\
    return [\
        {\
            "month": t.get("month", ""),\
            "revenue": t.get("revenue", 0),\
            "invoiced": t.get("invoiced", 0),\
            "paid": t.get("paid", 0),\
            "outstanding": t.get("outstanding", 0),\
            "payment_rate": t.get("payment_rate", 0),\
        }\
        for t in trends\
    ]\
\
def transform_clients_for_pdf(clients: list) -> list:\
    """Transform backend top clients to PDF template format"""\
    return [\
        {\
            "client_name": c.get("client_name", ""),\
            "total_revenue": c.get("total_amount", 0),\
            "invoiced": c.get("total_amount", 0),\
            "paid": c.get("paid_amount", 0),\
            "outstanding": c.get("outstanding_amount", 0),\
        }\
        for c in clients\
    ]\
\
' backend/app/api/v1/reports.py

echo "=== Step 3: Modify PDF generation to use transformations ==="
# PDF 생성 부분 수정
sed -i '/pdf_bytes = pdf_generator.generate_financial_dashboard_pdf(/,/)/c\
        # Transform data for PDF template\
        transformed_summary = transform_summary_for_pdf(summary)\
        transformed_trends = transform_trends_for_pdf(monthly_trends)\
        transformed_clients = transform_clients_for_pdf(top_clients)\
        \
        # Generate PDF\
        pdf_bytes = pdf_generator.generate_financial_dashboard_pdf(\
            summary=transformed_summary,\
            monthly_trends=transformed_trends,\
            top_clients=transformed_clients,\
            start_date=start_date,\
            end_date=end_date\
        )' backend/app/api/v1/reports.py

echo "=== Step 4: Verify changes ==="
echo ""
echo "--- Dict import:"
grep "from typing import" backend/app/api/v1/reports.py

echo ""
echo "--- Transformation functions added:"
grep -c "def transform_" backend/app/api/v1/reports.py

echo ""
echo "--- PDF generation uses transformations:"
grep -A 5 "Transform data for PDF" backend/app/api/v1/reports.py

echo ""
echo "✅ Modifications complete!"
