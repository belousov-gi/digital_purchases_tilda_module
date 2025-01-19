from enum import Enum


class M2MRoles(Enum):
    root_service = 1
    external_service = 2

class NoReplyMailSubjects:
    verfification_code = 'Код для скачивания файла'