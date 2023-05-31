# ----------------------------------------------------------------------------------------------------------------------

# api для работы с PostgreSQL

# ----------------------------------------------------------------------------------------------------------------------

import psycopg2

from settings.config import DATABASE, USER, PASSWORD, HOST, PORT

connection = None

try:
    assert isinstance(DATABASE, object)
    connection = psycopg2.connect(
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )
except Exception as e:
    print('ERROR[open_db]: {}'.format(e))


def close_db():

    """
    Закрывает БД
    :return:
        Ничего не возвращает.
    """

    try:
        connection.close()
    except Exception as e:
        print('ERROR[close_db]: {}'.format(e))


def inquiry_to_db(inquiry, params=None, flag=False, one=True):

    """
    Принимает SQL-запрос и выполняет его
    :param params:
    :param inquiry:
        Этот параметр принимает в себя string SQL-запрос.
    :param flag:
        Указывает, надо ли выводить на экран отчет о запросе.
    :return:
        Ничего не возвращает.
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(inquiry, params)
            res = None

            if flag:
                if one:
                    res = cursor.fetchone()
                else:
                    res = cursor.fetchall()

            connection.commit()
            return res
    except Exception as e:
        connection.rollback()
        print('ERROR[inquiry_to_db]: {}'.format(e))
