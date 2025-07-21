def get_page_items(items, page, limit):
    start = page * limit
    end = start + limit
    return items[start:end]

data = ["a", "b", "c"]
print(get_page_items(data, 0, 2))
print(get_page_items(data, -1, 2))
print(get_page_items(data, 1, -3))

# ❌ 문제점:
# - 음수 page 또는 limit 값에 대한 검증이 없어 슬라이싱 시 예상치 못한 결과 발생 가능
# - limit가 음수일 경우 반환 결과가 빈 리스트가 아님
# - 경계값(예: page가 리스트 범위를 벗어나는 경우)에 대한 처리가 없음
