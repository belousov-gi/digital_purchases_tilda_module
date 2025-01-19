from pydantic import BaseModel


class JWTToken(BaseModel):
    jwt_token: str


class M2MTokenInfo(BaseModel):
    service_name: str
    role: str


#-------------------------------------------------Responses-------------------------------------------------------
class M2MTokenResponse(BaseModel):
    id: int
    service_name: str
    m2m_token: str
    role: str
