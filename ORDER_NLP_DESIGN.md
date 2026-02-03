# 🤖 거래처 자연어 주문 자동화 시스템 설계

## 📋 문제 정의

### 입력 (거래처 요청)
```
[02/03] 추가 배차요청
백암 _ 저온 → 경산 16판 1대

동이천센터 → 양산 16판 1대

**2/3(화)목우촌 오후배차**
15:30 / 육가공5톤
16:30 / 육가공11톤
```

### 출력 (구조화된 주문)
```json
{
  "order_date": "2026-02-03",
  "pickup_client": "백암",
  "delivery_client": "경산",
  "temperature_zone": "REFRIGERATED",
  "pallet_count": 16,
  "vehicle_count": 1
}
```

---

## 🎯 해결 방안

### 방안 1: 규칙 기반 + LLM (GPT-4) - **권장**

**장점**: 
- 빠른 구현 (1-2주)
- 높은 정확도 (95%+)
- 실시간 처리 가능
- 새로운 패턴 즉시 대응

**구조**:
```
자연어 입력 
  → 전처리 (날짜, 숫자 추출)
  → LLM (GPT-4) 호출
  → 후처리 (검증, 매칭)
  → 구조화된 주문 생성
```

**예시 LLM Prompt**:
```
당신은 물류 주문 처리 전문가입니다. 다음 거래처 요청을 JSON으로 변환하세요.

거래처 데이터베이스:
- 백암: {id: 1, address: "경기도 용인시 처인구 백암면", type: "PICKUP"}
- 경산: {id: 5, address: "경상북도 경산시 압량읍", type: "DELIVERY"}
- 동이천센터: {id: 3, address: "경기도 이천시 부발읍 동이천로", type: "PICKUP"}
- 양산: {id: 7, address: "경상남도 양산시 물금읍", type: "DELIVERY"}

요청:
"백암 _ 저온 → 경산 16판 1대"

출력 형식:
{
  "pickup_client_id": number,
  "delivery_client_id": number,
  "temperature_zone": "FROZEN" | "REFRIGERATED" | "AMBIENT",
  "pallet_count": number,
  "vehicle_count": number,
  "notes": string
}
```

---

### 방안 2: Few-shot Learning + Fine-tuned Model

**장점**:
- 더 정확한 특화 모델
- 비용 절감 (장기적)
- 회사 특화 패턴 학습

**구조**:
```
훈련 데이터 수집 (100-500건)
  → GPT-4 fine-tuning
  → 모델 배포
  → 실시간 추론
```

**필요 데이터**:
```json
[
  {
    "input": "백암 _ 저온 → 경산 16판 1대",
    "output": {
      "pickup_client_id": 1,
      "delivery_client_id": 5,
      "temperature_zone": "REFRIGERATED",
      "pallet_count": 16
    }
  },
  {
    "input": "2/3(화)목우촌 오후배차 15:30 / 육가공5톤",
    "output": {
      "pickup_client_id": 8,
      "delivery_client_id": null,
      "pickup_time": "15:30",
      "vehicle_type": "5TON"
    }
  }
]
```

---

### 방안 3: Hybrid (규칙 + LLM + 학습)

**장점**:
- 최고 정확도
- 점진적 개선
- 사람 검증 최소화

**구조**:
```
1단계: 규칙 기반 전처리
  - 날짜 추출: "02/03", "2/3(화)" → 2026-02-03
  - 숫자 추출: "16판" → 16, "5톤" → 5000kg
  - 온도 키워드: "저온", "냉동", "냉장", "상온"

2단계: 거래처 매칭 (Fuzzy + Vector DB)
  - "백암" → DB 검색 → id: 1
  - "경산" → DB 검색 → id: 5
  - Levenshtein distance < 2
  - 또는 Vector embedding 유사도 > 0.85

3단계: LLM 보완
  - 애매한 경우만 LLM 호출
  - 새로운 거래처명 추론
  - 온도대 추론

4단계: 사용자 검증
  - 신뢰도 < 80% → 사용자 확인
  - 확인된 데이터 → 훈련 DB 추가

5단계: 지속 학습
  - 월 1회 모델 재학습
  - 새로운 패턴 반영
```

---

## 💻 구현 방안 (방안 1 기준)

### 1. 백엔드 API 구조

