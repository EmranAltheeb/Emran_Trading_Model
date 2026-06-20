import os
import requests
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from config import FINNHUB_KEY

def calculate_rsi(prices, period=14):
    """حساب مؤشر القوة النسبية RSI"""
    if len(prices) < period: return 50.0
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / (down if down != 0 else 0.00001)
    rsi = np.zeros_like(prices)
    rsi[:period] = 100.0 - (100.0 / (1.0 + rs))

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        up_val = delta if delta > 0 else 0.0
        down_val = -delta if delta < 0 else 0.0
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / (down if down != 0 else 0.00001)
        rsi[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi[-1]

def get_finnhub_sentiment(asset):
    """سحب حركة السوق الفورية والأسعار العالمية من Finnhub"""
    try:
        clean_symbol = asset.replace("s", "").upper()
        if "XAUUSD" in asset.upper(): clean_symbol = "GC=F"
        
        url = f"https://finnhub.io/api/v1/quote?symbol={clean_symbol}&token={FINNHUB_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if "c" in data and data["c"] > 0:
            return f"Finnhub Live Price: {data['c']} | High: {data['h']} | Low: {data['l']}"
        return "Finnhub Telemetry: Asset not listed or limit reached."
    except:
        return "Finnhub Telemetry: Temporarily Unavailable."

def get_market_data(asset, style):
    """الدالة الرئيسية الفائقة لتجميع داتا MT5 المعززة بالمؤشرات الجديدة ودمجها مع Finnhub"""
    timeframe = mt5.TIMEFRAME_M5 if style == "Scalping" else mt5.TIMEFRAME_H4
    rates = mt5.copy_rates_from_pos(asset, timeframe, 0, 50)
    
    # قيم افتراضية في حال انقطاع الداتا
    rsi_val, ema_9, ema_21 = 50.0, 0.0, 0.0
    atr_val, macd_line, macd_signal, bb_upper, bb_lower = 0.0, 0.0, 0.0, 0.0, 0.0
    candles_txt = "No Data"
    
    if rates is not None and len(rates) > 0:
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # 1. حساب المؤشرات الأساسية
        close_prices = df['close'].to_numpy()
        rsi_val = calculate_rsi(close_prices, 14)
        df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
        df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
        ema_9 = df['ema_9'].iloc[-1]
        ema_21 = df['ema_21'].iloc[-1]
        
        # 2. حساب مؤشر الـ ATR (قياس التقلب اللحظي)
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = (df['high'] - df['close'].shift(1)).abs()
        df['tr3'] = (df['low'] - df['close'].shift(1)).abs()
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        atr_val = df['atr'].iloc[-1] if not pd.isna(df['atr'].iloc[-1]) else 0.0

        # 3. حساب مؤشر الـ MACD (الزخم والاتجاه العام)
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        df['macd_line'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd_line'].ewm(span=9, adjust=False).mean()
        macd_line = df['macd_line'].iloc[-1]
        macd_signal = df['macd_signal'].iloc[-1]

        # 4. حساب مؤشر البولنجر باندز Bollinger Bands (مناطق السعر الغالي والرخيص)
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['std_20'] = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['sma_20'] + (df['std_20'] * 2)
        df['bb_lower'] = df['sma_20'] - (df['std_20'] * 2)
        bb_upper = df['bb_upper'].iloc[-1] if not pd.isna(df['bb_upper'].iloc[-1]) else 0.0
        bb_lower = df['bb_lower'].iloc[-1] if not pd.isna(df['bb_lower'].iloc[-1]) else 0.0
        
        # صياغة الملخص الفني لإرساله للذكاء الاصطناعي
        candle_summary = ""
        for i, row in df.tail(10).iterrows():
            candle_summary += f"T:{row['time'].strftime('%H:%M')} | C:{row['close']} | V:{row['tick_volume']}\n"
        candles_txt = candle_summary
        
    # دمج تأكيد Finnhub والأرقام الفائقة الجديدة في نص التقرير
    finnhub_info = get_finnhub_sentiment(asset)
    
    analysis_report = (
        f"{candles_txt}\n"
        f"[ADVANCED TECHNICAL METRICS]:\n"
        f"• ATR (Volatility): {atr_val:.5f}\n"
        f"• MACD Line: {macd_line:.5f} | Signal Line: {macd_signal:.5f}\n"
        f"• Bollinger Bands -> Upper: {bb_upper:.5f} | Lower: {bb_lower:.5f}\n\n"
        f"[GLOBAL MARKET SENTIMENT (FINNHUB)]:\n{finnhub_info}"
    )
        
    return rsi_val, ema_9, ema_21, analysis_report