import requests
from django.core.mail import send_mail
from django.conf import settings


def send_telegram_message(message):
    """Send a Telegram message using your bot token and chat ID."""
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print("Telegram error:", e)


def send_low_stock_email(subject, message, recipients):
    """Send a low stock alert email."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            fail_silently=False,
        )
    except Exception as e:
        print("Email error:", e)
