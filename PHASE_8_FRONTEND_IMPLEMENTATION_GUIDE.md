# Phase 8 프론트엔드 구현 가이드

## ✅ 완료된 작업

### 1. API 클라이언트 (`frontend/src/api/billing-enhanced.ts`)
- ✅ 모든 Phase 8 API 엔드포인트 함수
- ✅ TypeScript 타입 정의
- ✅ 유틸리티 함수 (포맷팅, 날짜 계산)

## 📋 구현 우선순위 가이드

### 최우선 (Week 1)

#### 1. 재무 대시보드 (`frontend/src/pages/billing/Dashboard.tsx`)

**필요한 컴포넌트**:
```typescript
// 1) 재무 요약 카드 컴포넌트
// frontend/src/components/billing/FinancialSummaryCard.tsx

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency, formatPercent } from '@/api/billing-enhanced';

interface Props {
  title: string;
  value: number;
  subtitle?: string;
  trend?: number; // 전월 대비 증감률
  format: 'currency' | 'percent';
  icon?: React.ReactNode;
}

export function FinancialSummaryCard({ title, value, subtitle, trend, format, icon }: Props) {
  const formattedValue = format === 'currency' 
    ? formatCurrency(value) 
    : formatPercent(value);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{title}</span>
          {icon}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold">{formattedValue}</div>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        {trend && (
          <p className={`text-sm mt-2 ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% from last month
          </p>
        )}
      </CardContent>
    </Card>
  );
}
```

```typescript
// 2) 매출 추이 차트
// frontend/src/components/billing/RevenueTrendChart.tsx

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { MonthlyTrend } from '@/api/billing-enhanced';

interface Props {
  data: MonthlyTrend[];
}

export function RevenueTrendChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="month" />
        <YAxis />
        <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
        <Legend />
        <Line type="monotone" dataKey="revenue" stroke="#10b981" name="매출" />
        <Line type="monotone" dataKey="collected" stroke="#3b82f6" name="수금" />
        <Line type="monotone" dataKey="settlements" stroke="#ef4444" name="정산" />
        <Line type="monotone" dataKey="net_profit" stroke="#8b5cf6" name="순이익" />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

```typescript
// 3) 주요 고객 차트
// frontend/src/components/billing/TopClientsChart.tsx

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { TopClient } from '@/api/billing-enhanced';

interface Props {
  data: TopClient[];
}

export function TopClientsChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical">
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis type="number" />
        <YAxis dataKey="client_name" type="category" width={100} />
        <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
        <Bar dataKey="total_revenue" fill="#10b981" name="매출" />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

```typescript
// 4) 메인 대시보드 페이지
// frontend/src/pages/billing/Dashboard.tsx

import { useQuery } from '@tanstack/react-query';
import { getFinancialSummary, getMonthlyTrends, getTopClients, getCurrentMonthDates } from '@/api/billing-enhanced';
import { FinancialSummaryCard } from '@/components/billing/FinancialSummaryCard';
import { RevenueTrendChart } from '@/components/billing/RevenueTrendChart';
import { TopClientsChart } from '@/components/billing/TopClientsChart';
import { DollarSign, TrendingUp, Clock, Activity } from 'lucide-react';

