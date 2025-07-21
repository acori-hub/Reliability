public class OrderService {
    public static void main(String[] args) {
        Order order = null;
        printOrderSummary(order);
    }

    public static void printOrderSummary(Order order) {
        System.out.println("Order amount: " + order.amount);
    }
}

class Order {
    public int amount;

    public Order(int amount) {
        this.amount = amount;
    }
}

// 문제 설명:
// - order 객체가 null임에도 필드 접근 시도 → NullPointerException 발생
// - 널 체크 없이 객체 접근하는 전형적인 문제
