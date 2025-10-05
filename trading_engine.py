import random
from datetime import datetime
from config import UTC3_TZ

class TradingEngine:
    def __init__(self):
        from config import TRADING_PAIRS
        self.pairs = TRADING_PAIRS
        
    def analyze_and_decide(self):
        """تحليل عشوائي واتخاذ قرار التداول"""
        pair = random.choice(self.pairs)
        direction = random.choice(['BUY', 'SELL'])
        
        # وقت UTC+3 مع ثواني = 00
        utc3_time = datetime.now(UTC3_TZ)
        trade_time = utc3_time.replace(second=0, microsecond=0).strftime("%H:%M:%S")
        
        return {
            'pair': pair,
            'direction': direction,
            'trade_time': trade_time,
            'duration': 30
        }
    
    def update_stats(self, result, stats):
        """تحديث الإحصائيات"""
        stats['total_trades'] += 1
        
        if result == 'WIN':
            stats['win_trades'] += 1
        else:
            stats['loss_trades'] += 1
            
        stats['net_profit'] = stats['win_trades'] - stats['loss_trades']
        return stats
    
    def get_utc3_time(self):
        """الحصول على وقت UTC+3 الحالي"""
        return datetime.now(UTC3_TZ).strftime("%H:%M:%S")
