import MetaTrader5 as mt5
import pandas as pd
import os
from config import EXCEL_FILE

def execute_trade(asset, direction, rsi, ema_9, ema_21):
    """الدالة المسؤولة عن إرسال أوامر التداول الحية إلى سيرفر MT5 مع إدارة صارمة للمخاطر"""
    # 1. التأكد من اتجاه الصفقة (في حال الـ HOLD لا نفعل شيئاً)
    if direction not in ["BUY", "SELL"]:
        print(f"[⏳ HOLD] نظام الرادار يوصي بالحياد لرمز {asset}. لم يتم فتح أي صفقات.")
        return
    
    # 2. جلب أسعار العرض والطلب الحالية للأصل
    tick = mt5.symbol_info_tick(asset)
    if tick is None:
        print(f"[❌ ERROR] تعذر جلب أسعار لـ {asset} لتنفيذ الصفقة.")
        return

    # 3. إعدادات الحماية وإدارة رأس المال (الريسك)
    lot_size = 0.01  # حجم اللوت الافتراضي لحماية الحساب (يمكنك تعديله حسب رغبتك)
    deviation = 20   # الانحراف المسموح به في السعر (Slippage)
    
    if direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        # حساب الاستوب لوز والتيك بروفيت ديناميكياً (مثال: 30 نقطة استوب و 60 نقطة هدف)
        sl = price - (300 * mt5.symbol_info(asset).point)
        tp = price + (600 * mt5.symbol_info(asset).point)
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = price + (300 * mt5.symbol_info(asset).point)
        tp = price - (600 * mt5.symbol_info(asset).point)

    # 4. بناء هيكل الطلب الموجه لسيرفر التداول
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": asset,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": deviation,
        "magic": 202606,  # الرقم السحري الخاص بالبوت لتمييز صفقاته عن التداول اليدوي
        "comment": "AI Quad-Agent System",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # 5. إرسال الصفقة حياً والتحقق من النتيجة
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"[❌ EXECUTION FAILED] فشل فتح صفقة الـ {direction} لـ {asset}. السبب: {result.comment}")
    else:
        print(f"[🚀 SUCCESS] تم تنفيذ صفقة {direction} حية لـ {asset} بنجاح عند سعر {price}!")
        # توثيق الصفقة الناجحة فوراً في ملف إكسل للحفاظ على سجل الأداء والTelemetry
        log_signal_to_excel(asset, direction, price, rsi, ema_9, ema_21)

def log_signal_to_excel(asset, direction, price, rsi, ema_9, ema_21):
    """توثيق وحفظ بيانات الإشارة والصفقة المنفذة في ملف إكسل للتحليل اللاحق"""
    new_data = {
        "Time": [pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')],
        "Asset": [asset],
        "Direction": [direction],
        "Execution Price": [price],
        "RSI": [rsi],
        "EMA_9": [ema_9],
        "EMA_21": [ema_21]
    }
    df_new = pd.DataFrame(new_data)
    
    if not os.path.exists(EXCEL_FILE):
        df_new.to_excel(EXCEL_FILE, index=False)
    else:
        try:
            df_old = pd.read_excel(EXCEL_FILE)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined.to_excel(EXCEL_FILE, index=False)
        except:
            # في حال كان ملف الإكسل مفتوحاً وجاءت إشارة جديدة لمنع انهيار الكود
            print("[⚠️ WARNING] ملف الإكسل مغلق حالياً أو قيد الاستخدام، تم تجاوز الحفظ المؤقت لحماية الرادار.")