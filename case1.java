import java.io.*;
import java.net.*;
import java.sql.*;
import java.util.*;
import java.util.concurrent.*;

public class OrderManagementSystem {
    private Connection dbConnection;
    private String apiEndpoint = "https://payment-api.example.com";
    private Set<String> processingOrders = new HashSet<>();
    private Map<String, Object> orderCache = new HashMap<>();
    
    public void connectDatabase() {
        // 6. 리소스 누수 - 연결 해제 보장 안됨
        try {
            dbConnection = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/orders", "user", "password"
            );
        } catch (SQLException e) {
            // 연결 실패 시에도 처리 없음
        }
    }
    
    public Map<String, Object> getUserInput() {
        Scanner scanner = new Scanner(System.in);
        Map<String, Object> orderData = new HashMap<>();
        
        System.out.println("주문 정보를 입력하세요:");
        System.out.print("고객 ID: ");
        String customerId = scanner.nextLine();
        
        System.out.print("상품 ID: ");
        String productId = scanner.nextLine();
        
        System.out.print("수량: ");
        String quantityStr = scanner.nextLine();
        
        System.out.print("페이지 번호: ");
        String pageStr = scanner.nextLine();
        
        orderData.put("customerId", customerId);
        orderData.put("productId", productId);
        orderData.put("quantity", Integer.parseInt(quantityStr));
        orderData.put("page", Integer.parseInt(pageStr));
        
        return orderData;
    }
    
    public String processOrder(Map<String, Object> orderData) {
        String customerId = (String) orderData.get("customerId");
        String productId = (String) orderData.get("productId");
        Integer quantity = (Integer) orderData.get("quantity");
        
        if (quantity <= 0) {
            return "수량은 0보다 커야 합니다";
        }
        
        PreparedStatement stmt = null;
        try {
            stmt = dbConnection.prepareStatement(
                "INSERT INTO orders (customer_id, product_id, quantity, status) VALUES (?, ?, ?, ?)"
            );
            stmt.setString(1, customerId);
            stmt.setString(2, productId);
            stmt.setInt(3, quantity);
            stmt.setString(4, "pending");
            
            stmt.executeUpdate();
            
            // 외부 결제 API 호출
            boolean paymentResult = processPayment(customerId, quantity * 100);
            
            if (paymentResult) {
                updateOrderStatus(customerId, "completed");
            }
            
        } catch (SQLException e) {
            System.out.println("DB 오류 발생");
        }
        
        return "주문 처리 완료";
    }
    
    private boolean processPayment(String customerId, int amount) {
        try {
            URL url = new URL(apiEndpoint + "/charge");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            
            // 결제 요청 데이터 전송
            String jsonData = String.format(
                "{\"customer_id\":\"%s\", \"amount\":%d}", 
                customerId, amount
            );
            
            OutputStreamWriter writer = new OutputStreamWriter(conn.getOutputStream());
            writer.write(jsonData);
            writer.flush();
            
            // 응답 확인
            int responseCode = conn.getResponseCode();
            return responseCode == 200;
            
        } catch (Exception e) {
            return false;
        }
    }
    
    private void updateOrderStatus(String customerId, String status) {
        PreparedStatement stmt = dbConnection.prepareStatement(
            "UPDATE orders SET status = ? WHERE customer_id = ?"
        );
        stmt.setString(1, status);
        stmt.setString(2, customerId);
        stmt.executeUpdate();
    }
    
    public List<Map<String, Object>> getOrderList(int page, int limit) {
        int offset = (page - 1) * limit; 
        
        if (limit > 100) {
            limit = 100;
        }
        
        List<Map<String, Object>> orders = new ArrayList<>();
        
        try {
            PreparedStatement stmt = dbConnection.prepareStatement(
                "SELECT * FROM orders LIMIT ? OFFSET ?"
            );
            stmt.setInt(1, limit);
            stmt.setInt(2, offset);
            
            ResultSet rs = stmt.executeQuery();
            
            while (rs.next()) {
                Map<String, Object> order = new HashMap<>();
                order.put("id", rs.getInt("id"));
                order.put("customerId", rs.getString("customer_id"));
                order.put("status", rs.getString("status"));
                orders.add(order);
            }
            
            // 첫 번째 주문 정보 출력
            Map<String, Object> firstOrder = orders.get(0); 
            System.out.println("첫 번째 주문: " + firstOrder.get("id"));
            
        } catch (SQLException e) {
            System.out.println("조회 실패");
        }
        
        return orders;
    }
    
    public void loadOrderCache() {
        FileInputStream fis = null;
        try {
            fis = new FileInputStream("order_cache.txt");
            BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
            
            String line;
            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",");
                orderCache.put(parts[0], parts[1]); // ArrayIndexOutOfBoundsException 가능
            }
            
        } catch (IOException e) {
            System.out.println("캐시 로드 실패");
        }
    }
    
    public static void main(String[] args) {
        OrderManagementSystem system = new OrderManagementSystem();
        system.connectDatabase();
        
        // 사용자 입력 받기
        Map<String, Object> orderData = system.getUserInput();
        
        // 주문 처리
        String result = system.processOrder(orderData);
        
        // 주문 목록 조회
        Integer page = (Integer) orderData.get("page");
        List<Map<String, Object>> orders = system.getOrderList(page, -10); 
        
        // 캐시 로드
        system.loadOrderCache();
        
        System.out.println("처리 결과: " + result);
    }
}