import os, json
from typing import List

root_path = os.path.join(os.path.dirname(__file__), "users")

def read(user_id, filename):
    with open(os.path.join(root_path, f"{user_id}/{filename}.json"), "r", encoding="utf-8") as file:
        	return json.loads(file.read())

def write(user_id, filename, data):
    path = os.path.join(root_path, f"{user_id}/{filename}.json")
    try:
        with open(path, "r", encoding="utf-8") as file:
            backup_data = file.read()
    except:
        backup_data = ""
    with open(path, "w", encoding="utf-8") as file:
        try:
            file.write(
            	json.dumps(data, ensure_ascii=False, indent=4)
            )
        except Exception as e:
            file.write(backup_data)
            raise e


def start() -> List[int]:
    users = []
    for dir in os.listdir(root_path):
        if not dir.isdigit():
            continue
        users.append(int(dir))
    return users


for i, uid in enumerate(start()):
    num = 0 if i < 180 else 1
    data = read(uid, "user")
    data['catcher'] = num
    write(uid, "user", data)