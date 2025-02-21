import pickle

from gcsa.google_calendar import GoogleCalendar
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from config import config


# первичное создание token.pickle
def init_token_save():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/calendar'],
        redirect_uri="http://localhost:8080/"
    )
    creds = flow.run_local_server(port=8080)

    # Save credentials manually
    with open('token.pickle', 'wb') as token_file:
        pickle.dump(creds, token_file)

    print("✅ Token with refresh_token saved!")


# объект GoogleCalendar - при вызове проверить актуальность токена и обновить, если expired
def get_google_calendar() -> GoogleCalendar:
    # Load credentials
    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.pickle", "wb") as token_file:
            pickle.dump(creds, token_file)

    return GoogleCalendar(default_calendar=config.calendar_id, credentials=creds)
