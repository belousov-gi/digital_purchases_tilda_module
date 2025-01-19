from pydantic import BaseModel


class DownloadPurchaseInfo(BaseModel):
    purchase_name: str
    URL: str


class JWTPurchaseData(BaseModel):
    id_consumer: int
    id_product: int
    timestamp: int


class GeneratedVerificationCode(BaseModel):
    id_consumer: int
    id_product: int
    purchase_timestamp: int


class VerificationInfo(BaseModel):
    code_value: int
    consumer_token: str


class InputPurchaseInfo(BaseModel):
    id_consumer: int
    id_product: int
    id_tilda_order: str
    consumer_email: str
    timestamp: int


#-------------------------------------------------Responses-------------------------------------------------------
class CodeResponse(BaseModel):
    id_consumer: int
    value: int
    created_at: int


class PurchaseResponse(BaseModel):
    id: int
    id_consumer: int
    id_product: int
    id_tilda_order: str
    timestamp: int
    file_format: str
    purchase_name: str
    URL: str
    consumer_email: str
