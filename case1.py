def register_user(age, email):
    print(f"User registered with age: {age}, email: {email}")

def main():
    age = input("Enter your age: ")
    email = input("Enter your email: ")
    register_user(age, email)

main()

# 문제 설명:
# 사용자가 나이에 숫자가 아닌 문자를 입력하거나,
# 이메일 형식이 잘못되어도 아무런 검증 없이 등록됨.
# 잘못된 데이터가 시스템에 저장될 수 있음.
