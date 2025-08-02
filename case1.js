function createUserProfile(name, ageStr) {
  const age = parseInt(ageStr);

  const user = {
    name: name.trim(),
    age: age,
    createdAt: new Date().toISOString(),
  };

  console.log("사용자 프로필 생성 완료:", user);
  return user;
}

const inputName = prompt("이름을 입력하세요:");
const inputAge = prompt("나이를 입력하세요:");

createUserProfile(inputName, inputAge);
