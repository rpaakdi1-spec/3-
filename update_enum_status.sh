#!/bin/bash

echo "=============================================="
echo "상태 용어 통일 - ENUM 업데이트"
echo "=============================================="

# 1. OrderStatus ENUM에 '배송중' 추가
echo ""
echo "1. OrderStatus ENUM에 '배송중' 추가..."
docker exec uvis-db psql -U uvis_user -d uvis_db -c "ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS '배송중';"
echo "✅ 완료"

# 2. DispatchStatus ENUM에 '배차완료' 추가
echo ""
echo "2. DispatchStatus ENUM에 '배차완료' 추가..."
docker exec uvis-db psql -U uvis_user -d uvis_db -c "ALTER TYPE dispatchstatus ADD VALUE IF NOT EXISTS '배차완료';"
echo "✅ 완료"

# 3. 현재 ENUM 값 확인
echo ""
echo "3. 업데이트된 ENUM 확인"
echo "------------------------------"
echo "OrderStatus:"
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT unnest(enum_range(NULL::orderstatus));"

echo ""
echo "DispatchStatus:"
docker exec uvis-db psql -U uvis_user -d uvis_db -c "SELECT unnest(enum_range(NULL::dispatchstatus));"

echo ""
echo "=============================================="
echo "ENUM 업데이트 완료!"
echo "=============================================="
