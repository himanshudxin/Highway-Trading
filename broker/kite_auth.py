import json, os, pyotp, requests
from kiteconnect import KiteConnect

def auto_login():
    with open(os.path.expanduser("~/.kite_credentials.json"), "r") as f: c = json.load(f)
    s = requests.Session()
    r = s.post("https://kite.zerodha.com/api/login", data={"user_id": c["user_id"], "password": c["password"]})
    totp = pyotp.TOTP(c["totp_secret"]).now()
    s.post("https://kite.zerodha.com/api/twofa", data={"user_id": c["user_id"], "request_id": r.json()["data"]["request_id"], "twofa_value": totp})
    req_token = s.get(f"https://kite.zerodha.com/connect/login?api_key={c['api_key']}&v=3").url.split("request_token=")[1].split("&")[0]
    data = KiteConnect(api_key=c["api_key"]).generate_session(req_token, api_secret=c["api_secret"])
    with open(os.path.expanduser("~/.kite_session.json"), "w") as f: json.dump({"api_key": c["api_key"], "access_token": data["access_token"]}, f)
    print("Kite token refreshed successfully.")

if __name__ == "__main__": auto_login()
