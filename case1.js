function submitOrder(order) {
  // 주문 처리 (예: 결제 요청)
  console.log(`Processing order for quantity: ${order.quantity}`);
  // 실제 결제 API 호출 생략
}

function simulateClientRequest() {
  const orderData = {
    productId: "SKU12345",
    quantity: -3, // 잘못된 입력
  };
  submitOrder(orderData);
}

simulateClientRequest();

// 문제 설명:
// - quantity가 음수인데도 검증 없이 처리됨
// - isNaN, 타입 체크, 값 범위 확인 없음
// - 악의적인 입력으로 오작동 가능성 있음
