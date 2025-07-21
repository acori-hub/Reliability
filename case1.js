function getUserProfile() {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      reject("Failed to fetch user");
    }, 1000);
  });
}

function run() {
  getUserProfile().then((profile) => {
    console.log("User:", profile.name);
  });

  console.log("Request sent");
}

run();

// 문제 설명:
// - Promise에서 reject 발생 시 .catch()가 없어 오류가 처리되지 않음
// - profile이 undefined 상태에서 접근하면 후속 에러 발생 가능
// - 비동기 오류 흐름을 고려하지 않은 구성
