# developer: th2empty
# date 15.03.2022

import json
import os
import traceback

import mysql.connector as mysql

from vk.user_bot import dlp, ND


class _DBConnData:
    def __init__(self, host: str, username: str, password: str, database: str):
        self.host = host
        self.username = username
        self.password = password
        self.database = database


def _get_db_conn_data():
    current_dir = os.getcwd()
    with open('{0}/vk/user_bot/configs/mysql_conn.json'.format(current_dir), 'r') as cfg:
        data = json.load(cfg)

        return _DBConnData(data.get("host"),
                           data.get("username"),
                           data.get("password"),
                           data.get("database"),
                           )


@dlp.register('запреты', receive=True)
def get_list(nd: ND):
    try:
        conn_data = _get_db_conn_data()
        db = mysql.connect(
            host=conn_data.host,
            user=conn_data.username,
            passwd=conn_data.password,
            database=conn_data.database,
            auth_plugin='mysql_native_password',
            # charset = "utf8mb4_unicode_ci"
        )

        cursor = db.cursor()
        cursor.execute("SELECT words FROM forbidden_words WHERE uid={0}".format(nd.db.user_id))

        words = cursor.fetchall()

        if len(words) > 0 and words[0][0] != "":
            words = words[0][0]
            words_list = words.split(";")
            response = "⛔ Запрещенные слова:\n"
            forbidden_words = ""
            for i in range(len(words_list)):
                if words_list[i] == " " or words_list[i] == "":
                    continue
                if i + 1 >= len(words_list):
                    forbidden_words += "{0}".format(words_list[i])
                else:
                    forbidden_words += "{0}, ".format(words_list[i])

            if forbidden_words == "" or forbidden_words == " ":
                nd.msg_op(2, "🕯 Ничто не запрещено, значит всё дозволено")
                return

            nd.msg_op(2, response + forbidden_words)
            return
        else:
            nd.msg_op(2, "🕯 Ничто не запрещено, значит всё дозволено")
            return
    except Exception as ex:
        print("ERROR:: {0}".format(traceback.format_exc()))
        nd.msg_op(2, "❗Не удалось выполнить запрос в базу данных, произошла ошибка.\n\n{0}".format(ex))


@dlp.register('+запрет', receive=True)
def add_word(nd: ND):
    settings = nd.db.settings_get()

    try:
        conn_data = _get_db_conn_data()
        db = mysql.connect(
            host=conn_data.host,
            user=conn_data.username,
            passwd=conn_data.password,
            database=conn_data.database,
            auth_plugin='mysql_native_password'
        )

        cursor = db.cursor()
        cursor.execute("SELECT words FROM forbidden_words WHERE uid={0}".format(nd.db.user_id))

        message = nd.msg.get("text")
        words = cursor.fetchall()
        message = message.replace("{0}".format(settings.prefix), "")
        word = message.replace("+запрет ", "")

        if len(words) > 0:
            words_list = words[0][0].split(";")
            if not word in words_list:
                words = words[0][0] + ";{0}".format(word)
            else:
                nd.msg_op(2, "🤡 '{0}' уже запрещено".format(word))
                return
        else:
            words = word

        cursor.execute("update forbidden_words set words='{0}' where uid={1}".format(words, nd.db.user_id))
        db.commit()

        nd.msg_op(2, "✅ '{0}' теперь запрещено!".format(word))
    except Exception as ex:
        print("ERROR:: {0}".format(traceback.format_exc()))
        nd.msg_op(2, "❗Не удалось выполнить запрос в базу данных, произошла ошибка.\n\n{0}".format(ex))


@dlp.register('-запрет', receive=True)
def del_word(nd: ND):
    settings = nd.db.settings_get()

    try:
        conn_data = _get_db_conn_data()
        db = mysql.connect(
            host=conn_data.host,
            user=conn_data.username,
            passwd=conn_data.password,
            database=conn_data.database,
            auth_plugin='mysql_native_password'
        )

        cursor = db.cursor()
        cursor.execute("SELECT words FROM forbidden_words WHERE uid={0}".format(nd.db.user_id))

        message = nd.msg.get("text")
        words = cursor.fetchall()
        message = message.replace("{0}".format(settings.prefix), "")
        word = message.replace("-запрет ", "")
        words = words[0][0]
        words_list = words.split(";")

        print("START WORDS", words)

        if len(words) > 0 and words[0][0] != " ":
            if word not in words_list:
                nd.msg_op(2, "❗Слово '{0}' и так не запрещено".format(word))
                return

            words = words.replace(";", " ")
            words = words.replace("{0}".format(word), "")
            words.lstrip()
            words = words.replace(" ", ";")
            print("FINAL WORDS", words)
        else:
            nd.msg_op(2, "❗Ошибка... Список запретов пуст.")
            return

        cursor.execute("update forbidden_words set words='{0}' where uid={1}".format(words, nd.db.user_id))
        db.commit()
        nd.msg_op(2, "✅ Слово '{0}' теперь разрешено!".format(word))
    except Exception as ex:
        print("ERROR:: {0}".format(traceback.format_exc()))
        nd.msg_op(2, "❗Не удалось выполнить запрос в базу данных, произошла неизвестная ошибка")
