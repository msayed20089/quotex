import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
from config import UTC3_TZ

class TradingScheduler:
    def __init__(self):
        from qx_broker import QXBrokerManager
        from telegram_bot import TelegramBot
        from trading_engine import TradingEngine
        
        self.qx_manager = QXBrokerManager()
        self.telegram_bot = TelegramBot()
        self.trading_engine = TradingEngine()
        
        self.stats = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'net_profit': 0,
            'session_start': datetime.now(UTC3_TZ)
        }
        
        self.pending_trades = {}
        self.regular_schedule_started = False
        
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ)
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة بتوقيت UTC+3"""
        logging.info("🚀 بدء التداول 24 ساعة بتوقيت UTC+3...")
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        self.telegram_bot.send_message(
            f"🎯 <b>بدء تشغيل البوت بنجاح!</b>\n\n"
            f"📊 البوت يعمل الآن 24 ساعة\n"
            f"🔄 صفقة كل 3 دقائق\n"
            f"⏰ الوقت الحالي: {current_time} (UTC+3)\n\n"
            f"🚀 <i>استعد لفرص ربح مستمرة!</i>"
        )
        
        # بدء أول صفقة فورية
        self.start_immediate_trade()
        
        # جدولة الصفقات المنتظمة كل 3 دقائق
        self.schedule_regular_trades()
    
    def start_immediate_trade(self):
        """بدء أول صفقة فورية"""
        try:
            now_utc3 = self.get_utc3_time()
            next_trade_time = now_utc3.replace(second=0, microsecond=0) + timedelta(minutes=1)
            time_until_trade = (next_trade_time - now_utc3).total_seconds()
            
            logging.info(f"⏰ أول صفقة بعد: {time_until_trade:.0f} ثانية - الساعة: {next_trade_time.strftime('%H:%M:%S')} (UTC+3)")
            
            threading.Timer(time_until_trade, self.execute_trade_cycle).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
    
    def schedule_regular_trades(self):
        """جدولة الصفقات كل 3 دقائق بتوقيت UTC+3"""
        schedule.clear()
        
        # جدولة صفقة كل 3 دقائق على مدار 24 ساعة
        for hour in range(0, 24):
            for minute in range(0, 60, 3):
                schedule_time = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(schedule_time).do(self.execute_trade_cycle)
        
        logging.info("✅ تم جدولة الصفقات كل 3 دقائق بتوقيت UTC+3")
    
    def execute_trade_cycle(self):
        """دورة تنفيذ الصفقة الكاملة"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # وقت التنفيذ بعد 60 ثانية
            execute_time = self.get_utc3_time() + timedelta(seconds=60)
            execute_time_str = execute_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
            
            # تخزين بيانات الصفقة
            trade_id = f"{execute_time_str}_{trade_data['pair']}"
            self.pending_trades[trade_id] = {
                'data': trade_data,
                'start_time': execute_time,
                'end_time': execute_time + timedelta(seconds=30)
            }
            
            # إرسال إشارة الصفقة
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                execute_time_str
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - {execute_time_str} (UTC+3)")
            
            # تنفيذ الصفقة بعد 60 ثانية بالضبط
            threading.Timer(60, self.start_trade_execution, [trade_id]).start()
            
            # بدء الجدولة المنتظمة بعد الصفقة الأولى
            if not self.regular_schedule_started:
                self.regular_schedule_started = True
                self.start_regular_schedule_message()
                
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة: {e}")
    
    def start_regular_schedule_message(self):
        """إرسال رسالة بدء الجدولة المنتظمة"""
        self.telegram_bot.send_message(
            "🔄 <b>بدء الجدولة المنتظمة</b>\n\n"
            "📊 البوت يعمل الآن بالنظام المنتظم\n"
            "⏰ صفقة كل 3 دقائق بتوقيت UTC+3\n"
            "🎯 <i>جاري تحضير الصفقات القادمة...</i>"
        )
    
    def start_trade_execution(self, trade_id):
        """بدء تنفيذ الصفقة في المنصة"""
        try:
            if trade_id not in self.pending_trades:
                return
                
            trade_info = self.pending_trades[trade_id]
            trade_data = trade_info['data']
            
            # تنفيذ الصفقة في المنصة
            success = self.qx_manager.execute_trade(
                trade_data['pair'],
                trade_data['direction'],
                trade_data['duration']
            )
            
            if success:
                logging.info(f"✅ بدء صفقة في المنصة: {trade_data['pair']} - {trade_data['direction']}")
                
                # جدولة نشر النتيجة بعد 30 ثانية
                time_until_result = (trade_info['end_time'] - self.get_utc3_time()).total_seconds()
                threading.Timer(time_until_result, self.publish_trade_result, [trade_id]).start()
            else:
                logging.error(f"❌ فشل تنفيذ الصفقة في المنصة: {trade_data['pair']}")
                
        except Exception as e:
            logging.error(f"❌ خطأ في تنفيذ الصفقة: {e}")
    
    def publish_trade_result(self, trade_id):
        """نشر نتيجة الصفقة بعد 30 ثانية"""
        try:
            if trade_id not in self.pending_trades:
                return
                
            trade_info = self.pending_trades[trade_id]
            trade_data = trade_info['data']
            
            # الحصول على النتيجة من المنصة
            result = self.qx_manager.get_trade_result()
            
            # تحديث الإحصائيات
            self.stats = self.trading_engine.update_stats(result, self.stats)
            
            # إرسال النتيجة
            self.telegram_bot.send_trade_result(
                trade_data['pair'],
                result,
                self.stats
            )
            
            current_time = self.get_utc3_time().strftime("%H:%M:%S")
            logging.info(f"🎯 نتيجة صفقة: {trade_data['pair']} - {result} - الوقت: {current_time} (UTC+3)")
            
            # مسح الصفقة
            del self.pending_trades[trade_id]
            
            # إحصائيات كل 10 صفقات
            if self.stats['total_trades'] % 10 == 0:
                self.send_periodic_stats()
            
        except Exception as e:
            logging.error(f"❌ خطأ في نشر النتيجة: {e}")
    
    def send_periodic_stats(self):
        """إرسال إحصائيات دورية"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        stats_text = f"""
📊 <b>إحصائيات دورية</b>

• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}

⏰ آخر تحديث: {current_time} (UTC+3)

🎯 <i>استمر في التداول!</i>
"""
        self.telegram_bot.send_message(stats_text)
    
    def run_scheduler(self):
        """تشغيل الجدولة"""
        self.start_24h_trading()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
