from app.core.enums import M2MRoles
from fastapi import HTTPException
from abc import ABC
class CustomHTTPException(ABC, HTTPException):
    pass

class GenerationCodeFail(CustomHTTPException):
    def __init__(self, *args, status_code: int = 500):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'Generation of verification code failed. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)


class GettingPurchaseFromDBFail(CustomHTTPException):
    def __init__(self, *args, status_code: int = 500):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'Service tried to get last consumer\'s purchase from database, but nothing has been found. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)

class M2MTokenExists(CustomHTTPException):
    def __init__(self, *args, status_code: int = 422):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'M2M token for this service is already exists. If you want to generate the new one, text an administrator. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)

class NotAllowedRoleForToken(CustomHTTPException):
    def __init__(self, *args, status_code: int = 422):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = ('This type of m2m token is not allowed. For external services use role: \'{0}\'. Extra info: {1}'
                       .format( M2MRoles.external_service.name, self.message))
        super().__init__(status_code=status_code, detail=self.detail)



class IncorrectProductId(CustomHTTPException):
    def __init__(self, *args, status_code: int = 422):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'Such id_product does not exist in database. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)


class NeedToRequestNewVerificationCode(CustomHTTPException):
    def __init__(self, *args, status_code: int = 403):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'Request new verification code. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)

class FileCantBeFounded(CustomHTTPException):
    def __init__(self, *args, status_code: int = 500):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'File can\'t be founded on server. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)


class VerificationCodeDoesntExist(CustomHTTPException):
    def __init__(self, *args, status_code: int = 422):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = 'Verification code doesn\'t exist in data base. Extra info: {0}'.format(self.message)
        super().__init__(status_code=status_code, detail=self.detail)

class MaxCodeRequestindReached(CustomHTTPException):
    def __init__(self, *args, status_code: int = 403):
        if args:
            self.message = args[0]
        else:
            self.message = None

        self.detail = ('Quantity of requesting new codes has reached the maximum. Extra info: {0}'
                       .format(self.message))
        super().__init__(status_code=status_code, detail=self.detail)