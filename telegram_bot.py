from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
import logging

class TelegramBot:
    def __init__(self):
        self.updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
        self.bot = self.updater.bot
        
    def create_signup_button(self):
        """إنشاء زر التسجيل"""
        keyboard = [[InlineKeyboardButton("📈 سجل في كيوتكس واحصل على 30% بونص", url=QX_SIGNUP_URL)]]
        return InlineKeyboardMarkup(keyboard)
    
    def send_message(self, text, chat_id=CHANNEL_ID):
        """إرسال رسالة مع زر التسجيل"""
        try:
            self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=self.create_signup_button(),
                parse_mode='HTML'
            )
            return True
        except Exception as e:
            logging.error(f"خطأ في إرسال الرسالة: {e}")
            return False
    
    def send_trade_signal(self, pair, direction, trade_time):
        """إرسال إشارة التداول"""
        text = f"""
📊 <b>*استعد صفقه جديده*</b>

💰 <b>الزوج:</b> {pair}
🕒 <b>ميعاد الصفقة:</b> {trade_time}
📈 <b>الاتجاه:</b> {direction}
⏱ <b>المدة:</b> 30 ثانية

🔔 <i>استعد للصفقة القادمة</i>
"""
        return self.send_message(text)
    
    def send_trade_result(self, pair, result, stats):
        """إرسال نتيجة الصفقة"""
        text = f"""
🎯 <b>نتيجة الصفقة</b>

💰 <b>الزوج:</b> {pair}
📊 <b>النتيجة:</b> {'🎉 ربح' if result == 'ربح' else '❌ خسارة'}

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