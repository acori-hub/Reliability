import java.io.*;
import java.net.*;
import java.util.Scanner;

class Payment {
    String userId;
    int amount;
    boolean paymentProcessed = false;
    boolean receiptSaved = false;

    public Payment(String userId, int amount) {
        this.userId = userId;
        this.amount = amount;
    }
}

public class PaymentService {

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("사용자 ID를 입력하세요: ");
        String userId = scanner.nextLine(); 

        System.out.print("결제 금액을 입력하세요: ");
        int amount = Integer.parseInt(scanner.nextLine()); 

        Payment payment = new Payment(userId, amount);
        processPayment(payment);
    }

    public static void processPayment(Payment payment) {
        sendToPaymentGateway(payment); 
        saveReceipt(payment); 

        System.out.println("결제 완료 처리됨: " + payment.userId);
    }

    public static void sendToPaymentGateway(Payment payment) {
        try {
            // 외부 결제 API 호출 시도 
            URL url = new URL("http://payment.example.com/process?user=" + payment.userId + "&amount=" + payment.amount);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.connect();

            payment.paymentProcessed = true;

        } catch (Exception e) {
            System.out.println("결제 요청 중 오류 발생");
        }
    }

    public static void saveReceipt(Payment payment) {
        FileWriter writer = null;
        try {
            writer = new FileWriter("receipts.txt", true);
            writer.write("결제자: " + payment.userId + ", 금액: " + payment.amount + "\n");
            payment.receiptSaved = true;
        } catch (IOException e) {
            System.out.println("영수증 저장 실패");
        }
    }
}

