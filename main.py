from datetime import date, datetime
import json
from pathlib import Path

from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from sheet_ import read_sheet, source_spreadsheet
from calendar_ import get_google_calendar


app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

class Request(BaseModel):
    email: str

@app.get("/")
def root():
    return FileResponse("flakes.html")

@app.get("/static/favicon.ico")
def root():
    return FileResponse("/static/favicon.ico")


@app.post("/sync_calendar")
def sync_calendar(request: Request) -> JSONResponse:
    try:
        calendar = get_google_calendar()

        # прочитать таблицу
        data = read_sheet(spreadsheet=source_spreadsheet, page='СВЕЖИЕ РЕЛИЗЫ')
        print(f'{len(data) = }')

        # прочитать существующие события в календаре
        existing: set[tuple] = set()
        for event in calendar.get_events(time_min=date(2025, 1, 1)):
            existing.add(tuple([event.start, event.summary]))

        added: list[str] = []
        bad_date: list[str] = []

        for row in data:
            # искомые поля
            date_str, nickname, release = row.get('Дата релиза'), row.get('Никнеймы'), row.get('Название релиза')

            # пропустить строки без данных
            if not (date_str and nickname and release):
                continue

            # преобразовать
            try:
                event_date = datetime.strptime(date_str.strip(), '%d.%m.%Y').date()
            except Exception as e:
                print(f'date error: {date_str = }, {e = }')
                bad_date.append(date_str)
                continue
            event_description = f'{nickname} - {release}'

            # проверить, нет ли уже в календаре этого события
            if tuple([event_date, event_description]) in existing:
                continue
            existing.add(tuple([event_date, event_description]))

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
        status = 'success'

    except Exception as e:
        print(e)
        status = "error"
        message = str(e)

    # logs
    log = f"{datetime.now()}\t{request.email}\t{message}"
    with open("event_log.tsv", "a") as f:
        print(log, file=f)

    return JSONResponse({"status": status, "message": message})



if __name__ == "__main__":
    res = json.loads(sync_calendar().body.decode("utf-8"))
    print(res['message'])
