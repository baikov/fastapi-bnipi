import os

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

# Настройки для Redis
redis_settings = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "db": 0,
}
