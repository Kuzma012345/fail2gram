import yaml
from yaml.loader import SafeLoader


def get_msg_by_key(key: str):
    with open('./settings/bot_messages.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)

        return data[key]


class MessageBot:
    START_MSG = get_msg_by_key('StartMessage')
    SUCCESSFUL = get_msg_by_key('SuccessfulMessage')
    UNSUCCESSFUL = get_msg_by_key('UnsuccessfulMessage')
    ERROR_LOGIN_FLAGS = get_msg_by_key('LoginErrorFlagsMessage')
    BASE_ERROR = get_msg_by_key('BaseError')
    DEFAULT = get_msg_by_key('DefaultMessage')
    STAGE_LOGIN_KEY = get_msg_by_key('StageLoginKey')
    STAGE_NAME = get_msg_by_key('StageName')


class TitleButton:
    LOGOUT_ACCOUNT = get_msg_by_key('LogoutAccount')
    LIST_EVENTS = get_msg_by_key('ListEvents')
    LIST_REMOTE_CONNECTIONS = get_msg_by_key('ListRemoteConnections')
    LIST_BANS = get_msg_by_key('ListBans')
