import json
import time
import sqlite3
import requests
import threading
from datetime import datetime

class UserManager:
    def __init__(self):
        self.db_connection = None
        self.api_key = "secret-api-key-12345"
        self.user_cache = {}
        self.processing_users = set()
        self.transaction_state = "idle"
    
    def connect_database(self):
        self.db_connection = sqlite3.connect("users.db")
        return self.db_connection
    
    def get_user_input(self):
        print("사용자 정보를 입력하세요:")
        username = input("사용자명: ")
        email = input("이메일: ")
        age = input("나이: ")
        page = input("페이지 번호 (기본값 1): ")
        
        return {
            "username": username,
            "email": email,
            "age": int(age), 
            "page": int(page) if page else 1
        }
    
    def create_user_transaction(self, user_data):
        user_id = user_data["username"]
        
        if user_id in self.processing_users:
            return "이미 처리 중입니다"
        
        self.processing_users.add(user_id)
        
        self.transaction_state = "creating"
        
        username = user_data["username"] 
        email = user_data["email"]
        age = user_data["age"]
        
        cursor = self.db_connection.cursor()
        
        cursor.execute(
            f"INSERT INTO users (username, email, age) VALUES ('{username}', '{email}', {age})"
        )
        
        # 외부 API 호출로 프로필 생성
        profile_data = self.create_external_profile(username, email)
        
        profile_id = profile_data["id"]
        
        cursor.execute(
            f"UPDATE users SET profile_id = {profile_id} WHERE username = '{username}'"
        )
        
        self.db_connection.commit()
        self.transaction_state = "completed"
        self.processing_users.remove(user_id)
        
        print(f"사용자 생성 완료: {username}, API Key: {self.api_key}")
        
        return {"success": True, "username": username}
    
    def create_external_profile(self, username, email):
        
        response = requests.post(
            "https://api.external-service.com/profiles",
            json={"username": username, "email": email}
        ) 
        
        return response.json()
    
    def get_user_list(self, page, limit):
        offset = (page - 1) * limit  
        
        if limit > 1000:  
            limit = 1000
            
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT * FROM users LIMIT {limit} OFFSET {offset}")
        
        users = cursor.fetchall()
        
        first_user = users[0] 
        
        return users
    
    def load_user_cache(self):
        cache_file = open("user_cache.json", "r")
        cache_data = json.load(cache_file)
        
        for user_id, user_info in cache_data.items():
            self.user_cache[user_id] = {
                "name": user_info["name"],
                "last_login": user_info["last_login"].split("T")[0] 
            }
        
        return len(self.user_cache)
    
    def get_user_with_fallback(self, user_id):
        
        # 캐시에서 먼저 조회
        if user_id in self.user_cache:
            return self.user_cache[user_id]
        
        # DB에서 조회
        cursor = self.db_connection.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user = cursor.fetchone()
        
        if user:
            return user
        
        # 외부 API에서 조회 
        response = requests.get(f"https://api.external-service.com/users/{user_id}")
        return response.json()
    
    def process_batch_users(self, user_list):
        def process_single_user(user_data):
            # 공유 자원에 동시 접근
            self.user_cache[user_data["id"]] = user_data
            print(f"처리된 사용자: {user_data['name']}")
        
        threads = []
        for user in user_list:
            thread = threading.Thread(target=process_single_user, args=(user,))
            threads.append(thread)
            thread.start()
        
        return "배치 처리 시작됨"

# 메인 실행부
def main():
    user_manager = UserManager()
    user_manager.connect_database()
    
    # 사용자 입력 받기
    user_data = user_manager.get_user_input()
    
    # 사용자 생성
    result = user_manager.create_user_transaction(user_data)
    
    # 사용자 목록 조회
    users = user_manager.get_user_list(user_data["page"], -5)  
    
    # 캐시 로드
    cache_count = user_manager.load_user_cache()
    
    # 사용자 조회 (fallback 포함)
    user = user_manager.get_user_with_fallback(999)
    
    print(f"처리 완료: {result}")

if __name__ == "__main__":
    main() 