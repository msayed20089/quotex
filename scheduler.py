import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
from config import CAIRO_TZ

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
            'session_start': datetime.now(CAIRO_TZ)
        }
        
        self.pending_trades = {}
        
    def get_cairo_time(self):
        """الحصول على وقت القاهرة"""
        return datetime.now(CAIRO_TZ)
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة بتوقيت القاهرة"""
        logging.info("🚀 بدء التداول 24 ساعة بتوقيت القاهرة...")
        
        # إرسال رسالة بدء التشغيل
        current_time = self.get_cairo_time().strftime("%H:%M:%S")
        self.telegram_bot.send_message(
            f"🎯 <b>بدء تشغيل البوت بنجاح!</b>\n\n"
            f"📊 البوت يعمل الآن 24 ساعة بتوقيت القاهرة\n"
            f"🔄 صفقة كل 3 دقائق على مدار الساعة\n"
            f"⏰ الوقت الحالي في القاهرة: {current_time}\n\n"
            f"🚀 <i>استعد لفرص ربح مستمرة!</i>"
        )
        
        # بدء أول صفقة فورية
        self.start_immediate_trade()
        
        # جدولة الصفقات المنتظمة كل 3 دقائق
        self.schedule_regular_trades()
    
    def start_immediate_trade(self):
        """بدء أول صفقة فورية"""
        try:
            # حساب أقرب وقت مع ثواني = 00 بتوقيت القاهرة
            now_cairo = self.get_cairo_time()
            next_trade_time = now_cairo.replace(second=0, microsecond=0) + timedelta(minutes=1)
            time_until_trade = (next_trade_time - now_cairo).total_seconds()
            
            logging.info(f"⏰ أول صفقة بعد: {time_until_trade:.0f} ثانية - الساعة: {next_trade_time.strftime('%H:%M:%S')} بتوقيت القاهرة")
            
            # جدولة الصفقة الأولى
            threading.Timer(time_until_trade, self.execute_trade_cycle).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
    
    def schedule_regular_trades(self):
        """جدولة الصفقات كل 3 دقائق بتوقيت القاهرة"""
        # مسح الجدول القديم
        schedule.clear()
        
        # جدولة صفقة كل 3 دقائق على مدار 24 ساعة بتوقيت القاهرة
        for hour in range(0, 24):  # 24 ساعة
            for minute in range(0, 60, 3):  # كل 3 دقائق
                schedule_time = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(schedule_time).do(self.execute_trade_cycle).tag('cairo_trades')
        
        logging.info("✅ تم جدولة الصفقات كل 3 دقائق بتوقيت القاهرة")
    
    def execute_trade_cycle(self):
        """دورة تنفيذ الصفقة الكاملة بتوقيت القاهرة"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # وقت التنفيذ بعد 60 ثانية (مع ثواني = 00)
            execute_time = self.get_cairo_time() + timedelta(seconds=60)
            execute_time_str = execute_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
            
            # تخزين بيانات الصفقة
            trade_id = f"{execute_time_str}_{trade_data['pair']}"
            self.pending_trades[trade_id] = trade_data
            
            # إرسال إشارة الصفقة
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                execute_time_str
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - {execute_time_str} بتوقيت القاهرة")
            
            # تنفيذ الصفقة بعد 60 ثانية بالضبط
            threading.Timer(60, self.process_trade_result, [trade_id]).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة: {e}")
    
    def process_trade_result(self, trade_id):
        """معالجة نتيجة الصفقة"""
        try:
            if trade_id not in self.pending_trades:
                logging.error(f"❌ صفقة غير موجودة: {trade_id}")
                return
                
            trade_data = self.pending_trades[trade_id]
            
            # محاكاة تنفيذ الصفقة
            self.qx_manager.execute_trade(
                trade_data['pair'],
                trade_data['direction'],
                trade_data['duration']
            )
            
            # الحصول على النتيجة
            result = self.qx_manager.get_trade_result()
            
            # تحديث الإحصائيات
            self.stats = self.trading_engine.update_stats(result, self.stats)
            
            # إرسال النتيجة
            self.telegram_bot.send_trade_result(
                trade_data['pair'],
                result,
                self.stats
            )
            
            current_time = self.get_cairo_time().strftime("%H:%M:%S")
            logging.info(f"✅ نتيجة صفقة: {trade_data['pair']} - {result} - الوقت: {current_time} بتوقيت القاهرة")
            
            # مسح الصفقة من القائمة
            del self.pending_trades[trade_id]
            
            # إرسال إحصائيات كل 10 صفقات
            if self.stats['total_trades'] % 10 == 0:
                self.send_periodic_stats()
            
        except Exception as e:
            logging.error(f"❌ خطأ في معالجة النتيجة: {e}")
    
    def send_periodic_stats(self):
        """إرسال إحصائيات دورية"""
        current_time = self.get_cairo_time().strftime("%H:%M:%S")
        stats_text = f"""
📊 <b>إحصائيات دورية</b>

• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}

⏰ آخر تحديث: {current_time} بتوقيت القاهرة

🎯 <i>استمر في التداول!</i>
"""
        self.telegram_bot.send_message(stats_text)
    
    def run_scheduler(self):
        """تشغيل الجدولة"""
        # بدء التداول 24 ساعة
        self.start_24h_trading()
        
        # تشغيل الجدولة
        while True:
            schedule.run_pending()
            time.sleep(1)
