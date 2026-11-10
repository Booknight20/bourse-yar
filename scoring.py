import math

def score_signal(x, horizon="short"):
    score = 0
    reasons = []
    if x["volume_ratio"] >= 1.5:
        score += 20; reasons.append("افزایش حجم معاملات")
    if x["mfi"] >= 55:
        score += 15; reasons.append("قدرت جریان نقدینگی")
    if x["rsi"] >= 50 and x["rsi"] <= 72:
        score += 15; reasons.append("RSI در محدوده مثبت")
    if x["macd_hist"] > 0:
        score += 15; reasons.append("شتاب مثبت MACD")
    if x["close"] > x["ema20"] > x["ema50"]:
        score += 20; reasons.append("روند صعودی میانگین‌ها")
    if math.isfinite(x.get("sma200", float("nan"))) and x["close"] > x["sma200"]:
        score += 15; reasons.append("قیمت بالاتر از میانگین ۲۰۰روزه")
    if horizon == "swing" and x["return5"] > 15:
        score -= 15; reasons.append("هشدار رشد تند کوتاه‌مدت")
    return max(0, min(100, score)), reasons
