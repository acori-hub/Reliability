import java.util.concurrent.CompletableFuture;

public class AsyncService {
    public static void main(String[] args) {
        fetchUser().thenAccept(user -> {
            System.out.println("User name: " + user.name);
        });
        System.out.println("Async request sent");
    }

    public static CompletableFuture<User> fetchUser() {
        return CompletableFuture.supplyAsync(() -> {
            throw new RuntimeException("Failed to fetch user");
        });
    }
}

class User {
    public String name;
    public User(String name) {
        this.name = name;
    }
}

// 문제 설명:
// - CompletableFuture 내부에서 예외 발생 시 후속 thenAccept에서 예외 전파됨
// - exceptionally 또는 handle 메서드를 사용해 예외를 처리하지 않음
// - 비동기 흐름에서 예외가 누락되면 프로그램 전체 안정성 저하
