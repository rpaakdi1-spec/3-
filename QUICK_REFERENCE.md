# 배차 최적화 수정 - 빠른 참조 카드

## 🔴 문제
```
POST /api/v1/dispatches/optimize → 500 Internal Server Error
TypeError: DispatchOptimizationService.optimize_dispatch() got an unexpected keyword argument 'vehicle_ids'
```

## ✅ 해결 (3단계)

### 1단계: 스크립트 복사
```bash
cd /home/user/webapp
scp server_fix_optimization.sh root@139.150.11.99:/root/
```

### 2단계: 서버에서 실행
```bash
ssh root@139.150.11.99
bash /root/server_fix_optimization.sh
```

### 3단계: 테스트
```bash
# 서버에서
curl -X POST "http://localhost:8000/api/v1/dispatches/optimize" \
  -H "Content-Type: application/json" \
  -d '{ "order_ids": [1, 2], "vehicle_ids": [], "dispatch_date": "2026-02-19" }' | jq .

# 로컬에서
python3 test_dispatch_flow.py
```

## 📋 예상 결과

**성공 응답:**
```json
{
  "success": true,
  "message": "배차 최적화 완료",
  "total_orders": 2,
  "assigned_orders": 2,
  "execution_time": 2.3
}
```

**통합 테스트:**
```
총 테스트: 6
성공: 6 (100%)
실패: 0
```

## 🚨 문제 발생 시

### 진단 도구
```bash
ssh root@139.150.11.99 "bash /root/quick_diagnosis.sh"
```

### 로그 확인
```bash
ssh root@139.150.11.99 "docker logs uvis-backend --tail 50"
```

### 파일 확인
```bash
ssh root@139.150.11.99 "head -60 /root/uvis/backend/app/api/dispatches.py"
```

## 📚 상세 문서

| 문서 | 용도 |
|------|------|
| `DEPLOYMENT_PLAN.md` | 전체 배포 계획 |
| `DEPLOY_OPTIMIZATION_FIX.md` | 상세 수정 가이드 |
| `TROUBLESHOOTING.md` | 문제 해결 |

## 💾 커밋 정보

```
221089c - Add deployment scripts and documentation
e1108c1 - Fix dispatch optimization endpoint and add integration tests
```

## ⚡ 원라이너 (한 줄로 배포)

```bash
scp server_fix_optimization.sh root@139.150.11.99:/root/ && \
ssh root@139.150.11.99 "bash /root/server_fix_optimization.sh"
```

---

**작성:** 2026-02-19  
**상태:** ✅ 배포 준비 완료
