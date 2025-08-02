import requests

def fetch_user_data(user_id):
    url = f"https://api.example.com/users/{user_id}"
    response = requests.get(url) 
    data = response.json()  

    print("데이터 가져오기 완료")  

    return data

def main():
    user_id = input("조회할 사용자 ID를 입력하세요: ")
    user_data = fetch_user_data(user_id)
    print(f"사용자 정보: {user_data}")

main()


