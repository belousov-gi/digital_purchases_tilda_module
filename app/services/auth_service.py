import jwt
from app.api.schemas.auth import M2MTokenInfo
from app.core.config import settings
from app.core.enums import M2MRoles
from app.exceptions.http_exc import NotAllowedRoleForToken
from fastapi import HTTPException, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/create_m2m_token')
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

async def create_jwt_token(data) -> str:
    """Func of creation JWT token. To send in input some objects is possible too."""
    if not isinstance(data, dict):
        data = jsonable_encoder(data)
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token


async def get_info_from_token(jwt_token: str = Depends(oauth2_scheme)):
    """Func of getting all user info from JWT token"""
    try:
        payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def create_m2m_token(m2m_token_info:M2MTokenInfo) -> str:
    """Func of creation m2m tokens for services."""
    if m2m_token_info.role in M2MRoles.__dict__:
        if m2m_token_info.role != settings.ADMIN_SERVICE_ROLE:
            token = await create_jwt_token(m2m_token_info)
            return token

    raise NotAllowedRoleForToken(f'Requested role: \'{m2m_token_info.role}\' for service \'{m2m_token_info.service_name}\'')
