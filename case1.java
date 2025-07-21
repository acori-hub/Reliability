public class UserService {
    public static void main(String[] args) {
        User user = new User("bob123", "");
        saveUser(user);
    }

    public static void saveUser(User user) {
        // DB 저장 로직 (생략)
        System.out.println("Saving user " + user.username + " with email " + user.email);
    }
}

class User {
    String username;
    String email;

    public User(String username, String email) {
        this.username = username;
        this.email = email;  // 빈 문자열 가능
    }
}

// 문제 설명:
// - email 필드가 빈 문자열임에도 저장 시도
// - 이메일 형식 검증이 없음 (@ 포함 여부, 도메인 확인 등)
// - 유효성 검사 없이 잘못된 데이터가 저장되어 시스템 정합성 깨질 수 있음
