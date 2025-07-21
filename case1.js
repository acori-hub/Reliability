function paginate(items, page, limit) {
  const start = page * limit;
  const end = start + limit;
  return items.slice(start, end);
}

const data = ["a", "b", "c"];
console.log(paginate(data, 0, 2));
console.log(paginate(data, -1, 2));
console.log(paginate(data, 1, -3));

// ❌ 문제점:
// - 음수 page 또는 limit 값 검증 없음
// - limit가 음수면 slice 인자가 이상하게 작동할 수 있음
// - 범위를 벗어난 인덱스 접근 시 예상치 못한 빈 배열이나 오류 발생 가능
