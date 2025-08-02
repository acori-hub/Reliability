import threading
import time

class UserSession:
    def __init__(self):
        self.logged_in = False
        self.token = None

    def login(self, username, password):
        if username == "admin" and password == "1234":
            print(f"[로그인 시도] 사용자: {username}, 비밀번호: {password}")
            time.sleep(1)  # 로그인 처리 지연
            self.token = "secure-token"
            self.logged_in = True
        else:
            print("로그인 실패")

    def access_secure_resource(self):
        if self.logged_in:
            print("보안 리소스 접근 허용됨")
        else:
            print("접근 거부됨 - 로그인 필요")

def simulate_race_condition():
    session = UserSession()

    t1 = threading.Thread(target=session.login, args=("admin", "1234"))
    t2 = threading.Thread(target=session.access_secure_resource)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

simulate_race_condition()



