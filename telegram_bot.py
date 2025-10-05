from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import telegram
import logging
import os
import random
from datetime import datetime
from config import UTC3_TZ, TELEGRAM_TOKEN, CHANNEL_ID, QX_SIGNUP_URL

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
    
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ).strftime("%H:%M:%S")
        
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
        """إرسال إشارة التداول"""
        current_time = self.get_utc3_time()
        text = f"""
📊 <b>إشارة تداول جديدة</b>

💰 <b>الزوج:</b> {pair}
🕒 <b>ميعاد الصفقة:</b> {trade_time} 🎯
📈 <b>الاتجاه:</b> {direction}
⏱ <b>المدة:</b> 30 ثانية

⏰ <b>الوقت الحالي:</b> {current_time} (UTC+3)

🔔 <i>الصفقة ستبدأ خلال دقيقة</i>
"""
        return self.send_message(text)
    
    def send_trade_result(self, pair, result, stats):
        """إرسال نتيجة الصفقة"""
        result_emoji = "🎉 WIN" if result == 'WIN' else "❌ LOSS"
        current_time = self.get_utc3_time()
        
        text = f"""
🎯 <b>نتيجة الصفقة</b>

💰 <b>الزوج:</b> {pair}
📊 <b>النتيجة:</b> {result_emoji}
⏰ <b>الوقت:</b> {current_time} (UTC+3)

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
        current_time = self.get_utc3_time()
        text = f"⏰ <b>استعد!</b> - الوقت: {current_time} (UTC+3)\n\n{random.choice(messages)}"
        return self.send_message(text)
