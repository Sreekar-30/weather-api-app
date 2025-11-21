from flask import Flask, render_template, request, jsonify
import os, requests, time
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('OPENWEATHER_API_KEY')
CACHE = {}
CACHE_TTL = 300

def fetch_weather(city_query):
    if not API_KEY:
        return {'error': 'OPENWEATHER_API_KEY not set.'}
    key = city_query.strip().lower()
    now = time.time()

    # Cache
    if key in CACHE:
        ts, data = CACHE[key]
        if now - ts < CACHE_TTL:
            data['_cached'] = True
            return data

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_query, "appid": API_KEY, "units": "metric"}

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        if data.get("cod") != 200:
            return {"error": data.get("message")}

        result = {
            "city": data["name"],
            "country": data["sys"].get("country"),
            "temp_c": data["main"].get("temp"),
            "feels_like_c": data["main"].get("feels_like"),
            "humidity": data["main"].get("humidity"),
            "pressure": data["main"].get("pressure"),
            "description": data["weather"][0].get("description"),
            "wind_m_s": data["wind"].get("speed")
        }

        CACHE[key] = (now, result)
        return result

    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None
    cached = False

    if request.method == "POST":
        city = request.form.get("city", "")
        if city:
            data = fetch_weather(city)
            if "error" in data:
                error = data["error"]
            else:
                weather = data
                cached = data.get("_cached", False)

    return render_template("index.html", weather=weather, error=error, cached=cached)

@app.route("/api/weather")
def api_weather():
    city = request.args.get("q", "")
    if not city:
        return {"error": "missing q param"}
    data = fetch_weather(city)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
