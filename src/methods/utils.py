import urllib.parse


def parse_callback_data(data: str) -> dict:
    # Удаляем префикс и парсим параметры
    query_string = data.split(':', 1)[1]
    return dict(urllib.parse.parse_qsl(query_string))