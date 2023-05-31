import os

with open(os.environ["TELEGRAM_TOKEN_FILE"], "r") as f:
    TOKEN = f.read()

DATABASE = os.environ["DB_DATABASE"]
USER = os.environ["DB_USER"]

with open(os.environ["DB_PASSWORD_FILE"], "r") as f:
    PASSWORD = f.read()

HOST = os.environ["DB_HOST"]
PORT = os.environ["DB_PORT"]


class CommandBot:
    START = 'start'
    HELP = 'help'
    LOGIN = 'login'


class Status:
    OK = 0
    FAILED = 1