```python
# backend/app/services/order_nlp_service.py
from openai import OpenAI
import re
from datetime import datetime
from typing import Dict, List, Optional

class OrderNLPService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def parse_order_request(self, text: str) -> List[Dict]:
        """자연어 주문 요청을 파싱"""
        
        # 1. 전처리
        preprocessed = self._preprocess(text)
        
        # 2. 거래처 DB 가져오기
        clients = self._get_clients_context()
        
        # 3. LLM 호출
        parsed_orders = await self._call_llm(preprocessed, clients)
        
        # 4. 후처리 및 검증
        validated_orders = self._validate_and_enrich(parsed_orders)
        
        return validated_orders
    
    def _preprocess(self, text: str) -> str:
        """전처리: 날짜, 특수문자 정규화"""
        # 날짜 추출
        date_pattern = r'(\d{1,2})/(\d{1,2})'
        text = re.sub(date_pattern, lambda m: f"2026-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}", text)
        
        # 온도 키워드 정규화
        temp_map = {
            '저온': 'REFRIGERATED',
            '냉장': 'REFRIGERATED',
            '냉동': 'FROZEN',
            '상온': 'AMBIENT'
        }
        for key, value in temp_map.items():
            text = text.replace(key, f"[{value}]")
        
        return text
    
    def _get_clients_context(self) -> str:
        """거래처 DB를 LLM이 이해할 수 있는 형태로 변환"""
        clients = self.db.query(Client).filter(Client.is_active == True).all()
        
        context = "거래처 데이터베이스:\n"
        for client in clients:
            context += f"- {client.name} (코드: {client.code}, 주소: {client.address}, 타입: {client.client_type})\n"
        
        return context
    
    async def _call_llm(self, text: str, clients_context: str) -> List[Dict]:
        """LLM 호출"""
        prompt = f"""당신은 물류 주문 처리 전문가입니다. 
거래처 요청을 분석하여 구조화된 주문 정보로 변환하세요.

{clients_context}

규칙:
1. 날짜는 YYYY-MM-DD 형식
2. 온도대는 FROZEN, REFRIGERATED, AMBIENT 중 하나
3. 거래처명은 위 DB에서 가장 유사한 것으로 매칭
4. "판"은 pallet_count, "톤"은 weight_kg로 변환
5. 화살표(→) 또는 "에서~로" 패턴으로 상차지/하차지 구분

요청:
{text}

출력 형식 (JSON Array):
[
  {{
    "order_date": "YYYY-MM-DD",
    "pickup_client_name": "거래처명",
    "delivery_client_name": "거래처명",
    "temperature_zone": "FROZEN|REFRIGERATED|AMBIENT",
    "pallet_count": number,
    "weight_kg": number or null,
    "pickup_time": "HH:MM" or null,
    "notes": "추가 정보",
    "confidence": 0.0-1.0
  }}
]
"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # 빠르고 저렴
            messages=[
                {"role": "system", "content": "You are a logistics order processing expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 일관성 우선
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        return json.loads(result)
    
    def _validate_and_enrich(self, orders: List[Dict]) -> List[Dict]:
        """검증 및 DB 매칭"""
        validated = []
        
        for order in orders:
            # 거래처 매칭
            pickup_client = self._match_client(order['pickup_client_name'])
            delivery_client = self._match_client(order['delivery_client_name'])
            
            if pickup_client:
                order['pickup_client_id'] = pickup_client.id
                order['pickup_address'] = pickup_client.address
            
            if delivery_client:
                order['delivery_client_id'] = delivery_client.id
                order['delivery_address'] = delivery_client.address
            
            # 신뢰도 체크
            if order.get('confidence', 0) < 0.7:
                order['needs_review'] = True
            
            validated.append(order)
        
        return validated
    
    def _match_client(self, client_name: str) -> Optional[Client]:
        """거래처명 매칭 (Fuzzy)"""
        from fuzzywuzzy import fuzz
        
        clients = self.db.query(Client).filter(Client.is_active == True).all()
        
        best_match = None
        best_score = 0
        
        for client in clients:
            score = fuzz.ratio(client_name, client.name)
            if score > best_score:
                best_score = score
                best_match = client
        
        # 80% 이상 유사도만 매칭
        if best_score >= 80:
            return best_match
        
        return None
```

### 2. API 엔드포인트

