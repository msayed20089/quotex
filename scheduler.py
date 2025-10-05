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
            'session_start': self.get_cairo_time()
        }
        
        self.pending_trades = {}
        self.trade_counter = 0
        
    def get_cairo_time(self):
        """الحصول على وقت القاهرة +3 ساعات"""
        cairo_time = datetime.now(CAIRO_TZ)
        # إضافة 3 ساعات للتوقيت
        adjusted_time = cairo_time + timedelta(hours=3)
        return adjusted_time
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة"""
        logging.info("🚀 بدء التداول 24 ساعة بتوقيت القاهرة+3...")
        
        current_time = self.get_cairo_time().strftime("%H:%M:%S")
        self.telegram_bot.send_message(
            f"🎯 <b>بدء تشغيل البوت بنجاح!</b>\n\n"
            f"📊 البوت يعمل الآن 24 ساعة\n"
            f"🔄 صفقة كل 3 دقائق\n"
            f"⏰ الوقت الحالي: {current_time}\n\n"
            f"🚀 <i>استعد لفرص ربح مستمرة!</i>"
        )
        
        # بدء أول صفقة فورية
        self.start_immediate_trade()
        
        # جدولة الصفقات المنتظمة كل 3 دقائق
        self.schedule_regular_trades()
    
    def start_immediate_trade(self):
        """بدء أول صفقة فورية"""
        try:
            now_cairo = self.get_cairo_time()
            next_trade_time = now_cairo.replace(second=0, microsecond=0) + timedelta(minutes=1)
            time_until_trade = (next_trade_time - now_cairo).total_seconds()
            
            logging.info(f"⏰ أول صفقة بعد: {time_until_trade:.0f} ثانية - الساعة: {next_trade_time.strftime('%H:%M:%S')}")
            
            threading.Timer(time_until_trade, self.execute_trade_cycle).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
    
    def schedule_regular_trades(self):
        """جدولة الصفقات كل 3 دقائق"""
        schedule.clear()
        
        for hour in range(0, 24):
            for minute in range(0, 60, 3):
                schedule_time = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(schedule_time).do(self.execute_trade_cycle)
        
        logging.info("✅ تم جدولة الصفقات كل 3 دقائق")
    
    def execute_trade_cycle(self):
        """دورة تنفيذ الصفقة الكاملة"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # وقت بداية الصفقة (الآن + 60 ثانية)
            trade_start_time = self.get_cairo_time() + timedelta(seconds=60)
            trade_start_str = trade_start_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
            
            # وقت نهاية الصفقة (بعد 30 ثانية من البداية)
            trade_end_time = trade_start_time + timedelta(seconds=30)
            trade_end_str = trade_end_time.strftime("%H:%M:%S")
            
            # تخزين بيانات الصفقة
            trade_id = f"{trade_start_str}_{trade_data['pair']}"
            self.pending_trades[trade_id] = {
                'data': trade_data,
                'start_time': trade_start_time,
                'end_time': trade_end_time
            }
            
            # إرسال إشارة الصفقة
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                trade_start_str
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - تبدأ: {trade_start_str}")
            
            # تنفيذ الصفقة بعد 60 ثانية (بداية الصفقة)
            threading.Timer(60, self.start_trade_execution, [trade_id]).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة: {e}")
    
    def start_trade_execution(self, trade_id):
        """بدء تنفيذ الصفقة في المنصة"""
        try:
            if trade_id not in self.pending_trades:
                return
                
            trade_info = self.pending_trades[trade_id]
            trade_data = trade_info['data']
            
            # تنفيذ الصفقة في المنصة
            self.qx_manager.execute_trade(
                trade_data['pair'],
                trade_data['direction'],
                trade_data['duration']
            )
            
            logging.info(f"✅ بدء صفقة في المنصة: {trade_data['pair']} - {trade_data['direction']}")
            
            # جدولة نشر النتيجة بعد 30 ثانية (نهاية الصفقة)
            time_until_result = (trade_info['end_time'] - self.get_cairo_time()).total_seconds()
            threading.Timer(time_until_result, self.publish_trade_result, [trade_id]).start()
            
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
            
            current_time = self.get_cairo_time().strftime("%H:%M:%S")
            logging.info(f"🎯 نتيجة صفقة: {trade_data['pair']} - {result} - الوقت: {current_time}")
            
            # مسح الصفقة
            del self.pending_trades[trade_id]
            
            # إحصائيات كل 10 صفقات
            if self.stats['total_trades'] % 10 == 0:
                self.send_periodic_stats()
            
        except Exception as e:
            logging.error(f"❌ خطأ في نشر النتيجة: {e}")
    
    def send_periodic_stats(self):
        """إرسال إحصائيات دورية"""
        current_time = self.get_cairo_time().strftime("%H:%M:%S")
        stats_text = f"""
📊 <b>إحصائيات دورية</b>

• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}

⏰ آخر تحديث: {current_time}

🎯 <i>استمر في التداول!</i>
"""
        self.telegram_bot.send_message(stats_text)
    
    def run_scheduler(self):
        """تشغيل الجدولة"""
        self.start_24h_trading()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
