async function getStockPrice() {
  const res = await fetch("https://api.stock.example.com/price");
  const data = await res.json();
  console.log("Stock price:", data.price);
}

getStockPrice();

//
// ❌ 문제점:
// - fetch 실패 또는 응답 상태가 200이 아닐 경우 오류가 발생하지만 예외 처리가 없음
// - 네트워크 장애나 API 서버 문제 발생 시 사용자에게 아무런 안내 없이 앱이 중단될 수 있음
// - 실패 시 fallback 또는 오류 메시지도 제공하지 않음
