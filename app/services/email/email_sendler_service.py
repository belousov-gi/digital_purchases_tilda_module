import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from socket import gaierror
from app.core.config import settings
from app.core import logger_config
import logging

logger = logging.getLogger(__name__)


async def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        smtp_server = settings.SMTP_SERVER
        port = settings.SSL_PORT

        message = MIMEMultipart()
        message["From"] = formataddr((settings.EMAIL_DISPLAY_NAME, sender_email))
        message["To"] = recipient_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(from_addr=sender_email,
                            to_addrs=[recipient_email],
                            msg=message.as_string())
        logger.info("Email sent successfully to %s. Mail body: %s. Sendler: %s", recipient_email, body, sender_email)
    except smtplib.SMTPAuthenticationError as e:
        logger.critical("Failed to authenticate with the SMTP server. Check your username and password. Extra info: %s", e)
    except smtplib.SMTPRecipientsRefused as e:
        logger.critical("Recipient email address was refused by the server: %s. %s", recipient_email, e)
    except smtplib.SMTPSenderRefused as e:
        logger.critical("Sender email address was refused by the server: %s. %s", sender_email, e)
    except smtplib.SMTPException as e:
        logger.critical("SMTP error occurred: %s.", e)
    except gaierror as e:
        logger.critical("Network error. Failed to connect to the SMTP server. %s", e)
    except Exception as e:
        logger.critical("An unexpected error occurred: %s", e)

