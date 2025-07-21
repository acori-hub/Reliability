def send_welcome_email(user):
    print(f"Sending welcome email to {user['email']}")

def process_new_user():
    new_user = {
        "username": "charlie"
    }
    send_welcome_email(new_user)

process_new_user()

# 문제 설명:
# - user 딕셔너리에 'email' 키가 없음 → KeyError 발생
# - None 여부, 키 존재 여부 확인 없이 딕셔너리 접근
# - 필수 값이 누락되었을 때의 방어 코드가 없음
