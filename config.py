import os

# إعدادات البوت - استخدام environment variables للأمان
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7920984703:AAHkRNpgzDxBzS61hAe7r7cO_fATlAB8oqM")
CHANNEL_ID = os.getenv('CHANNEL_ID', "@Kingelg0ld")
QX_SIGNUP_URL = "https://broker-qx.pro/sign-up/?lid=1376472"

# بيانات الدخول لـ QX Broker
QX_CREDENTIALS = {
    'email': os.getenv('QX_EMAIL', 'mohamedels928@gmail.com'),
    'password': os.getenv('QX_PASSWORD', 'Mrvip@219'),
    'login_url': 'https://qxbroker.com/ar/sign-in/'
}

# الأزواج المطلوبة
TRADING_PAIRS = [
    'USD/BRL', 'USD/EGP', 'USD/TRY', 'USD/ARS', 'USD/COP',
    'USD/DZD', 'USD/IDR', 'USD/BDT', 'USD/CAD', 'USD/NGN',
    'USD/PKR', 'USD/NR', 'USD/MXN', 'USD/PHP'
]

# إعدادات التداول
TRADE_SETTINGS = {
    'duration_seconds': 30,
    'trade_interval_minutes': 3,
    'session_start': '06:00',
    'session_end': '20:00'
}