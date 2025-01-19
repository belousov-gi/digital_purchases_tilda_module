import os
from fastapi import FastAPI, Request, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.api.endpoints.auth import auth_router
from app.api.schemas.auth import M2MTokenInfo
from app.api.schemas.order_info import VerificationInfo, PurchaseResponse, JWTPurchaseData
from app.core.config import settings
from app.exceptions.http_exc import NeedToRequestNewVerificationCode, FileCantBeFounded, CustomHTTPException
from app.repositories.db_repo import PostgreRepo, IDb
from app.services import auth_service, order_service
from app.services.email import email_sendler_service, email_creator
from app.services.db.database import get_async_session
from app.services.db.models import Purchase
from app.core import logger_config
import logging

#Create logger
logger = logging.getLogger(__name__)





app = FastAPI(docs_url="/docs",
              redoc_url="/redoc",
              openapi_url="/openapi.json")
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)


@app.exception_handler(CustomHTTPException)
async def custom_exception_handler(request: Request, exc: CustomHTTPException):


    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )
async def get_db_repository(session: AsyncSession = Depends(get_async_session)) -> IDb:
    return PostgreRepo(session)


@app.get("/api/v1/purchase/{jwt_token}")
async def get_purchase(jwt_token: str, m2m_token_info: M2MTokenInfo = Depends(auth_service.get_info_from_token),
                       db: IDb = Depends(get_db_repository)):

    token_info = await auth_service.get_info_from_token(jwt_token)

    purchase_info = Purchase(**token_info)
    is_verification_passed = await order_service.check_available_verification(JWTPurchaseData(**token_info), db=db)


    if not is_verification_passed:
        raise NeedToRequestNewVerificationCode()

    file_name = str(purchase_info.id_product) + '.pdf'
    file_path = os.path.join(settings.PATH_TO_FILES, file_name)

    if os.path.exists(file_path):
        return FileResponse(file_path, media_type='application/octet-stream', filename=file_name)
    else:
        return FileCantBeFounded(f'Purchase info: {jsonable_encoder(purchase_info)}')


@app.post("/api/v1/purchase", response_model=list[PurchaseResponse])
async def save_purchase(request: Request,
                        m2m_token_info: M2MTokenInfo = Depends(auth_service.get_info_from_token),
                        db: IDb = Depends(get_db_repository)):
    input_purchase_info = await request.json()
    input_purchases = await order_service.get_list_of_purchases(input_purchase_info, db=db)

    purchases = await order_service.add_download_info(input_info_purchases=input_purchases, requested_url=request.url.path, db=db)
    saved_purchases = await order_service.save_purchases(purchases=purchases, db=db)

    await email_sendler_service.send_email(sender_email=settings.PURCHASE_SMTP_SENDER,
                                           sender_password=settings.PURCHASE_SMTP_SENDER_PSW,
                                           recipient_email=saved_purchases[0].consumer_email,
                                           subject=settings.PURCHASE_SUBJECT_MAIL,
                                           body=email_creator.create_purchase_email_body(saved_purchases)
                                           )

    return saved_purchases


@app.post("/api/v1/check_verification_code", response_model=bool)
async def check_verification_code(verification_info: VerificationInfo,
                                  m2m_token_info: M2MTokenInfo = Depends(auth_service.get_info_from_token),
                                  db: IDb = Depends(get_db_repository)) -> bool:
    purchase_info = await auth_service.get_info_from_token(verification_info.consumer_token)
    purchase_info = Purchase(**purchase_info)
    is_code_valid = order_service.validate_verification_code(code=verification_info.code_value,
                                                             id_consumer=purchase_info.id_consumer,
                                                             db=db)
    return await is_code_valid


@app.get('/api/v1/send_new_verification_code/{jwt_token}')
async def send_new_verification_code(jwt_token: str,
                                    m2m_token_info: M2MTokenInfo = Depends(auth_service.get_info_from_token),
                                    db: IDb = Depends(get_db_repository)):
    purchase_info = await auth_service.get_info_from_token(jwt_token)
    purchase_info = Purchase(**purchase_info)
    code = await order_service.generate_new_verification_code(id_consumer=purchase_info.id_consumer, db=db)
    code = await db.save_new_verification_code(code)

    await email_sendler_service.send_email(sender_email=settings.NO_REPLY_SMTP_SENDER,
                                           sender_password=settings.NO_REPLY_SMTP_SENDER_PSW,
                                           recipient_email=purchase_info.consumer_email,
                                           subject='Код подтверждения',
                                           body=email_creator.create_verification_code_downloading_body(code=code.value,
                                                                                                        purchase_name=purchase_info.purchase_name,
                                                                                                        purchase_url=purchase_info.URL)
                                           )

    response = 'Проверочный код был отправлен на почту, которая была указана при покупке.'
    return response
