import requests

def fetch_exchange_rate():
    response = requests.get("https://api.exchangerate.example.com/latest")
    data = response.json()
    print("USD to EUR:", data["rates"]["EUR"])

fetch_exchange_rate()

# ❌ 문제점:
# - 외부 API 호출 실패, 타임아웃, 잘못된 응답이 발생해도 예외 처리가 없음
# - 요청 실패 시 런타임 에러로 프로그램이 중단될 수 있음
# - 재시도, fallback 등의 대안 로직 부재
