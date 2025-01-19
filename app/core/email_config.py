from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    MAIN_URL: str = os.getenv('MAIN_URL')
    SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL')
    SUPPORT_EMAIL_LINK: str = os.getenv('SUPPORT_EMAIL_LINK')
    SUPPORT_TELEGRAM_LINK: str = os.getenv('SUPPORT_TELEGRAM_LINK')

    HTML_BODY_PURCHASE: str = '''        
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Ваш заказ - %(main_url)s</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #ff6347;
            }
            a {
                color: #ff6347;
                text-decoration: none;
            }
            .footer {
                margin-top: 20px;
                font-size: 14px;
                color: #777;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⭐️ Спасибо за покупку! ⭐️</h1>
            <p>Дорогие родители,</p>
            <p>Спасибо, что выбрали наши развивающие игры. Мы рады, что можем быть частью детства Ваших детей и помочь им учиться через игру🧸</p>
            <h2>💡 Ваши покупки:</h2>
            <ul>
                %(purchases_html)s
            </ul>
            %(footer)s
        </div>
    </body>
    </html>
    '''

    HTML_BODY_CODE: str = '''        
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Код подтверждения от %(main_url)s</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f5f5f5;
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #ff6347;
            }
            a {
                color: #ff6347;
                text-decoration: none;
            }
            .footer {
                margin-top: 20px;
                font-size: 14px;
                color: #777;
            }
            .code {
                font-size: 28px;
                font-weight: bold;
                text-align: center;
                margin: 20px 0;
                color: #000;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔑 Ваш код подтверждения!</h1>
            <p>Для того, чтобы скачать файл, перейдите по ссылке и введите указаный ниже код:</p>
            <div class="code">
                %(code)s
            </div>
            <p>Ссылка для подтверждения и скачивания "%(purchase_name)s" - <a href=%(purchase_url)s>ссылка</a></p>
            %(footer)s
        </div>
    </body>
    </html>

    '''

    FOOTER = '''<div class="footer">
                <p>Если у вас возникнут вопросы, наши добрые феи поддержки всегда готовы помочь! ❤️️</p> 
                <p>Свяжитесь с нами через <a href=%s>%s</a> или через <a href=%s>телеграм</a>.</p>
                <p>С наилучшими пожеланиями,<a href=%s>tvoideti.ru</a></p>
            </div>''' % (SUPPORT_EMAIL_LINK, SUPPORT_EMAIL, SUPPORT_TELEGRAM_LINK, MAIN_URL)


settings = Settings()
