function greetUser(user) {
  console.log(`Hello, ${user.name.toUpperCase()}!`);
}

const userData = {
  id: 101,
};

greetUser(userData);

// 문제 설명:
// - user.name이 undefined인 상태에서 toUpperCase() 호출 → TypeError 발생
// - null/undefined 확인 없이 속성 접근하여 런타임 에러 발생 가능
