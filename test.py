import os
import openai

# OpenAI API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# 챗봇 대화 진행 함수
def chat(prompt):
    response = openai.Completion.create(  # 수정 - openai.Completion.create 대신 사용
        engine="text-embedding-ada-002",  # 엔진 명칭도 변경 (OpenAI 문서 확인)
        prompt=prompt,
        temperature=0.7,
        max_tokens=1000,
    )
    return response.choices[0].text

# 사용자 입력 반복 및 챗봇 대화
while True:
  # 사용자 입력 받기
  user_input = input("말씀해주세요: ")

  # 챗봇 응답 생성
  bot_response = chat(prompt=user_input)

  # 챗봇 응답 출력
  print(f"챗봇: {bot_response}")