import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    raise Exception("Network error")

async def main():
    result = await fetch_data()
    print("Fetched:", result)

asyncio.run(main())

# 문제 설명:
# - fetch_data 내부에서 예외 발생 시 main에서 처리하지 않아 프로그램이 비정상 종료됨
# - try-except를 통해 예외를 핸들링하지 않음
# - 비동기 함수 호출 시 오류 발생 가능성 고려되지 않음