```python
# backend/app/api/orders.py
@router.post("/parse-nlp")
async def parse_order_nlp(
    request: dict,
    db: Session = Depends(get_db)
):
    """자연어 주문 파싱"""
    text = request.get('text', '')
    
    if not text:
        raise HTTPException(status_code=400, detail="텍스트가 필요합니다")
    
    nlp_service = OrderNLPService(db)
    parsed_orders = await nlp_service.parse_order_request(text)
    
    return {
        "success": True,
        "orders": parsed_orders,
        "count": len(parsed_orders)
    }
```

### 3. 프론트엔드 UI

```tsx
// frontend/src/components/orders/OrderNLPInput.tsx
function OrderNLPInput() {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [parsedOrders, setParsedOrders] = useState([])

  const handleParse = async () => {
    setLoading(true)
    try {
      const response = await ordersAPI.parseNLP({ text })
      setParsedOrders(response.data.orders)
    } catch (err) {
      alert('파싱 실패')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <h3>📝 자연어 주문 입력</h3>
      
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="예: [02/03] 추가 배차요청&#10;백암 _ 저온 → 경산 16판 1대"
        rows={8}
        style={{ width: '100%', padding: '12px', fontSize: '14px' }}
      />
      
      <button 
        onClick={handleParse}
        disabled={loading || !text}
        className="button"
      >
        {loading ? '🤖 분석 중...' : '🤖 AI 파싱'}
      </button>

      {parsedOrders.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h4>파싱 결과 ({parsedOrders.length}건)</h4>
          {parsedOrders.map((order, idx) => (
            <div key={idx} style={{ 
              padding: '12px', 
              border: '1px solid #ddd', 
              borderRadius: '4px',
              marginBottom: '10px',
              backgroundColor: order.needs_review ? '#fff3cd' : '#d4edda'
            }}>
              <div><strong>주문 {idx + 1}</strong></div>
              <div>상차: {order.pickup_client_name}</div>
              <div>하차: {order.delivery_client_name}</div>
              <div>온도: {order.temperature_zone}</div>
              <div>팔레트: {order.pallet_count}개</div>
              {order.needs_review && (
                <div style={{ color: '#856404', marginTop: '8px' }}>
                  ⚠️ 신뢰도 낮음 - 확인 필요
                </div>
              )}
              <button 
                onClick={() => handleCreateOrder(order)}
                className="button secondary"
                style={{ marginTop: '8px' }}
              >
                ✓ 주문 생성
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
```

---

## 📊 성능 및 비용

### LLM 호출 비용 (GPT-4o-mini)
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens
- 주문 1건당 약 500 tokens (입력 400 + 출력 100)
- **비용: 약 $0.0003 (0.4원) per 주문**

### 예상 정확도
- 1단계 (규칙 기반): 60-70%
- 2단계 (Fuzzy 매칭): 80-85%
- 3단계 (LLM): 95-98%
- **전체: 95%+ 정확도**

### 처리 속도
- 전처리: 10ms
- Fuzzy 매칭: 50ms
- LLM 호출: 1-2초
- **전체: 약 2초 per 요청**

---

## 🎯 구현 우선순위

### Phase 1: MVP (1-2주)
1. ✅ 전처리 함수 구현
2. ✅ LLM 통합 (GPT-4o-mini)
3. ✅ 기본 UI (텍스트 입력 → 파싱)
4. ✅ 거래처 Fuzzy 매칭

### Phase 2: 개선 (2-3주)
1. ✅ 신뢰도 점수 추가
2. ✅ 사용자 검증 UI
3. ✅ 검증된 데이터 학습 DB 저장
4. ✅ 배치 처리 (여러 주문 동시 파싱)

### Phase 3: 고도화 (1-2개월)
1. ✅ Fine-tuned 모델 훈련
2. ✅ Vector DB 통합 (거래처 검색)
3. ✅ 자동 학습 파이프라인
4. ✅ 대시보드 (파싱 성공률, 오류율)

---

## 🚀 즉시 시작 가능한 솔루션

```bash
# 1. OpenAI API 키 설정
export OPENAI_API_KEY="sk-..."

# 2. 필요 패키지 설치
pip install openai fuzzywuzzy python-Levenshtein

# 3. 테스트 스크립트 실행
python test_order_nlp.py
```

---

## 💡 권장 사항

1. **방안 1 (규칙 + LLM)로 시작** ← 가장 빠르고 효과적
2. 100-200건 데이터 수집 후 **Fine-tuning 고려**
3. 사용자 피드백 루프 구축
4. 월 1회 성능 리뷰 및 모델 업데이트

---

**질문이나 추가 요구사항 있으시면 말씀해주세요!** 🚀
