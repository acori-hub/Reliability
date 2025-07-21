import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class WeatherFetcher {
    public static void main(String[] args) throws Exception {
        URL url = new URL("https://api.weather.example.com/current");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        Scanner scanner = new Scanner(conn.getInputStream());
        while (scanner.hasNext()) {
            System.out.println(scanner.nextLine());
        }
        scanner.close();
    }
}

// ❌ 문제점:
// - API 호출 실패 시 IOException 발생 가능하지만 처리하지 않음
// - 응답 코드가 200이 아닐 경우에도 입력 스트림을 읽어 오류 발생 가능
// - 사용자에게 실패 안내 없이 프로그램이 종료될 수 있음
