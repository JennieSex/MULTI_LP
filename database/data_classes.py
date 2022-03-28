from typing import List


class _dataclass:
    attributes: List[str] = []

    def __init__(self, data: dict):
        self.__dict__.update(data)

    @classmethod
    def _find_annotated_vars(cls):
        for attr in cls.__annotations__:
            if not attr.startswith('_'):
                cls.attributes.append(attr)


class Settings(_dataclass):
    nickname: str
    prefix: str
    farm: dict
    catcher: int
    friends_add: bool
    dogs_del: bool
    ignore_list: List[str]
    del_requests: bool
    captcha: bool
    online: bool
    offline: bool
    templates_bind: int
    trusted_users: List[int]
    delete: dict
    mentions: dict
    leave_chats: bool
    autostatus_on: bool
    autostatus_format: str
    repeater: dict


class Account(_dataclass):
    added_by: int
    user_id: int
    vk_longpoll: bool


Settings._find_annotated_vars()
Account._find_annotated_vars()