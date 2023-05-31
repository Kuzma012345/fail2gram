# https://t.me/DKKKKKKKKKKK_bot

import telebot

from settings.config import CommandBot, TOKEN
from tools.config_reader import MessageBot, TitleButton
from tools.database_worker import *
from tools.exceptions import *
from tools.event_handlers.event_login_handler import *
from telebot import types

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=[CommandBot.START, CommandBot.HELP])
def send_welcome(message):
    save_telegram_id_if_not_exist(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton(TitleButton.LOGOUT_ACCOUNT)
    item2 = types.KeyboardButton(TitleButton.LIST_EVENTS)
    item3 = types.KeyboardButton(TitleButton.LIST_REMOTE_CONNECTIONS)
    item4 = types.KeyboardButton(TitleButton.LIST_BANS)

    markup.add(item1, item2, item3, item4)

    bot.send_message(message.chat.id, MessageBot.START_MSG, reply_markup=markup)


@bot.message_handler(commands=[CommandBot.LOGIN])
def log_in(message):
    save_telegram_id_if_not_exist(message.chat.id)

    if not check_login(message.chat.id):
        if not STATE_CHAT_ID.get(message.chat.id):
            STATE_CHAT_ID[message.chat.id] = StateLogin.KEY
            bot.reply_to(message, MessageBot.STAGE_LOGIN_KEY)
    else:
        bot.reply_to(message, MessageBot.BASE_ERROR)


@bot.message_handler(func=lambda message: True)
def scanner_all_msg(message):
    if STATE_CHAT_ID.get(message.chat.id) == StateLogin.KEY:
        login_handler(message)
        bot.reply_to(message, MessageBot.STAGE_NAME)
        return
    elif STATE_CHAT_ID.get(message.chat.id) == StateLogin.NAME:
        res = login_handler(message)

        if res == Status.FAILED:
            bot.reply_to(message, MessageBot.UNSUCCESSFUL)
            exit_from_bot(message)
            return

        bot.reply_to(message, MessageBot.SUCCESSFUL)
        return

    res = buttons_handler(message)

    if res == Status.FAILED:
        bot.reply_to(message, MessageBot.DEFAULT)
    elif not res:
        bot.reply_to(message, MessageBot.BASE_ERROR)
    else:
        bot.reply_to(message, res)


def buttons_handler(message) -> Status:
    actions = {
        TitleButton.LOGOUT_ACCOUNT: exit_from_bot,
        TitleButton.LIST_EVENTS: get_list_events,
        TitleButton.LIST_REMOTE_CONNECTIONS: get_list_remote_connections,
        TitleButton.LIST_BANS: get_list_bans,
    }

    action = actions.get(message.text)

    if action:
        res = action(message)

        if res is None:
            return Status.FAILED
        else:
            return res
    else:
        return Status.FAILED


def save_telegram_id_if_not_exist(telegram_id: int):
    if not check_exist_telegram_id(telegram_id):
        res = save_telegram_id(telegram_id)

        if res == Status.FAILED:
            raise FailedSaveTelegramIdException


bot.infinity_polling()
