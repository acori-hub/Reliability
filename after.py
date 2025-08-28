import requests
import json
import sqlite3
import logging
import time
import re
import hashlib
from contextlib import contextmanager
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import threading

# 설정 관리
@dataclass
class Config:
    API_ENDPOINT: str = "https://bank-api.com/transfer"
    MAX_TRANSFER_AMOUNT: float = 1000000.0
    MIN_TRANSFER_AMOUNT: float = 0.01
    API_TIMEOUT_SECONDS: int = 30
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_BASE: float = 2.0
    MAX_PAGE_LIMIT: int = 100
    
CONFIG = Config()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('transactions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TransferService:
    def __init__(self, api_key_hash: str):
        self._api_key_hash = api_key_hash
        self._db_lock = threading.Lock()
        self._init_database()
    
    def _init_database(self) -> None:
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect("transactions.db") as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accounts (
                        user_id TEXT PRIMARY KEY,
                        balance REAL NOT NULL CHECK(balance >= 0)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        status TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES accounts (user_id)
                    )
                """)
                connection.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as database_error:
            logger.error(f"Database initialization failed: {str(database_error)}")
            raise
    
    @contextmanager
    def _get_database_connection(self):
        """데이터베이스 연결 관리 - 리소스 누수 방지"""
        connection = None
        try:
            connection = sqlite3.connect("transactions.db")
            connection.row_factory = sqlite3.Row
            yield connection
        except sqlite3.Error as database_error:
            if connection:
                connection.rollback()
            logger.error(f"Database error: {str(database_error)}")
            raise
        finally:
            if connection:
                connection.close()
    
    def _validate_user_input(self, user_id: str, to_account: str, amount: float, memo: str) -> None:
        """입력값 검증"""
        if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
            raise ValueError("Invalid user_id: must be non-empty string")
        
        if not to_account or not isinstance(to_account, str):
            raise ValueError("Invalid to_account: must be non-empty string")
        
        # 계정 형식 검증 (영숫자, 하이픈만 허용)
        if not re.match(r'^[a-zA-Z0-9\-]+$', to_account):
            raise ValueError("Invalid account format")
        
        if not isinstance(amount, (int, float)) or amount <= CONFIG.MIN_TRANSFER_AMOUNT:
            raise ValueError(f"Amount must be greater than {CONFIG.MIN_TRANSFER_AMOUNT}")
        
        if amount > CONFIG.MAX_TRANSFER_AMOUNT:
            raise ValueError(f"Amount exceeds maximum limit: {CONFIG.MAX_TRANSFER_AMOUNT}")
        
        if memo and len(memo) > 200:
            raise ValueError("Memo too long: maximum 200 characters")
    
    def _get_user_balance(self, connection: sqlite3.Connection, user_id: str) -> Optional[float]:
        """사용자 잔액 조회 - SQL 인젝션 방지"""
        cursor = connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result['balance'] if result else None
    
    def _call_external_api_with_retry(self, transfer_data: Dict) -> Dict:
        """외부 API 호출 - 재시도 및 백오프 로직"""
        for attempt in range(CONFIG.MAX_RETRY_ATTEMPTS):
            try:
                # 민감정보 마스킹된 로그
                masked_data = {**transfer_data}
                masked_data['api_key'] = "***MASKED***"
                logger.info(f"API call attempt {attempt + 1}: {masked_data}")
                
                response = requests.post(
                    CONFIG.API_ENDPOINT,
                    json=transfer_data,
                    timeout=CONFIG.API_TIMEOUT_SECONDS,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    wait_time = CONFIG.RETRY_BACKOFF_BASE ** attempt
                    logger.warning(f"Rate limited, waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"API error: {response.status_code} - {response.text}")
                    if attempt == CONFIG.MAX_RETRY_ATTEMPTS - 1:
                        raise requests.HTTPError(f"API call failed: {response.status_code}")
                    
            except requests.Timeout:
                logger.warning(f"API timeout on attempt {attempt + 1}")
                if attempt == CONFIG.MAX_RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(CONFIG.RETRY_BACKOFF_BASE ** attempt)
            except requests.RequestException as request_error:
                logger.error(f"Request error on attempt {attempt + 1}: {str(request_error)}")
                if attempt == CONFIG.MAX_RETRY_ATTEMPTS - 1:
                    raise
                time.sleep(CONFIG.RETRY_BACKOFF_BASE ** attempt)
        
        raise Exception("All API retry attempts failed")
    
    def transfer_money(self, user_id: str, to_account: str, amount: float, memo: str = "") -> Dict:
        """안전한 송금 처리"""
        try:
            # 입력값 검증
            self._validate_user_input(user_id, to_account, amount, memo)
            
            with self._db_lock:  # 경쟁 상태 방지
                with self._get_database_connection() as connection:
                    # 트랜잭션 시작
                    connection.execute("BEGIN IMMEDIATE")
                    
                    try:
                        # 잔액 확인
                        current_balance = self._get_user_balance(connection, user_id)
                        if current_balance is None:
                            raise ValueError("User account not found")
                        
                        if current_balance < amount:
                            raise ValueError("Insufficient balance")
                        
                        # 외부 API 호출
                        api_request = {
                            "api_key": self._api_key_hash,
                            "from_account": user_id,
                            "to_account": to_account,
                            "amount": round(amount, 2),
                            "memo": memo[:200]  # 길이 제한
                        }
                        
                        api_response = self._call_external_api_with_retry(api_request)
                        
                        if not api_response.get("transfer_id"):
                            raise ValueError("Invalid API response: missing transfer_id")
                        
                        # 데이터베이스 업데이트 (원자적 처리)
                        cursor = connection.cursor()
                        cursor.execute(
                            "UPDATE accounts SET balance = balance - ? WHERE user_id = ?",
                            (amount, user_id)
                        )
                        cursor.execute(
                            "INSERT INTO transactions (user_id, amount, status) VALUES (?, ?, ?)",
                            (user_id, amount, "completed")
                        )
                        
                        connection.commit()
                        
                        logger.info(f"Transfer completed successfully: {user_id} -> {to_account}, amount: {amount}")
                        return {
                            "status": "success",
                            "transfer_id": api_response["transfer_id"],
                            "amount": amount,
                            "remaining_balance": current_balance - amount
                        }
                        
                    except Exception as transaction_error:
                        connection.rollback()
                        logger.error(f"Transaction rolled back due to error: {str(transaction_error)}")
                        raise
                        
        except ValueError as validation_error:
            logger.warning(f"Validation error: {str(validation_error)}")
            return {"status": "failed", "error": "Invalid input", "details": str(validation_error)}
        except requests.RequestException as api_error:
            logger.error(f"External API error: {str(api_error)}")
            return {"status": "failed", "error": "External service unavailable", "retry_after": 60}
        except Exception as unexpected_error:
            logger.error(f"Unexpected error in transfer: {str(unexpected_error)}")
            return {"status": "failed", "error": "Internal service error"}
    
    def get_transaction_history(self, user_id: str, page: int, limit: int) -> Dict:
        """안전한 거래 내역 조회"""
        try:
            # 입력값 검증 및 경계 조건 처리
            if not user_id or not isinstance(user_id, str):
                raise ValueError("Invalid user_id")
            
            if not isinstance(page, int) or page < 0:
                raise ValueError("Page must be non-negative integer")
            
            if not isinstance(limit, int) or limit <= 0 or limit > CONFIG.MAX_PAGE_LIMIT:
                raise ValueError(f"Limit must be between 1 and {CONFIG.MAX_PAGE_LIMIT}")
            
            offset = page * limit
            
            with self._get_database_connection() as connection:
                cursor = connection.cursor()
                # 매개변수화된 쿼리로 SQL 인젝션 방지
                cursor.execute("""
                    SELECT id, amount, status, created_at 
                    FROM transactions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (user_id, limit, offset))
                
                transactions = [dict(row) for row in cursor.fetchall()]
                
                # 총 개수 조회
                cursor.execute("SELECT COUNT(*) as total FROM transactions WHERE user_id = ?", (user_id,))
                total_count = cursor.fetchone()['total']
                
                return {
                    "status": "success",
                    "transactions": transactions,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "has_next": offset + limit < total_count
                    }
                }
                
        except ValueError as validation_error:
            logger.warning(f"Invalid pagination parameters: {str(validation_error)}")
            return {"status": "failed", "error": str(validation_error)}
        except sqlite3.Error as database_error:
            logger.error(f"Database error in transaction history: {str(database_error)}")
            return {"status": "failed", "error": "Database service unavailable"}
        except Exception as unexpected_error:
            logger.error(f"Unexpected error in transaction history: {str(unexpected_error)}")
            return {"status": "failed", "error": "Internal service error"}

