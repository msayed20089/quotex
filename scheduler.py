import schedule
import time
from datetime import datetime, timedelta
from threading import Thread

class TradingScheduler:
    def __init__(self):
        self.qx_manager = QXBrokerManager()
        self.telegram_bot = TelegramBot()
        self.trading_engine = TradingEngine()
        self.stats = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'net_profit': 0,
            'session_start': datetime.now()
        }
        self.next_trade_time = None
        
    def schedule_tasks(self):
        """جدولة جميع المهام"""
        # الساعة 5:40 صباحاً
        schedule.every().day.at("05:40").do(self.send_start_announcement)
        
        # الساعة 5:58 صباحاً
        schedule.every().day.at("05:58").do(self.send_preparation_message)
        
        # بدء الصفقات من 6:00 إلى 20:00
        self.schedule_trading_session()
        
        # إعادة تعيين الإحصائيات كل 6 ساعات
        schedule.every(6).hours.do(self.reset_session_stats)
        
        # تقرير نهائي الساعة 2 صباحاً
        schedule.every().day.at("02:00").do(self.send_daily_report)
    
    def send_start_announcement(self):
        """إرسال إعلان بدء التداول"""
        text = """
🔄 <b>البوت يبدأ نشر الصفقات الساعة 6 صباحاً</b>

📊 <i>استعد لجلسة تداول مليئة بالفرص!</i>

🎯 <b>التسجيل في منصة كيوتكس والحصول على بونص يصل إلى 30%</b>
سجل من اللينك ده: https://broker-qx.pro/sign-up/?lid=1376472
"""
        self.telegram_bot.send_message(text)
    
    def send_preparation_message(self):
        """إرسال رسالة الاستعداد"""
        self.telegram_bot.send_motivational_message()
    
    def schedule_trading_session(self):
        """جدولة جلسة التداول كل 3 دقائق"""
        start_time = datetime.now().replace(hour=6, minute=0, second=0, microsecond=0)
        end_time = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
        
        current_time = start_time
        while current_time <= end_time:
            schedule_time = current_time.strftime("%H:%M")
            
            # جدولة إشارة الصفقة قبل دقيقة
            signal_time = (current_time - timedelta(minutes=1)).strftime("%H:%M")
            schedule.every().day.at(signal_time).do(
                self.send_trade_signal, 
                current_time + timedelta(seconds=35)
            )
            
            # جدولة تنفيذ الصفقة
            schedule.every().day.at(schedule_time).do(
                self.execute_scheduled_trade,
                current_time + timedelta(seconds=35)
            )
            
            current_time += timedelta(minutes=3)
    
    def send_trade_signal(self, trade_execution_time):
        """إرسال إشارة التداول قبل دقيقة"""
        trade_data = self.trading_engine.analyze_and_decide()
        self.next_trade_data = trade_data
        self.next_trade_time = trade_execution_time
        
        self.telegram_bot.send_trade_signal(
            trade_data['pair'],
            trade_data['direction'],
            trade_execution_time.strftime("%H:%M:%S")
        )
    
    def execute_scheduled_trade(self, execution_time):
        """تنفيذ الصفقة المجدولة"""
        if not self.next_trade_data:
            return
        
        # تنفيذ الصفقة على المنصة
        success = self.qx_manager.execute_trade(
            self.next_trade_data['pair'],
            self.next_trade_data['direction'],
            self.next_trade_data['duration']
        )
        
        if success:
            # الانتظار لمعرفة النتيجة
            time.sleep(35)
            result = self.qx_manager.get_trade_result()
            
            # تحديث الإحصائيات
            self.stats = self.trading_engine.update_stats(result, self.stats)
            
            # إرسال النتيجة
            self.telegram_bot.send_trade_result(
                self.next_trade_data['pair'],
                result,
                self.stats
            )
        
        self.next_trade_data = None
    
    def reset_session_stats(self):
        """إعادة تعيين إحصائيات الجلسة"""
        self.stats = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'net_profit': 0,
            'session_start': datetime.now()
        }
    
    def send_daily_report(self):
        """إرسال تقرير يومي"""
        text = f"""
📊 <b>تقرير التداول اليومي</b>

📈 <b>إحصائيات اليوم:</b>
• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}

🎯 <i>نراكم في جلسة تداول جديدة!</i>
"""
        self.telegram_bot.send_message(text)
        self.reset_session_stats()
    
    def run_scheduler(self):
        """تشغيل الجدولة"""
        self.schedule_tasks()
        while True:
            schedule.run_pending()
            time.sleep(1)