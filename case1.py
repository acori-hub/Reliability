def register_user(data):
    # 사용자 정보 등록 처리 (예: DB 저장)
    print(f"Registering user: {data['username']} with age {data['age']}")

def handle_request():
    # 외부 입력 예시
    input_data = {
        "username": "alice",
        "age": "twenty"  # 문자열 숫자 아님
    }
    register_user(input_data)

handle_request()

# 문제 설명:
# - 'age'가 문자열 "twenty"로 숫자 아님
# - 숫자 여부 및 값 범위 검증이 없음
# - 예외 없이 진행되면 논리 오류 발생 가능
# - 실제 서비스에서는 타입, 형식, 유효 범위 검사가 반드시 필요
