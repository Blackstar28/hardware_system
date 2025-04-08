import requests
from django.core.mail import send_mail
from django.conf import settings
import requests

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

def notify_low_stock(product):
    if product.stock < product.low_stock_threshold:

        # Email
        send_mail(
            subject=f'Low Stock Alert: {product.name}',
            message=f'{product.name} only has {product.stock} items left in stock!',
            from_email='ajkleinf@gmai.com',
            recipient_list=['ajkleinf@gmail.com'],
            fail_silently=False,
        )

        # Telegram
        telegram_token = '7994933931:AAHRzdRiDUa-DroW8JCGFy-gOmWr2lJfRRw'
        chat_id = '398718055'
        message = f'⚠️ LOW STOCK: {product.name} - only {product.stock} left.'
        requests.get(f'https://api.telegram.org/bot{telegram_token}/sendMessage?chat_id={chat_id}&text={message}')


def notify_low_stock(product):
    print(f"🔍 Checking stock for {product.name} — Current: {product.stock}, Threshold: {product.low_stock_threshold}")

    
    if product.stock < product.low_stock_threshold:
        print("⚠️ Low stock detected. Sending notifications...")

        message = f"⚠️ LOW STOCK ALERT:\n{product.name} has only {product.stock} left in stock!"

        # ✅ Telegram
        try:
            telegram_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            response = requests.get(
                telegram_url,
                params={
                    "chat_id": settings.TELEGRAM_CHAT_ID,
                    "text": message
                }
            )
            response.raise_for_status()
            print("✅ Telegram message sent!")
        except Exception as e:
            print("🚫 Telegram error:", e)

        # ✅ Email
        try:
            send_mail(
                subject="Low Stock Alert",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.NOTIFICATION_EMAIL],
                fail_silently=False,
            )
            print("✅ Email sent!")
        except Exception as e:
            print("🚫 Email error:", e)