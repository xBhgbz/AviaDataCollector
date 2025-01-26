import json

from loguru import logger
from requests import Response


def _merge_data(avia_data: str, contract_data: str) -> dict:
    """Возвращает склееный ответ из промптов"""
    avia_data = _extract_json_string(avia_data)
    contract_data = None or _extract_json_string(contract_data)
    logger.info("Avia data %s" % avia_data)
    logger.info("Contract data %s" % contract_data)

    return {
        "avia_data": json.loads(avia_data) if avia_data else [],
        "contract_data": json.loads(contract_data) if contract_data else {}
    }


def _extract_json_string(string: str) -> str | None:
    """Достает из строки валидный json"""

    object_start = string.find("{")
    array_start = string.find("[")

    if object_start == -1 and array_start == -1:
        return

    if object_start != -1:
        start_index = object_start
        start_symbol, end_symbol = "{", "}"

        if array_start != -1 and array_start < object_start:
            start_index = array_start
            start_symbol, end_symbol = "[", "]"
    else:
        start_index = array_start
        start_symbol, end_symbol = "[", "]"

    # Считаем количество открывающих и закрывающих скобок
    count = 0
    for i in range(start_index, len(string)):
        if string[i] == start_symbol:
            count += 1
        elif string[i] == end_symbol:
            count -= 1
        # Если количество скобок вернулось к нулю, значит, мы нашли конец JSON-объекта
        if count == 0:
            return string[start_index:i + 1]
    return


def _parse_ai_response(response: Response) -> str:
    """Парсит ответ от нейронки"""
    full_message = ""
    for line in response.iter_lines():
        # Пропускаем пустые строки
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data: "):
                try:
                    # Убираем "data: "
                    data = json.loads(decoded_line[6:])
                    message = data.get("message", "")
                    full_message += message
                except json.JSONDecodeError:
                    pass

    return full_message
