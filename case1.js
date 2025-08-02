async function fetchPosts(page, limit) {
  const url = `https://api.example.com/posts?page=${page}&limit=${limit}`;

  const response = await fetch(url);
  const data = await response.json();

  console.log(`총 ${data.length}개의 게시물이 로드되었습니다.`);
  return data;
}

function main() {
  const page = parseInt(prompt("페이지 번호를 입력하세요:"));
  const limit = parseInt(prompt("가져올 게시물 수를 입력하세요:"));

  fetchPosts(page, limit)
    .then((posts) => {
      console.log("게시물:", posts);
    })
    .catch((err) => {
      console.error("API 호출 실패:", err);
    });
}

main();