export function BillingDashboard() {
  const { startDate, endDate } = getCurrentMonthDates();

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['billing-summary', startDate, endDate],
    queryFn: () => getFinancialSummary(startDate, endDate),
  });

  const { data: trends, isLoading: trendsLoading } = useQuery({
    queryKey: ['billing-trends'],
    queryFn: () => getMonthlyTrends(undefined, undefined, 12),
  });

  const { data: topClients, isLoading: clientsLoading } = useQuery({
    queryKey: ['top-clients', startDate, endDate],
    queryFn: () => getTopClients(startDate, endDate, 10),
  });

  if (summaryLoading || trendsLoading || clientsLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">재무 대시보드</h1>

      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <FinancialSummaryCard
          title="총 매출"
          value={summary?.total_revenue || 0}
          subtitle={`수금률: ${summary?.collection_rate.toFixed(1)}%`}
          format="currency"
          icon={<DollarSign className="w-5 h-5" />}
        />
        <FinancialSummaryCard
          title="미수금"
          value={summary?.total_receivables || 0}
          subtitle={`연체: ${summary?.overdue_count}건`}
          format="currency"
          icon={<Clock className="w-5 h-5" />}
        />
        <FinancialSummaryCard
          title="정산 대기"
          value={summary?.pending_settlements || 0}
          subtitle="승인 대기 중"
          format="currency"
          icon={<Activity className="w-5 h-5" />}
        />
        <FinancialSummaryCard
          title="순 현금 흐름"
          value={summary?.net_cash_flow || 0}
          subtitle="이번 달"
          format="currency"
          icon={<TrendingUp className="w-5 h-5" />}
        />
      </div>

      {/* 차트 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>월별 매출 추이</CardTitle>
          </CardHeader>
          <CardContent>
            <RevenueTrendChart data={trends || []} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>주요 고객 매출</CardTitle>
          </CardHeader>
          <CardContent>
            <TopClientsChart data={topClients || []} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

**라우팅 추가** (`frontend/src/App.tsx`):
```typescript
<Route path="/billing/dashboard" element={<BillingDashboard />} />
```

---

#### 2. 요금 미리보기 컴포넌트

```typescript
// frontend/src/components/billing/ChargePreview.tsx

import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { previewCharge, formatCurrency, ChargePreviewRequest } from '@/api/billing-enhanced';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface Props {
  onChargeCalculated?: (totalAmount: number) => void;
}

export function ChargePreview({ onChargeCalculated }: Props) {
  const [request, setRequest] = useState<ChargePreviewRequest>({
    client_id: 0,
    dispatch_date: new Date().toISOString().split('T')[0],
    total_distance_km: 0,
    pallets: 0,
    weight_kg: 0,
    vehicle_type: '일반',
    is_urgent: false,
  });

  const [shouldPreview, setShouldPreview] = useState(false);

  // 자동 계산 (디바운스 적용 권장)
  useEffect(() => {
    if (request.client_id > 0 && request.total_distance_km > 0) {
      setShouldPreview(true);
    }
  }, [request]);

  const { data: preview, isLoading } = useQuery({
    queryKey: ['charge-preview', request],
    queryFn: () => previewCharge(request),
    enabled: shouldPreview && request.client_id > 0,
  });

  useEffect(() => {
    if (preview && onChargeCalculated) {
      onChargeCalculated(preview.breakdown.total_amount);
    }
  }, [preview, onChargeCalculated]);

  return (
    <Card>
      <CardHeader>
        <CardTitle>요금 미리보기</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* 입력 폼 */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label>배차 날짜</Label>
            <Input
              type="date"
              value={request.dispatch_date}
              onChange={(e) => setRequest({ ...request, dispatch_date: e.target.value })}
            />
          </div>
          <div>
            <Label>거리 (km)</Label>
            <Input
              type="number"
              value={request.total_distance_km}
              onChange={(e) => setRequest({ ...request, total_distance_km: Number(e.target.value) })}
            />
          </div>
          <div>
            <Label>팔레트 수</Label>
            <Input
              type="number"
              value={request.pallets}
              onChange={(e) => setRequest({ ...request, pallets: Number(e.target.value) })}
            />
          </div>
          <div>
            <Label>무게 (kg) - 선택사항</Label>
            <Input
              type="number"
              value={request.weight_kg || ''}
              onChange={(e) => setRequest({ ...request, weight_kg: Number(e.target.value) || undefined })}
            />
          </div>
          <div>
            <Label>차량 타입</Label>
            <Select
              value={request.vehicle_type}
              onValueChange={(value) => setRequest({ ...request, vehicle_type: value })}
            >
              <option value="일반">일반</option>
              <option value="냉장">냉장</option>
              <option value="냉동">냉동</option>
            </Select>
          </div>
          <div className="flex items-center space-x-2 pt-6">
            <Checkbox
              checked={request.is_urgent}
              onCheckedChange={(checked) => setRequest({ ...request, is_urgent: !!checked })}
            />
            <Label>긴급 배차</Label>
          </div>
        </div>

        {/* 계산 결과 */}
        {isLoading && <div>계산 중...</div>}
        
        {preview && (
          <div className="space-y-3 pt-4 border-t">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">기본 요금 (거리)</span>
              <span>{formatCurrency(preview.breakdown.base_distance_charge)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">기본 요금 (팔레트)</span>
              <span>{formatCurrency(preview.breakdown.base_pallet_charge)}</span>
            </div>
            {preview.breakdown.base_weight_charge > 0 && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">기본 요금 (무게)</span>
                <span>{formatCurrency(preview.breakdown.base_weight_charge)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm font-medium">
              <span>소계</span>
              <span>{formatCurrency(preview.breakdown.subtotal)}</span>
            </div>

            {preview.breakdown.total_surcharge > 0 && (
              <>
                <div className="border-t pt-2" />
                <div className="flex justify-between text-sm text-amber-600">
                  <span>할증</span>
                  <span>+{formatCurrency(preview.breakdown.total_surcharge)}</span>
                </div>
              </>
            )}

            {preview.breakdown.total_discount > 0 && (
              <div className="flex justify-between text-sm text-green-600">
                <span>할인</span>
                <span>-{formatCurrency(preview.breakdown.total_discount)}</span>
              </div>
            )}

            <div className="border-t pt-2" />
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">부가세 (10%)</span>
              <span>{formatCurrency(preview.breakdown.tax_amount)}</span>
            </div>

            <div className="flex justify-between text-lg font-bold text-blue-600 border-t pt-2">
              <span>최종 금액</span>
              <span>{formatCurrency(preview.breakdown.total_amount)}</span>
            </div>

            {/* 안내 메시지 */}
            {preview.notes && preview.notes.length > 0 && (
              <Alert>
                <AlertDescription>
                  <ul className="list-disc list-inside space-y-1">
                    {preview.notes.map((note, index) => (
                      <li key={index}>{note}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

**배차 등록 화면에서 사용**:
```typescript
// frontend/src/pages/dispatches/CreateDispatch.tsx

import { ChargePreview } from '@/components/billing/ChargePreview';

export function CreateDispatch() {
  const [estimatedCost, setEstimatedCost] = useState(0);

  return (
    <div>
      {/* 기존 배차 등록 폼 */}
      
      {/* 요금 미리보기 추가 */}
      <ChargePreview onChargeCalculated={setEstimatedCost} />
      
      {/* 저장 버튼 등 */}
    </div>
  );
}
```

---

### 중요도: 중간 (Week 2)

#### 3. 청구서/정산서 목록 개선

기존 화면에 다음 기능 추가:
- Excel 내보내기 버튼
- 상세 필터링
- 요약 통계 카드

```typescript
// 내보내기 기능 추가
import { createExportTask } from '@/api/billing-enhanced';

const handleExport = async () => {
  const task = await createExportTask({
    start_date: startDate,
    end_date: endDate,
    format: 'excel',
    include_details: true,
  });
  
  // 작업 완료 대기 (폴링 또는 알림)
  alert(`내보내기 작업이 시작되었습니다. 작업 ID: ${task.task_id}`);
};
```

#### 4. 정산 승인 화면

```typescript
// frontend/src/pages/billing/SettlementApproval.tsx

import { useQuery, useMutation } from '@tanstack/react-query';
import { processSettlementApproval, getSettlementApprovalHistory } from '@/api/billing-enhanced';

export function SettlementApproval({ settlementId }: { settlementId: number }) {
  const { data: history } = useQuery({
    queryKey: ['settlement-approval-history', settlementId],
    queryFn: () => getSettlementApprovalHistory(settlementId),
  });

  const approveMutation = useMutation({
    mutationFn: (notes?: string) => processSettlementApproval({
      settlement_id: settlementId,
      action: 'approve',
      notes,
    }),
    onSuccess: () => {
      alert('승인되었습니다!');
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (reason: string) => processSettlementApproval({
      settlement_id: settlementId,
      action: 'reject',
      notes: reason,
    }),
    onSuccess: () => {
      alert('반려되었습니다!');
    },
  });

  return (
    <div>
      {/* 정산서 정보 표시 */}
      
      {/* 승인/반려 버튼 */}
      <div className="flex gap-2">
        <Button onClick={() => approveMutation.mutate()}>승인</Button>
        <Button variant="destructive" onClick={() => {
          const reason = prompt('반려 사유를 입력하세요:');
          if (reason) rejectMutation.mutate(reason);
        }}>반려</Button>
      </div>

      {/* 승인 이력 */}
      <div className="mt-6">
        <h3>승인 이력</h3>
        {history?.map((item) => (
          <div key={item.id} className="border-b py-2">
            <div>{item.action} - {item.created_at}</div>
            {item.notes && <div className="text-sm text-gray-600">{item.notes}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### 선택 사항 (Week 3)

#### 5. 자동 청구 스케줄 설정

```typescript
// frontend/src/pages/billing/AutoSchedule.tsx

import { useQuery, useMutation } from '@tanstack/react-query';
import { getAutoInvoiceSchedules, createOrUpdateAutoInvoiceSchedule } from '@/api/billing-enhanced';

export function AutoSchedulePage() {
  const { data: schedules } = useQuery({
    queryKey: ['auto-schedules'],
    queryFn: () => getAutoInvoiceSchedules(),
  });

  const createMutation = useMutation({
    mutationFn: createOrUpdateAutoInvoiceSchedule,
    onSuccess: () => {
      alert('스케줄이 저장되었습니다!');
    },
  });

  return (
    <div>
      <h1>자동 청구 스케줄 관리</h1>
      
      {/* 스케줄 목록 테이블 */}
      {schedules?.map((schedule) => (
        <div key={schedule.id}>
          {/* 스케줄 정보 표시 */}
        </div>
      ))}

      {/* 스케줄 추가 버튼 + 모달 */}
    </div>
  );
}
```

#### 6. 통계 분석 화면

```typescript
// frontend/src/pages/billing/Analytics.tsx

import { useQuery } from '@tanstack/react-query';
import { getBillingStatistics, getSettlementStatistics } from '@/api/billing-enhanced';

export function AnalyticsPage() {
  const { data: billingStats } = useQuery({
    queryKey: ['billing-stats'],
    queryFn: () => getBillingStatistics(),
  });

  const { data: settlementStats } = useQuery({
    queryKey: ['settlement-stats'],
    queryFn: () => getSettlementStatistics(),
  });

  return (
    <div>
      {/* 통계 카드 및 차트 */}
    </div>
  );
}
```

---

## 📦 필요한 패키지 설치

```bash
cd frontend

# Recharts (차트 라이브러리)
npm install recharts

# React Hook Form + Zod (폼 관리)
npm install react-hook-form zod @hookform/resolvers

# shadcn/ui 컴포넌트 (선택사항, 이미 설치되어 있을 수 있음)
npx shadcn-ui@latest add card
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add select
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add alert
```

---

## 🎯 성공 기준

### ✅ 필수 (최우선)
1. 재무 대시보드가 로드되고 데이터가 정상 표시됨
2. 요금 미리보기가 실시간으로 계산됨
3. 차트가 정상 렌더링됨

### 📊 권장 (중간)
4. 청구서/정산서 목록에 내보내기 기능 추가
5. 정산 승인 화면 구현

### 🌟 선택 (추가)
6. 자동 청구 스케줄 설정 화면
7. 통계 분석 화면

---

## 🚀 다음 단계

1. API 클라이언트 완성 ✅
2. 재무 대시보드 구현 (최우선)
3. 요금 미리보기 구현 (최우선)
4. 나머지 화면 순차적 구현

---

## 📝 참고사항

- 모든 API 호출은 `@tanstack/react-query` 사용 권장
- 에러 처리는 `react-query`의 에러 바운더리 활용
- 로딩 상태는 스켈레톤 UI 사용 권장
- 차트는 `Recharts` 사용 (이미 설치되어 있을 수 있음)

