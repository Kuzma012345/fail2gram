# ----------------------------------------------------------------------------------------------------------------------

# Кастомные исключения для приложения

# ----------------------------------------------------------------------------------------------------------------------
class Messages:
    FSTI_DEFAULT_MSG = 'Не удалось сохранить id юзера!'
    FSKTD_DEFAULT_MSG = 'Не удалось сохранить ключ юзера!'
    FSNTD_DEFAULT_MSG = 'Не удалось сохранить имя юзера!'


def _generate_error_message(obj_except):
    if obj_except.message:
        return f'{obj_except.__class__.__name__}: {obj_except.message}'
    else:
        return f'{obj_except.__class__.__name__}: {obj_except.default}'


class DefaultException(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        return _generate_error_message(self)


class FailedSaveTelegramIdException(DefaultException):
    def __init__(self, *args):
        super().__init__(*args)
        self.default = Messages.FSTI_DEFAULT_MSG


class FailedSaveKeyToDB(DefaultException):
    def __init__(self, *args):
        super().__init__(*args)
        self.default = Messages.FSKTD_DEFAULT_MSG


class FailedSaveNameToDB(DefaultException):
    def __init__(self, *args):
        super().__init__(*args)
        self.default = Messages.FSNTD_DEFAULT_MSG


__all__ = (
    FailedSaveTelegramIdException.__name__,
    FailedSaveKeyToDB.__name__,
    FailedSaveNameToDB.__name__,
)
