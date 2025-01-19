from app.api.schemas.auth import M2MTokenInfo, M2MTokenResponse
from app.core.config import settings
from app.exceptions.http_exc import M2MTokenExists
from app.repositories.db_repo import IDb, PostgreRepo
from app.services import auth_service
from app.services.db.database import get_async_session
from app.services.db.models import M2MToken
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.core import logger_config


logger = logging.getLogger(__name__)

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"]
)

async def get_db_repository(session: AsyncSession = Depends(get_async_session)) -> IDb:
    return PostgreRepo(session)

# OAuth2PasswordBearer for authentication by token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/create_m2m_token')


@auth_router.post("/create_m2m_token", response_model=M2MTokenResponse)
async def create_m2m_token(new_m2m_info: M2MTokenInfo,
                           token_info = Depends(auth_service.get_info_from_token),
                           db:IDb = Depends(get_db_repository)):
    """Func for creation m2m tokens without expiration.
    Before a creation m2m token for service, the existence of this token will be checked in a database.
    If it exists already, new token won't be generated and you get an exception."""
    logger.debug(f'admin m2m token info: {token_info}')
    logger.debug(f'new m2m info: {new_m2m_info}')

    token = M2MTokenInfo(**token_info)

    logger.debug(f'Token m2m admin object : {token.__dict__}')

    if token.role == settings.ADMIN_SERVICE_ROLE:
        token = await db.get_m2m_token(new_m2m_info.service_name)

        if token:
            raise M2MTokenExists(f'Tried to generate for following service: {new_m2m_info.service_name}')

        token = await auth_service.create_m2m_token(new_m2m_info)
        logger.debug(f'new m2m tiken: {token}')
        m2m_info = M2MToken(service_name=new_m2m_info.service_name, role=new_m2m_info.role, m2m_token=token)
        return await db.save_m2m_token(m2m_info)
    else:
        raise HTTPException(status_code=401, detail='Invalid token')
