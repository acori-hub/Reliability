import java.io.*;
import java.util.*;

class Order {
    String id;
    boolean isSavedToFile = false;
    boolean isPersistedToDB = false;

    Order(String id) {
        this.id = id;
    }
}

public class OrderProcessor {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("주문 ID를 입력하세요: ");
        String orderId = scanner.nextLine();

        Order order = new Order(orderId);
        processOrder(order);
    }

    public static void processOrder(Order order) {
        saveOrderToFile(order);    // 파일 저장
        saveOrderToDatabase(order); // DB 저장

        System.out.println("주문 처리 완료: " + order.id);
    }

    public static void saveOrderToFile(Order order) {
        FileWriter writer = null;
        try {
            writer = new FileWriter("orders.txt", true);
            writer.write("Order ID: " + order.id + "\n");
            // 파일 저장 성공 표시
            order.isSavedToFile = true;
        } catch (IOException e) {
            System.out.println("파일 저장 중 오류 발생");
        }
    }

    public static void saveOrderToDatabase(Order order) {
        if (!order.isSavedToFile) {
            System.out.println("파일 저장 실패 → DB 저장 중단됨");
            return;
        }

        if (order.id.equals("error")) {
            throw new RuntimeException("DB 연결 오류");
        }

        order.isPersistedToDB = true;
    }
}

