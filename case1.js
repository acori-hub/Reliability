function fetchUserData(userId) {
  const response = fetch(`https://api.example.com/users/${userId}`);
  return response.then(res => res.json());
}

fetchUserData("not-a-number")
  .then(data => console.log(data));
