#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('.env')

print("=" * 60)
print("🔍 환경변수 확인")
print("=" * 60)

openai_key = os.getenv("OPENAI_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if openai_key:
    print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...{openai_key[-10:]}")
    print(f"   길이: {len(openai_key)} 자")
else:
    print("❌ OPENAI_API_KEY: 설정되지 않음")

if gemini_key:
    print(f"✅ GEMINI_API_KEY: {gemini_key[:20]}...{gemini_key[-10:]}")
    print(f"   길이: {len(gemini_key)} 자")
else:
    print("❌ GEMINI_API_KEY: 설정되지 않음")

print()
print("=" * 60)
print("🧪 OpenAI API 테스트")
print("=" * 60)

if openai_key:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        print("📡 API 연결 테스트 중...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "안녕! 한 문장으로 간단히 응답해줘."}
            ],
            max_tokens=50
        )
        
        print("✅ OpenAI API 연결 성공!")
        print(f"   모델: gpt-4o")
        print(f"   응답: {response.choices[0].message.content}")
        print(f"   입력 토큰: {response.usage.prompt_tokens}")
        print(f"   출력 토큰: {response.usage.completion_tokens}")
        print(f"   총 토큰: {response.usage.total_tokens}")
        
        # 비용 계산
        input_cost = response.usage.prompt_tokens / 1_000_000 * 5.0
        output_cost = response.usage.completion_tokens / 1_000_000 * 15.0
        total_cost = input_cost + output_cost
        
        print(f"   예상 비용: ${total_cost:.6f} (₩{total_cost * 1300:.2f})")
        
    except Exception as e:
        print(f"❌ OpenAI API 오류: {e}")
else:
    print("⏭️  OpenAI API 키가 없어 건너뜁니다")

print()
print("=" * 60)
print("🧪 Gemini API 테스트")
print("=" * 60)

if gemini_key:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        print("📡 API 연결 테스트 중...")
        response = model.generate_content("안녕! 한 문장으로 간단히 응답해줘.")
        
        print("✅ Gemini API 연결 성공!")
        print(f"   모델: gemini-pro")
        print(f"   응답: {response.text}")
        print(f"   비용: 무료 (일일 제한 있음)")
        
    except Exception as e:
        print(f"❌ Gemini API 오류: {e}")
else:
    print("⏭️  Gemini API 키가 없어 건너뜁니다")

print()
print("=" * 60)
print("✅ 테스트 완료!")
print("=" * 60)
