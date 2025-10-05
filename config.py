import os

# إعدادات البوت - استخدام environment variables للأمان
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7920984703:AAHkRNpgzDxBzS61hAe7r7cO_fATlAB8oqM")
CHANNEL_ID = os.getenv('CHANNEL_ID', "@Kingelg0ld")
QX_SIGNUP_URL = "https://broker-qx.pro/sign-up/?lid=1376472"

# بيانات الدخول لـ QX Broker
QX_EMAIL = os.getenv('QX_EMAIL', 'mohamedels928@gmail.com')
QX_PASSWORD = os.getenv('QX_PASSWORD', 'Mrvip@219')
QX_LOGIN_URL = 'https://qxbroker.com/ar/sign-in/'

# الأزواج المطلوبة
TRADING_PAIRS = [
    'USD/BRL', 'USD/EGP', 'USD/TRY', 'USD/ARS', 'USD/COP',
    'USD/DZD', 'USD/IDR', 'USD/BDT', 'USD/CAD', 'USD/NGN',
    'USD/PKR', 'USD/NR', 'USD/MXN', 'USD/PHP'
]

# إعدادات التداول
TRADE_DURATION = 30
TRADE_INTERVAL = 3
SESSION_START = '06:00'
SESSION_END = '20:00'
