import schedule
import time
import threading
from datetime import datetime, timedelta
import logging

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
            'session_start': datetime.now()
        }
        
        self.next_trade_data = None
        self.trade_count = 0
        
    def start_immediate_trading(self):
        """بدء التداول الفوري بعد التشغيل"""
        logging.info("🚀 بدء التداول الفوري...")
        
        # إرسال رسالة بدء التشغيل
        self.telegram_bot.send_message(
            "🎯 <b>بدء تشغيل البوت بنجاح!</b>\n\n"
            "📊 البوت يعمل الآن وسيبدأ الصفقات فوراً\n"
            "⏰ جلسة التداول: 6:00 صباحاً - 8:00 مساءً\n"
            "🔄 صفقة كل 3 دقائق\n\n"
            "🚀 <i>استعد لفرص ربح مميزة!</i>"
        )
        
        # بدء أول صفقة خلال 30 ثانية
        schedule.every(30).seconds.do(self.execute_immediate_trade)
        
        # بعد أول صفقة، انتقل للنظام كل 3 دقائق
        self.trade_count = 0
        
    def execute_immediate_trade(self):
        """تنفيذ صفقة فورية"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # إرسال إشارة الصفقة
            trade_time = datetime.now().strftime("%H:%M:%S")
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                trade_time
            )
            
            logging.info(f"📤 تم إرسال إشارة الصفقة: {trade_data['pair']} - {trade_data['direction']}")
            
            # تنفيذ الصفقة بعد 35 ثانية
            threading.Timer(35, self.process_trade_result, [trade_data]).start()
            
            # بعد الصفقة الأولى، انتقل للنظام كل 3 دقائق
            self.trade_count += 1
            if self.trade_count == 1:
                schedule.clear()
                self.start_regular_schedule()
                
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
    
    def start_regular_schedule(self):
        """بدء الجدولة المنتظمة كل 3 دقائق"""
        logging.info("🔄 بدء الجدولة المنتظمة كل 3 دقائق")
        
        # صفقة كل 3 دقائق
        schedule.every(3).minutes.do(self.execute_regular_trade)
        
        # إرسال رسالة تأكيد
        self.telegram_bot.send_message(
            "🔄 <b>بدء الجدولة المنتظمة</b>\n\n"
            "📊 البوت يعمل الآن بالنظام المنتظم\n"
            "⏰ صفقة كل 3 دقائق\n"
            "🕗 من 6:00 صباحاً إلى 8:00 مساءً\n\n"
            "🎯 <i>جاري تحضير الصفقات القادمة...</i>"
        )
    
    def execute_regular_trade(self):
        """تنفيذ صفقة منتظمة"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # إرسال إشارة الصفقة قبل 60 ثانية من التنفيذ
            signal_time = datetime.now() + timedelta(seconds=60)
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                signal_time.strftime("%H:%M:%S")
            )
            
            logging.info(f"📤 تم إرسال إشارة الصفقة: {trade_data['pair']} - {trade_data['direction']}")
            
            # تنفيذ الصفقة بعد 60 ثانية
            threading.Timer(60, self.process_trade_result, [trade_data]).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة المنتظمة: {e}")
    
    def process_trade_result(self, trade_data):
        """معالجة نتيجة الصفقة"""
        try:
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
            
            logging.info(f"✅ تم معالجة صفقة: {trade_data['pair']} - {result}")
            
        except Exception as e:
            logging.error(f"❌ خطأ في معالجة النتيجة: {e}")
    
    def run_scheduler(self):
        """تشغيل الجدولة"""
        # بدء التداول الفوري
        self.start_immediate_trading()
        
        # تشغيل الجدولة
        while True:
            schedule.run_pending()
            time.sleep(1)
