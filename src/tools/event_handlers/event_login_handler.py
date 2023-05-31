from settings.config import Status
from tools.database_worker import *
from tools.validate import *

STATE_CHAT_ID = {}


def login_handler(message) -> Status:
    if STATE_CHAT_ID.get(message.chat.id) == StateLogin.KEY:
        res = Login.stage_name_handler(message)
        STATE_CHAT_ID[message.chat.id] = StateLogin.NAME
        return res
    elif STATE_CHAT_ID.get(message.chat.id) == StateLogin.NAME:
        res = Login.stage_password_handler(message)
        STATE_CHAT_ID.pop(message.chat.id)
        return res
    else:
        return Status.FAILED


class Login:
    @staticmethod
    def stage_password_handler(message) -> Status:
        user_id, digest = get_user_id_and_digest(message.chat.id)

        password = message.text
        telegram_id = message.chat.id

        if not validate(digest, password):
            return Status.FAILED
        else:
            set_login_successful(telegram_id)
            return Status.OK

    @staticmethod
    def stage_name_handler(message) -> Status:
        res = get_id_by_name(message.text)

        if res is not None:
            set_pending_login_user_id(message.chat.id, res)

            return Status.OK
        else:
            return Status.FAILED


class StateLogin:
    KEY = 0
    NAME = 1
