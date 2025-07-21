import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;
import java.io.IOException;

public class WeatherFetcher {
    public static void main(String[] args) {
        try {
            URL url = new URL("https://api.weather.example.com/current");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");

            int status = conn.getResponseCode();
            if (status != 200) {
                System.err.println("API returned error code: " + status);
                return;
            }

            Scanner scanner = new Scanner(conn.getInputStream());
            while (scanner.hasNext()) {
                System.out.println(scanner.nextLine());
            }
            scanner.close();
        } catch (IOException e) {
            System.err.println("Failed to fetch weather data: " + e.getMessage());
        }
    }
}

// ✅ 문제 없음:
// - HTTP 상태 코드 확인으로 비정상 응답에 대응 가능
// - IOException 예외를 명시적으로 처리해 앱 비정상 종료 방지
// - 사용자에게 오류 메시지를 출력하여 문제 원인 파악 가능
