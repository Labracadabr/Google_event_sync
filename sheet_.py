from pprint import pprint

import gspread
from gspread.spreadsheet import Spreadsheet
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import config

# данные для подключения к таблицам
gc = gspread.service_account(filename='token.json')
source_spreadsheet = gc.open_by_key(config.sheet_id)


@retry(stop=stop_after_attempt(5), wait=wait_exponential(), retry=retry_if_exception_type(gspread.exceptions.APIError))
def read_sheet(spreadsheet: Spreadsheet, page: str, head_idx=0) -> list[dict]:
    # получить лист таблицы по его id
    if isinstance(page, int) or page.isnumeric():
        sheet = spreadsheet.get_worksheet_by_id(page)
    # или по названию
    else:
        sheet = spreadsheet.worksheet(page)

    rows = sheet.get_all_values()
    head = rows[head_idx]  # имена колонок
    rows = rows[head_idx+1:]  # тело таблицы

    # сделать словарь из каждого ряда
    output = []
    for row in rows:
        output.append({column: row[i] for i, column in enumerate(head)})

    return output


if __name__ == '__main__':
    d = read_sheet(source_spreadsheet, page='СВЕЖИЕ РЕЛИЗЫ')
    pprint(d)
    pass