def main():
    """메인 실행 함수 - 안전한 사용자 입력 처리"""
    try:
        # 환경변수에서 API 키 로드 (실제 환경에서)
        api_key_hash = hashlib.sha256("actual_api_key".encode()).hexdigest()
        service = TransferService(api_key_hash)
        
        logger.info("Transfer service started")
        
        while True:
            try:
                user_input = input("Enter command (transfer,history,quit): ").strip()
                
                if user_input.lower() == "quit":
                    logger.info("Service shutting down")
                    break
                
                if not user_input:
                    continue
                
                parts = [part.strip() for part in user_input.split(",")]
                
                if len(parts) < 1:
                    print("Invalid command format")
                    continue
                
                command = parts[0].lower()
                
                if command == "transfer":
                    if len(parts) < 4:
                        print("Transfer format: transfer,user_id,to_account,amount[,memo]")
                        continue
                    
                    memo = parts[4] if len(parts) > 4 else ""
                    try:
                        amount = float(parts[3])
                        result = service.transfer_money(parts[1], parts[2], amount, memo)
                        print(f"Transfer result: {result}")
                    except ValueError as value_error:
                        print(f"Invalid amount: {parts[3]}")
                        
                elif command == "history":
                    if len(parts) < 4:
                        print("History format: history,user_id,page,limit")
                        continue
                    
                    try:
                        page = int(parts[2])
                        limit = int(parts[3])
                        result = service.get_transaction_history(parts[1], page, limit)
                        print(f"History result: {result}")
                    except ValueError as value_error:
                        print(f"Invalid page/limit parameters")
                else:
                    print("Unknown command. Available: transfer, history, quit")
                    
            except KeyboardInterrupt:
                logger.info("Service interrupted by user")
                break
            except Exception as input_error:
                logger.error(f"Error processing user input: {str(input_error)}")
                print("An error occurred. Please try again.")
                
    except Exception as startup_error:
        logger.error(f"Service startup failed: {str(startup_error)}")
        print("Service failed to start. Check logs for details.")

if __name__ == "__main__":
    main()