import java.util.List;

public class Paginator {
    public static List<String> paginate(List<String> items, int page, int limit) {
        int start = page * limit;
        int end = Math.min(start + limit, items.size());
        return items.subList(start, end);
    }

    public static void main(String[] args) {
        List<String> data = List.of("a", "b", "c");
        System.out.println(paginate(data, 0, 2));
        System.out.println(paginate(data, -1, 2));
        System.out.println(paginate(data, 1, -3));
    }
}

// ❌ 문제점:
// - 음수 page 또는 limit에 대한 예외 처리 없음
// - 음수 인덱스가 subList에 전달되어 IndexOutOfBoundsException 발생 가능
// - limit가 음수면 end < start 상황 발생 가능
