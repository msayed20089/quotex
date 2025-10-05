import random
from datetime import datetime

class TradingEngine:
    def __init__(self):
        from config import TRADING_PAIRS
        self.pairs = TRADING_PAIRS
        
    def analyze_and_decide(self):
        """تحليل عشوائي واتخاذ قرار التداول"""
        pair = random.choice(self.pairs)
        direction = random.choice(['BUY', 'SELL'])
        trade_time = datetime.now().strftime("%H:%M:%S")
        
        return {
            'pair': pair,
            'direction': direction,
            'trade_time': trade_time,
            'duration': 30
        }
    
    def update_stats(self, result, stats):
        """تحديث الإحصائيات"""
        stats['total_trades'] += 1
        
        if result == 'ربح':
            stats['win_trades'] += 1
        else:
            stats['loss_trades'] += 1
            
        stats['net_profit'] = stats['win_trades'] - stats['loss_trades']
        return stats
        def analyze_and_decide(self):
    """تحليل عشوائي واتخاذ قرار التداول"""
    pair = random.choice(self.pairs)
    direction = random.choice(['BUY', 'SELL'])
    
    # وقت دقيق بدون ثواني
    current_time = datetime.now()
    trade_time = current_time.replace(second=0, microsecond=0).strftime("%H:%M:00")
    
    return {
        'pair': pair,
        'direction': direction,
        'trade_time': trade_time,
        'duration': 30
    }
