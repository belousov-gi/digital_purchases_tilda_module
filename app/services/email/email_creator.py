from app.services.db.models import Purchase
from app.core.email_config import settings

main_url = settings.MAIN_URL
support_email = settings.SUPPORT_EMAIL
support_email_link = settings.SUPPORT_EMAIL_LINK
support_telegram_link = settings.SUPPORT_TELEGRAM_LINK
footer = settings.FOOTER
def create_purchase_email_body( purchases: list[Purchase]) -> str:
    purchases_html = ''
    for purchase in purchases:
        purchases_html += f'<li><a href={purchase.URL}>{purchase.purchase_name}</a></li>'

    html_body = settings.HTML_BODY_PURCHASE % {'main_url': settings.MAIN_URL, 'purchases_html': purchases_html,
                                               'footer': footer}

    return html_body

def create_verification_code_downloading_body(code: str, purchase_name: str, purchase_url: str) -> str:
    html_body = settings.HTML_BODY_CODE % {'main_url': settings.MAIN_URL, 'code': code, 'purchase_name': purchase_name,
                                           'purchase_url': purchase_name, 'footer': footer}

    return html_body