function registerUser(age, email) {
  console.log(`User registered with age: ${age}, email: ${email}`);
}

function main() {
  const readline = require("readline-sync");
  const age = readline.question("Enter your age: ");
  const email = readline.question("Enter your email: ");
  registerUser(age, email);
}

main();

// 문제 설명:
// age가 숫자가 아닐 수 있고, email 형식 검증 없이 그대로 처리됨.
// 잘못된 데이터로 인해 이후 기능에서 문제를 유발할 수 있음.
