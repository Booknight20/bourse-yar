import logging
import pandas as pd
import pytse_client as tse
from config import TOP_N, MIN_HISTORY
from indicators import calculate_indicators
from scoring import score_signal
from telegram_bot import publish_report

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bourse-yar")

def get_symbol_name(ticker):
    return getattr(ticker, "name", None) or getattr(ticker, "title", None) or getattr(ticker, "symbol", "نماد")

def run():
    log.info("Downloading market history")
    tickers = tse.download(symbols="all", write_to_csv=False, adjust=True)
    candidates = []
    for symbol, df in tickers.items():
        try:
            if df is None or len(df) < MIN_HISTORY:
                continue
            x = calculate_indicators(df)
            if not all(pd.notna(x[k]) for k in ("close", "rsi", "volume_ratio", "ema20", "ema50")):
                continue
            short_score, short_reasons = score_signal(x, "short")
            swing_score, swing_reasons = score_signal(x, "swing")
            candidates.append((symbol, x, short_score, short_reasons, swing_score, swing_reasons))
        except Exception as exc:
            log.warning("Skip %s: %s", symbol, exc)
    candidates.sort(key=lambda z: max(z[2], z[4]), reverse=True)
    lines = ["📊 بورس‌یار هوشمند | گزارش اسکن بازار", "⚠️ خروجی غربالگری است، نه توصیه قطعی خرید یا فروش.", ""]
    lines.append("🔹 گزینه‌های نوسان‌گیری (۱ تا ۷ روز)")
    for symbol, x, a, ar, b, br in sorted(candidates, key=lambda z:z[2], reverse=True)[:TOP_N]:
        if a < 40: continue
        lines.append(f"• {symbol} | امتیاز {a}/100 | RSI {x['rsi']:.1f} | حجم {x['volume_ratio']:.1f}x")
        if ar: lines.append("  " + "، ".join(ar[:3]))
    lines += ["", "🔸 گزینه‌های کوتاه‌مدت (۱ تا ۴ هفته)"]
    for symbol, x, a, ar, b, br in sorted(candidates, key=lambda z:z[4], reverse=True)[:TOP_N]:
        if b < 40: continue
        lines.append(f"• {symbol} | امتیاز {b}/100 | RSI {x['rsi']:.1f} | حجم {x['volume_ratio']:.1f}x")
        if br: lines.append("  " + "، ".join(br[:3]))
    if len(lines) <= 5:
        lines.append("در این اجرا نماد واجد شرایط کافی پیدا نشد یا داده‌ها ناقص بودند.")
    lines += ["", "معیارها: روند میانگین‌ها، RSI، MACD، MFI و حجم نسبی.",
              "ورود پول حقیقی/حقوقی و معاملات بلوکی در این نسخه هنوز تأیید مستقل نمی‌شوند."]
    publish_report("\n".join(lines))

if __name__ == "__main__":
    run()
