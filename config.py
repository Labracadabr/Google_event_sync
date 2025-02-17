from dataclasses import dataclass
from environs import Env


@dataclass
class Config:
    sheet_id: str = None
    calendar_id: str = None


# загрузить конфиг из переменных окружения
env = Env()
env.read_env()
config = Config(
    sheet_id=env('sheet_id'),
    calendar_id=env('calendar_id'),
)

