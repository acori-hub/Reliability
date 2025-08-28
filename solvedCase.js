async function getStockPrice() {
  try {
    const res = await fetch("https://api.stock.example.com/price");
    if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
    const data = await res.json();
    console.log("Stock price:", data?.price ?? "Unknown");
  } catch (err) {
    console.error(
      "Failed to fetch stock price. Using default value. Error:",
      err.message
    );
  }
}

getStockPrice();

//
// ✅ 문제 없음:
// - 네트워크 오류 및 HTTP 상태 오류에 안전하게 대응
// - 예외 발생 시 fallback 메시지 제공
// - 널 병합 연산자(`??`)로 안전한 데이터 출력 처리
