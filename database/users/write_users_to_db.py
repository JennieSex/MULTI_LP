# Developer: th2empty
# Date: 16.03.2022

import mysql.connector as mysql
import json
import os
import traceback

class _DBConnData:
    def __init__(self, host: str, username: str, password: str, database: str):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.auth_plugin = "mysql_native_password"


def _get_db_conn_data():
    current_dir = os.getcwd()
    with open('{0}/configs/mysql_conn.json'.format(current_dir), 'r') as cfg:
        data = json.load(cfg)
        
        return _DBConnData(data.get("host"), 
            data.get("username"), 
            data.get("password"), 
            data.get("database")
        ) 


def create_entries():
    try:
        print("\033[36m {}".format("⌛ Getting connection data..."))
        conn_data = _get_db_conn_data()
        print("\033[32m {}".format("⌛ Data received. Connecting to MySQL..."))
        db = mysql.connect(
            host = conn_data.host,
            user = conn_data.username,
            passwd = conn_data.password,
            database = conn_data.database,
            auth_plugin = conn_data.auth_plugin
        )
        print("\033[32m {}".format("✓ Connected to MySQL successfully"))
    except OSError as ex:
        print("\033[31m ☓ {0}".format(ex))
        return
    except mysql.Error as ex:
        print("\033[31m ☓ [ERROR]: Connection to MySQL failed: {0}".format(ex))
        return

    print("\033[36m ⌛ Getting a list of users...")

    users_list = os.listdir(os.getcwd())
    current_script = __file__.split("/")[len(__file__.split("/")) - 1]
    users_ids = ""
    users_count = 0
        
    print("\033[32m ✓ List of users received. Users to be written to the database:")
    for user in users_list:
        if user == "configs" or user == current_script:
            continue

        users_count += 1
        users_ids += "| {0}. @id{1} |".format(users_count, user)

    print("\033[33m {}".format(users_ids))
    print("\033[36m ⌛ Writing users to the database started...")
    for user in users_list:
        if user == "configs" or user == current_script:
            continue

        try:
            cursor = db.cursor()
            cursor.execute("INSERT INTO forbidden_words(uid, words) VALUES({0}, '')".format(user))
            print("\033[32m ✓ User @id{0} successfully added to database".format(user))
        except mysql.Error as ex:
            print("\033[31m ☓ [ERROR]: Failed to add user into db: {0}".format(ex))

    db.commit()


print("\033[36m {}".format("⌛ Preparing..."))
create_entries()
print("\033[32m \n✓ All Operation completed successfully")