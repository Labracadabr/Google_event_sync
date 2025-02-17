from datetime import date, datetime
import json

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from sheet_ import read_sheet, source_spreadsheet
from config import config


app = FastAPI()
calendar = GoogleCalendar(default_calendar=config.calendar_id, credentials_path="credentials.json")


@app.post("/sync_calendar")
def sync_calendar() -> JSONResponse:
    try:
        # прочитать таблицу
        data = read_sheet(spreadsheet=source_spreadsheet, page='СВЕЖИЕ РЕЛИЗЫ')
        print(f'{len(data) = }')

        added: list[str] = []
        bad_date: list[str] = []

        for row in data:
            # искомые поля
            event_date_str, nickname, release = row.get('Дата релиза'), row.get('Никнеймы'), row.get('Название релиза')

            # пропустить строки без данных
            if not (event_date_str and nickname and release):
                continue

            # преобразовать
            try:
                event_date = datetime.strptime(event_date_str, '%d.%m.%Y').date()
            except Exception as e:
                print(f'date error: {event_date_str = }, {e = }')
                bad_date.append(event_date_str)
                continue
            event_description = f'{nickname} - {release}'

            # внести в календарь
            event = Event(event_description, start=event_date, location='auto')
            calendar.add_event(event)
            added.append(str(event_date), )
            print(f'added: {event_description}, {event_date = }')

        # отчет о работе
        if added:
            added_str = "\n".join([f"{i}. {d}"for i, d in enumerate(sorted(list(set(added))), start=1)])
            message = 'События добавлены в даты:\n' + added_str
        else:
            message = 'Новых событий не найдено'

        if bad_date:
            bad_str = "\n".join([f"{i}. {repr(d)}"for i, d in enumerate(bad_date, start=1)])
            message += '\n\nНе распознана дата:\n' + bad_str

        return JSONResponse({"status": "success", "message": message})

    except Exception as e:
        print(e)
        return JSONResponse({"status": "error", "message": str(e)})


if __name__ == "__main__":
    res = json.loads(sync_calendar().body.decode("utf-8"))
    print(res['message'])
