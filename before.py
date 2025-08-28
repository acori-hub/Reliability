import requests
import json
import sqlite3

# 글로벌 변수들
db = None
api_key = "sk_live_12345abcdef"  # 하드코딩된 API 키
MAX_AMOUNT = 1000000

def init_db():
    global db
    db = sqlite3.connect("transactions.db", check_same_thread=False)
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id TEXT,
            amount REAL,
            status TEXT
        )
    """)

def transfer_money(user_id, to_account, amount, memo):
    # 입력 검증 없음
    print(f"Processing transfer: {user_id} -> {to_account}, amount: {amount}")
    
    # SQL 인젝션 취약점
    cursor = db.cursor()
    query = f"SELECT balance FROM accounts WHERE user_id = '{user_id}'"
    result = cursor.execute(query).fetchone()
    
    balance = result[0]  # None 체크 없음
    
    # 경쟁 상태 - 동시 요청 시 잔액 검증 우회 가능
    if balance >= amount:
        # 외부 API 호출 - 타임아웃 없음, 재시도 없음
        response = requests.post("https://bank-api.com/transfer", {
            "api_key": api_key,  # 로그에 민감정보 노출
            "from": user_id,
            "to": to_account,
            "amount": amount,
            "memo": memo
        })
        
        # 응답 검증 없음
        transfer_id = response.json()["transfer_id"]
        
        # 트랜잭션 없음 - 부분 실패 가능
        cursor.execute(f"UPDATE accounts SET balance = {balance - amount} WHERE user_id = '{user_id}'")
        cursor.execute(f"INSERT INTO transactions VALUES (NULL, '{user_id}', {amount}, 'completed')")
        
        return {"status": "success", "transfer_id": transfer_id}
    
    # 에러 처리 없음
    return {"status": "failed"}

def get_transaction_history(user_id, page, limit):
    # 페이징 검증 없음 - page=-1, limit=999999 가능
    offset = page * limit
    
    # SQL 인젝션 취약점
    query = f"SELECT * FROM transactions WHERE user_id = '{user_id}' LIMIT {limit} OFFSET {offset}"
    cursor = db.cursor()
    results = cursor.execute(query).fetchall()
    
    # 결과 검증 없음
    return results

def main():
    init_db()
    
    # 무한 루프 - 종료 조건 없음
    while True:
        user_input = input("Enter command: ")
        
        # 명령어 파싱 - 예외 처리 없음
        parts = user_input.split(",")
        cmd = parts[0]
        
        if cmd == "transfer":
            # 배열 인덱스 검증 없음
            result = transfer_money(parts[1], parts[2], float(parts[3]), parts[4])
            print(result)
        elif cmd == "history":
            results = get_transaction_history(parts[1], int(parts[2]), int(parts[3]))
            print(results)

if __name__ == "__main__":
    main()