import schedule
import time
import threading
from datetime import datetime, timedelta
import logging
import random

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
        
        self.is_trading_session = False
        
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
        
        # بدء أول صفقة في أقرب وقت دقيق (بدون ثواني)
        self.schedule_next_immediate_trade()
        
    def schedule_next_immediate_trade(self):
        """جدولة الصفقة الفورية في أقرب وقت دقيق"""
        now = datetime.now()
        
        # حساب أقرب وقت دقيق (بدون ثواني)
        next_trade_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # إذا كان خارج وقت التداول (8 مساءً - 6 صباحاً)، ابدأ من 6 الصبح
        if now.hour >= 20 or now.hour < 6:
            next_trade_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
            if now.hour >= 20:
                next_trade_time += timedelta(days=1)
        
        time_until_trade = (next_trade_time - now).total_seconds()
        
        logging.info(f"⏰ next trade at: {next_trade_time.strftime('%H:%M:%S')}")
        
        # جدولة الصفقة
        threading.Timer(time_until_trade, self.execute_immediate_trade).start()
        
        # بعد الصفقة الفورية، ابدأ الجدولة المنتظمة
        self.is_trading_session = True
    
    def execute_immediate_trade(self):
        """تنفيذ صفقة فورية في وقت دقيق"""
        try:
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            current_time = datetime.now().strftime("%H:%M:00")
            
            # إرسال إشارة الصفقة قبل 60 ثانية من التنفيذ
            signal_time = (datetime.now() + timedelta(seconds=60)).strftime("%H:%M:00")
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                signal_time
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - {signal_time}")
            
            # تنفيذ الصفقة بعد 60 ثانية بالضبط
            threading.Timer(60, self.process_trade_result, [trade_data]).start()
            
            # بعد الصفقة الأولى، ابدأ الجدولة المنتظمة كل 3 دقائق
            if not hasattr(self, 'regular_schedule_started'):
                self.regular_schedule_started = True
                self.start_regular_schedule()
                
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة الفورية: {e}")
    
    def start_regular_schedule(self):
        """بدء الجدولة المنتظمة كل 3 دقائق في أوقات دقيقة"""
        logging.info("🔄 بدء الجدولة المنتظمة كل 3 دقائق")
        
        # إرسال رسالة تأكيد
        self.telegram_bot.send_message(
            "🔄 <b>بدء الجدولة المنتظمة</b>\n\n"
            "📊 البوت يعمل الآن بالنظام المنتظم\n"
            "⏰ صفقة كل 3 دقائق في أوقات دقيقة\n"
            "🕗 من 6:00 صباحاً إلى 8:00 مساءً\n\n"
            "🎯 <i>جاري تحضير الصفقات القادمة...</i>"
        )
        
        # جدولة الصفقات كل 3 دقائق في أوقات دقيقة
        self.schedule_regular_trades()
    
    def schedule_regular_trades(self):
        """جدولة الصفقات كل 3 دقائق في أوقات دقيقة"""
        now = datetime.now()
        
        # بدء من الدقيقة الحالية + 3 دقائق
        start_minute = (now.minute // 3 + 1) * 3
        if start_minute >= 60:
            start_minute = 0
        
        # إنشاء الجدول لكل 3 دقائق من 6:00 إلى 20:00
        for hour in range(6, 20):  # من 6 صباحاً إلى 8 مساءً
            for minute in range(0, 60, 3):  # كل 3 دقائق
                if hour == 6 and minute < 0:  # تخطي الأوقات قبل 6:00
                    continue
                if hour == 20 and minute > 0:  # تخطي الأوقات بعد 20:00
                    continue
                
                schedule_time = f"{hour:02d}:{minute:02d}"
                schedule.every().day.at(schedule_time).do(self.execute_scheduled_trade, schedule_time)
        
        logging.info("✅ تم جدولة الصفقات كل 3 دقائق في أوقات دقيقة")
    
    def execute_scheduled_trade(self, schedule_time):
        """تنفيذ صفقة مجدولة في وقت دقيق"""
        try:
            # تحقق إذا كان وقت التداول نشط
            current_hour = datetime.now().hour
            if not (6 <= current_hour < 20):
                return
            
            # تحليل واتخاذ قرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # إرسال إشارة الصفقة قبل 60 ثانية من التنفيذ
            self.telegram_bot.send_trade_signal(
                trade_data['pair'],
                trade_data['direction'],
                schedule_time
            )
            
            logging.info(f"📤 إشارة صفقة: {trade_data['pair']} - {trade_data['direction']} - {schedule_time}")
            
            # تنفيذ الصفقة بعد 60 ثانية بالضبط
            threading.Timer(60, self.process_trade_result, [trade_data]).start()
            
        except Exception as e:
            logging.error(f"❌ خطأ في الصفقة المجدولة: {e}")
    
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
            
            logging.info(f"✅ نتيجة صفقة: {trade_data['pair']} - {result}")
            
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
