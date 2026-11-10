import json
import sys
import requests

BASE = "https://cdn.tsetmc.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.tsetmc.com/",
    "Origin": "https://www.tsetmc.com",
}

def main():
    session = requests.Session()
    session.headers.update(HEADERS)

    search_url = f"{BASE}/Instrument/GetInstrumentSearch/%D9%81%D9%88%D9%84%D8%A7%D8%AF"
    print("1) Checking CDN instrument search...")
    response = session.get(search_url, timeout=20)
    print(f"   HTTP {response.status_code}; content-type={response.headers.get('content-type', '')}")
    response.raise_for_status()
    payload = response.json()
    matches = payload.get("instrumentSearch") or []
    match = next((x for x in matches if x.get("lVal18AFC") == "فولاد"), None)
    if not match:
        print("ERROR: Search succeeded, but no exact فولاد symbol was found.")
        print(json.dumps(payload, ensure_ascii=False)[:1500])
        sys.exit(2)

    ins_code = match.get("insCode")
    if not ins_code:
        raise RuntimeError("Search result did not contain insCode")

    print("2) Checking daily history endpoint for فولاد...")
    history_url = f"{BASE}/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"
    history_response = session.get(history_url, timeout=30)
    print(f"   HTTP {history_response.status_code}; content-type={history_response.headers.get('content-type', '')}")
    history_response.raise_for_status()
    history_payload = history_response.json()
    rows = history_payload.get("closingPriceDaily") or []
    print(f"   Returned history rows: {len(rows)}")
    if len(rows) < 80:
        print("ERROR: Endpoint responded, but fewer than 80 daily rows were returned.")
        print(json.dumps(history_payload, ensure_ascii=False)[:1500])
        sys.exit(3)

    print("SUCCESS: GitHub Actions can reach the CDN search and history endpoints.")
    print(f"Sample symbol: {match.get('lVal18AFC')} | InsCode: {ins_code} | rows: {len(rows)}")

if __name__ == "__main__":
    main()
