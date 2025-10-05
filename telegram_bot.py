from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import os
import random

# استيراد الإعدادات من config
try:
    from config import CHANNEL_ID, TELEGRAM_TOKEN, QX_SIGNUP_URL
except ImportError:
    # استخدام القيم الافتراضية إذا فشل الاستيراد
    CHANNEL_ID = os.getenv('CHANNEL_ID', '@Kingelg0ld')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '7920984703:AAHkRNpgzDxBzS61hAe7r7cO_fATlAB8oqM')
    QX_SIGNUP_URL = "https://broker-qx.pro/sign-up/?lid=1376472"

class TelegramBot:
    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.channel_id = CHANNEL_ID
        self.signup_url = QX_SIGNUP_URL
        try:
            self.bot = telegram.Bot(token=self.token)
        except Exception as e:
            logging.error(f"خطأ في تهيئة بوت التليجرام: {e}")
            self.bot = None
        
    def create_signup_button(self):
        """إنشاء زر التسجيل"""
        keyboard = [[InlineKeyboardButton("📈 سجل في كيوتكس واحصل على 30% بونص", url=self.signup_url)]]
        return InlineKeyboardMarkup(keyboard)
    
    def send_message(self, text, chat_id=None):
        """إرسال رسالة مع زر التسجيل"""
        if chat_id is None:
            chat_id = self.channel_id
            
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.create_signup_button(),
                parse_mode='HTML'
            )
            logging.info("✅ تم إرسال الرسالة بنجاح")
            return True
        except Exception as e:
            logging.error(f"❌ خطأ في إرسال الرسالة: {e}")
            return False
    
    def send_trade_signal(self, pair, direction, trade_time):
        """إرسال إشارة التداول في وقت دقيق"""
        text = f"""
📊 <b>إشارة تداول جديدة</b>

💰 <b>الزوج:</b> {pair}
🕒 <b>ميعاد الصفقة:</b> {trade_time} ⏰
📈 <b>الاتجاه:</b> {direction}
⏱ <b>المدة:</b> 30 ثانية

🔔 <i>استعد للصفقة القادمة</i>
"""
        return self.send_message(text)
    
    def send_trade_result(self, pair, result, stats):
        """إرسال نتيجة الصفقة"""
        result_emoji = "🎉 ربح" if result == 'ربح' else "❌ خسارة"
        text = f"""
🎯 <b>نتيجة الصفقة</b>

💰 <b>الزوج:</b> {pair}
📊 <b>النتيجة:</b> {result_emoji}

📈 <b>إحصائيات الجلسة:</b>
• إجمالي الصفقات: {stats['total_trades']}
• الصفقات الرابحة: {stats['win_trades']}
• الصفقات الخاسرة: {stats['loss_trades']}
• صافي الربح: {stats['net_profit']}

🚀 <i>استمر في التداول بذكاء!</i>
"""
        return self.send_message(text)
    
    def send_motivational_message(self):
        """إرسال رسالة تحفيزية"""
        messages = [
            "🔥 استعد للربح! الصفقات القادمة ستكون مميزة",
            "💪 لحظات من التركيز تخلق أيامًا من النجاح",
            "🚀 الفرص لا تأتي بالصدفة، بل نصنعها بالتداول الذكي",
            "📈 كل صفقة جديدة هي فرصة للربح"
        ]
        text = f"⏰ <b>استعد!</b>\n\n{random.choice(messages)}"
        return self.send_message(text)
