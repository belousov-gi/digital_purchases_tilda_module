import random
import time
from app.api.schemas.order_info import JWTPurchaseData, InputPurchaseInfo
from app.core.config import settings
from app.exceptions.http_exc import (GenerationCodeFail, GettingPurchaseFromDBFail, IncorrectProductId,
                                     NeedToRequestNewVerificationCode, MaxCodeRequestindReached)
from app.repositories.db_repo import IDb
from app.services import auth_service
from app.services.db.models import Purchase, Code
from fastapi.encoders import jsonable_encoder


def get_currnet_time():
    return int(time.time())


async def save_purchases(purchases: list[Purchase], db: IDb) -> list[Purchase]:
    saved_purchases = await db.save_purchases(purchases)
    return saved_purchases


async def add_download_info(input_info_purchases: list[InputPurchaseInfo], requested_url: str,
                            db: IDb) -> list[Purchase]:
    """Func added downloaded info (URL for downloading and product name) to input purchase info.
    Returns list of objects with all info about purchase."""

    purchases = []

    for input_info_purchase in input_info_purchases:
        jwt_info = jsonable_encoder(input_info_purchase)
        token = await auth_service.create_jwt_token(jwt_info)
        product = await db.get_product(input_info_purchase.id_product)

        if product:
            #TODO: добавить реальную проверку наличия файла в данной директории
            url = settings.BASIC_DOWNLOAD_URL + requested_url + '/' + token

            purchase = Purchase(**jwt_info,
                                URL=url,
                                purchase_name=product.name,
                                file_format=product.file_format
                                )
            purchases.append(purchase)

        else:
            raise IncorrectProductId(
                f'Tried to generate download info for purchase: \'{jwt_info}\'. Product has not been found in database')

    return purchases


async def check_available_verification(purchase_info: JWTPurchaseData, db: IDb) -> bool:
    """Func of checking available verification for user before downloading the file from server.

    Returns False if:
     - purchase has been made later than (now - CODE_LIFETIME)
     - verification code has been expired already

    Returns True if code hasn't been expired yet.
    """

    current_time = get_currnet_time()
    last_purchase = await db.get_last_consumer_purchase(purchase_info.id_consumer)
    if not last_purchase:
        raise GettingPurchaseFromDBFail(f'Purchase info from jwt token: {purchase_info.model_dump_json}.')

    if current_time - last_purchase.timestamp < settings.VERIFICATION_LIFETIME:
        return True
    else:
        last_code = await db.get_last_consumer_code(purchase_info.id_consumer)
        if last_code:
            if last_code.is_succeeded == True and current_time - last_code.created_at < settings.VERIFICATION_LIFETIME:
               return True
        return False


async def generate_new_verification_code(id_consumer: int, db: IDb) -> Code:
    """Func of generation new verification code for consumer."""
    current_time = get_currnet_time()
    timestamp_from = current_time - settings.MAX_CODES_TIME_WINDOW
    code_quantity = await db.count_requested_codes_from_timestamp(start_timestamp=timestamp_from, id_consumer=id_consumer)
    if code_quantity >= settings.MAX_CODES_QUANTITY:
        raise MaxCodeRequestindReached('id_consumer: %s' % (id_consumer))

    random_code = random.sample("123456789", 4)
    random_code = int("".join(random_code))

    code = Code(id_consumer=id_consumer, value=random_code, created_at=current_time, entering_attempts=0, is_succeeded=False)
    if not code:
        raise GenerationCodeFail(f'Code has not been generated. id_consumer:{id_consumer}, created_at:{current_time}')
    return code


async def validate_verification_code(code: int, id_consumer: int, db: IDb) -> bool:
    """Func of validation verification code. It gets last verification code for user from database and compares with input value.
    Returns True if code is valid, otherwise returns False.
    ATTENTION: When code doesn't exist in database it also returns False"""

    verification_failed = False
    verification_succeeded = True

    last_code = await db.get_last_consumer_code(id_consumer)
    if not last_code:
        await db.add_code_entering_attempt(id_consumer)
        return verification_failed

    is_expired = True if last_code.created_at + settings.CODE_LIFETIME < get_currnet_time() else False
    is_reached_max_attempts = True if last_code.entering_attempts >= settings.ATTEMPTS_FOR_CODE else False

    if last_code.is_succeeded:
        raise NeedToRequestNewVerificationCode()

    if is_expired or is_reached_max_attempts:
        raise NeedToRequestNewVerificationCode()
    else:
        if last_code.value == code:
            await db.mark_code_as_succeded(last_code)
            return verification_succeeded
        else:
            await db.add_code_entering_attempt(id_consumer)
            return verification_failed


async def get_list_of_purchases(input_purchase_info, db: IDb) -> list[InputPurchaseInfo]:
    """Creates list of products from input purchase info"""

    consumer_email = input_purchase_info['Email']
    consumer = await db.get_consumer(consumer_email)

    if not consumer:
        consumer = await db.save_consumer(consumer_email)

    products = input_purchase_info['payment']['products']
    id_tilda_order = input_purchase_info['payment']['orderid']
    purchase_timestamp = get_currnet_time()
    all_purchases = []

    for product in products:
        id_product = int(product['sku'].split(':')[-1].strip())

        purchase = InputPurchaseInfo(
            id_consumer=consumer.id,
            id_product=id_product,
            id_tilda_order=id_tilda_order,
            timestamp=purchase_timestamp,
            consumer_email=consumer_email
        )

        all_purchases.append(purchase)

    return all_purchases
