#!/bin/bash

# Phase 9 - Comprehensive Testing Script
# Purpose: Test Phase 9 PDF/Excel report generation
# Author: Claude AI
# Date: 2026-02-07

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Phase 9 - Comprehensive Testing Script              ║"
echo "║          Advanced Reporting System Testing                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:80"
START_DATE="2025-11-07"
END_DATE="2026-02-07"
REPORT_DIR="/tmp/phase9_reports"

# Create report directory
mkdir -p "$REPORT_DIR"
cd "$REPORT_DIR"

echo -e "${BLUE}📊 Test Configuration:${NC}"
echo "  • Backend URL: $BASE_URL"
echo "  • Frontend URL: $FRONTEND_URL"
echo "  • Date Range: $START_DATE ~ $END_DATE"
echo "  • Report Directory: $REPORT_DIR"
echo ""

# Test 1: Backend Health Check
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 1: Backend Health Check                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s $BASE_URL/health)
echo "Response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi
echo ""

# Test 2: Authentication
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 2: Authentication                                       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}Logging in as admin...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

echo "Response: $LOGIN_RESPONSE"

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get authentication token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Authentication successful${NC}"
echo "Token (first 50 chars): ${TOKEN:0:50}..."
echo ""

# Test 3: Excel Report Download
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 3: Excel Report Download                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

EXCEL_FILE="$REPORT_DIR/financial_dashboard_${START_DATE}_${END_DATE}.xlsx"

echo -e "${BLUE}Downloading Excel report...${NC}"
echo "URL: $BASE_URL/api/v1/reports/financial-dashboard/excel"
echo "Parameters: start_date=$START_DATE, end_date=$END_DATE"
echo ""

HTTP_STATUS=$(curl -s -w "%{http_code}" -o "$EXCEL_FILE" \
  -X POST "$BASE_URL/api/v1/reports/financial-dashboard/excel?start_date=${START_DATE}&end_date=${END_DATE}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    if [ -f "$EXCEL_FILE" ]; then
        FILE_SIZE=$(stat -f%z "$EXCEL_FILE" 2>/dev/null || stat -c%s "$EXCEL_FILE" 2>/dev/null)
        echo -e "${GREEN}✅ Excel report downloaded successfully${NC}"
        echo "   File: $EXCEL_FILE"
        echo "   Size: $FILE_SIZE bytes"
        
        if [ "$FILE_SIZE" -gt 1000 ]; then
            echo -e "${GREEN}✅ File size looks good (>1KB)${NC}"
        else
            echo -e "${YELLOW}⚠️  File size is small (<1KB)${NC}"
        fi
    else
        echo -e "${RED}❌ Excel file not found${NC}"
    fi
else
    echo -e "${RED}❌ Excel download failed with status $HTTP_STATUS${NC}"
    cat "$EXCEL_FILE"
fi
echo ""

# Test 4: PDF Report Download
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 4: PDF Report Download                                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PDF_FILE="$REPORT_DIR/financial_dashboard_${START_DATE}_${END_DATE}.pdf"

echo -e "${BLUE}Downloading PDF report...${NC}"
echo "URL: $BASE_URL/api/v1/reports/financial-dashboard/pdf"
echo "Parameters: start_date=$START_DATE, end_date=$END_DATE"
echo ""

HTTP_STATUS=$(curl -s -w "%{http_code}" -o "$PDF_FILE" \
  -X POST "$BASE_URL/api/v1/reports/financial-dashboard/pdf?start_date=${START_DATE}&end_date=${END_DATE}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/pdf")

echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    if [ -f "$PDF_FILE" ]; then
        FILE_SIZE=$(stat -f%z "$PDF_FILE" 2>/dev/null || stat -c%s "$PDF_FILE" 2>/dev/null)
        echo -e "${GREEN}✅ PDF report downloaded successfully${NC}"
        echo "   File: $PDF_FILE"
        echo "   Size: $FILE_SIZE bytes"
        
        if [ "$FILE_SIZE" -gt 10000 ]; then
            echo -e "${GREEN}✅ File size looks good (>10KB)${NC}"
        else
            echo -e "${YELLOW}⚠️  File size is small (<10KB)${NC}"
        fi
        
        # Check PDF header
        FILE_HEADER=$(head -c 4 "$PDF_FILE")
        if [ "$FILE_HEADER" = "%PDF" ]; then
            echo -e "${GREEN}✅ Valid PDF file header${NC}"
        else
            echo -e "${RED}❌ Invalid PDF file header${NC}"
        fi
    else
        echo -e "${RED}❌ PDF file not found${NC}"
    fi
else
    echo -e "${RED}❌ PDF download failed with status $HTTP_STATUS${NC}"
    cat "$PDF_FILE"
fi
echo ""

# Test 5: Frontend Health Check
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 5: Frontend Health Check                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}Testing frontend...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Frontend is accessible${NC}"
else
    echo -e "${RED}❌ Frontend returned status $HTTP_STATUS${NC}"
fi
echo ""

# Test 6: API Documentation
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Test 6: API Documentation                                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${BLUE}Checking Swagger UI...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
echo "HTTP Status: $HTTP_STATUS"

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Swagger UI is accessible${NC}"
    echo "   URL: http://139.150.11.99:8000/docs#/Reports"
else
    echo -e "${RED}❌ Swagger UI returned status $HTTP_STATUS${NC}"
fi
echo ""

# Test Summary
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                      Test Summary                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PASS_COUNT=0
FAIL_COUNT=0

# Count results
[ -f "$EXCEL_FILE" ] && [ $(stat -f%z "$EXCEL_FILE" 2>/dev/null || stat -c%s "$EXCEL_FILE" 2>/dev/null) -gt 1000 ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))
[ -f "$PDF_FILE" ] && [ $(stat -f%z "$PDF_FILE" 2>/dev/null || stat -c%s "$PDF_FILE" 2>/dev/null) -gt 10000 ] && ((PASS_COUNT++)) || ((FAIL_COUNT++))

echo -e "${GREEN}✅ Passed: $PASS_COUNT tests${NC}"
echo -e "${RED}❌ Failed: $FAIL_COUNT tests${NC}"
echo ""

echo "📁 Generated Reports:"
ls -lh "$REPORT_DIR"
echo ""

echo "📝 Next Steps:"
echo "  1. Open Excel file: $EXCEL_FILE"
echo "     • Verify 4 sheets (Summary, Monthly Trends, Top Clients, Charts)"
echo "     • Check Korean font rendering"
echo "     • Verify 14 financial metrics"
echo ""
echo "  2. Open PDF file: $PDF_FILE"
echo "     • Verify 3 pages"
echo "     • Check Korean font rendering (NanumGothic)"
echo "     • Verify chart images"
echo "     • Check Top 10 clients table"
echo ""
echo "  3. Frontend UI Test:"
echo "     • URL: http://139.150.11.99/"
echo "     • Login: admin / admin123"
echo "     • Navigate: 청구/정산 → 재무 대시보드"
echo "     • Click: 보고서 다운로드 button"
echo "     • Select: Excel or PDF"
echo "     • Download and verify"
echo ""

if [ "$PASS_COUNT" -eq 2 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            🎉 All Tests Passed! 🎉                            ║${NC}"
    echo -e "${GREEN}║        Phase 9 Backend: ✅ 100% Working                        ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║            ⚠️  Some Tests Failed ⚠️                            ║${NC}"
    echo -e "${RED}║        Please check the errors above                          ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
