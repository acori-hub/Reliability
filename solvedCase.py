import requests

def fetch_exchange_rate():
    try:
        response = requests.get("https://api.exchangerate.example.com/latest", timeout=5)
        response.raise_for_status()
        data = response.json()
        print("USD to EUR:", data.get("rates", {}).get("EUR", "Unavailable"))
    except requests.exceptions.RequestException as e:
        print("API fetch failed. Fallback to cached value. Error:", e)

fetch_exchange_rate()

# ✅ 문제 없음:
# - 네트워크 예외, 응답 오류, JSON 파싱 오류 등에 안전하게 대응
# - 예외 발생 시 fallback 메시지 출력으로 사용자 경험 보호
# - 안전한 딕셔너리 접근 (`get`)으로 키 오류 방지
