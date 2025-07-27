import java.util.Scanner;

public class UserRegistration {
    public static void registerUser(int age, String email) {
        System.out.println("User registered: age=" + age + ", email=" + email);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter age: ");
        int age = Integer.parseInt(scanner.nextLine());
        System.out.print("Enter email: ");
        String email = scanner.nextLine();

        registerUser(age, email);
    }
}

// 문제 설명:
// age가 음수이거나 0인 경우, 또는 이메일 형식이 잘못돼도 검증 없이 그대로 등록됨.
// 추후 시스템 오류나 잘못된 동작의 원인이 될 수 있음.
