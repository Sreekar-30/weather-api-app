import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENWEATHER_API_KEY")
print("KEY:", repr(key))
if not key:
    print("No API key detected (None or empty).")
else:
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                         params={"q":"Bengaluru,IN","appid":key})
        print("STATUS:", r.status_code)
        # Try printing JSON (if any)
        try:
            print("JSON:", r.json())
        except Exception:
            print("TEXT:", r.text)
    except Exception as e:
        print("Request error:", e)
