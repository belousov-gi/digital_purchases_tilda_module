from app.core.enums import M2MRoles
from pydantic_settings import BaseSettings
import os

# from dotenv import load_dotenv
# load_dotenv()

class Settings(BaseSettings):

    #------------DB---------------------------
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")

    # ------------JWT-------------------------
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")

    # ------------PURCHASE AUTH---------------
    # Verification code lifetime in seconds
    CODE_LIFETIME: int = os.getenv("CODE_LIFETIME")
    # Quantity of attempts to enter the code
    ATTEMPTS_FOR_CODE: int = os.getenv("ATTEMPTS_FOR_CODE")
    # Time window in seconds in which system counts requested codes and compares with MAX_CODES_QUANTITY
    MAX_CODES_TIME_WINDOW: int = os.getenv("MAX_CODES_TIME_WINDOW")
    # Max codes for requesting
    MAX_CODES_QUANTITY: int = os.getenv("MAX_CODES_QUANTITY")
    # Time in seconds during which new verification is not needed
    VERIFICATION_LIFETIME: int = os.getenv("VERIFICATION_LIFETIME")

    # ------------MEDIA STORAGE---------------
    BASIC_DOWNLOAD_URL: str = os.getenv("BASIC_DOWNLOAD_URL")
    PATH_TO_FILES: str = os.getenv("PATH_TO_FILES")

    # ------------SMTP MAIL ------------------
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SSL_PORT: int = os.getenv("SSL_PORT")
    EMAIL_DISPLAY_NAME: str = os.getenv("EMAIL_DISPLAY_NAME")
    PURCHASE_SMTP_SENDER: str = os.getenv("PURCHASE_SMTP_SENDER")
    PURCHASE_SMTP_SENDER_PSW: str = os.getenv("PURCHASE_SMTP_SENDER_PSW")
    PURCHASE_SUBJECT_MAIL: str = os.getenv("PURCHASE_SUBJECT_MAIL")
    NO_REPLY_SMTP_SENDER: str = os.getenv("NO_REPLY_SMTP_SENDER")
    NO_REPLY_SMTP_SENDER_PSW: str = os.getenv("NO_REPLY_SMTP_SENDER_PSW")

    @property
    def ASYNC_DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def SYNC_DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    # Name of admin service's role which is stored in admin m2m jwt token. Via this token you get access for special functions. E.X: generation m2m tokens
    def ADMIN_SERVICE_ROLE(self):
        return M2MRoles.root_service.name


settings = Settings()