import csv
import math
import os

from flask import Flask, render_template, request

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_csv(filename):
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ZIPCODES = load_csv("zipcodes.csv")
FOOD_BANKS = load_csv("food_banks.csv")
PANTRIES = load_csv("pantries.csv")


def find_zip(zip_code):
    for row in ZIPCODES:
        if row["zip"] == zip_code:
            return row
    return None


def distance_miles(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    r = 3958.8  # radius of Earth in miles
    lat1_r, lat2_r = math.radians(lat1), math.radians(lat2)
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(d_lon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(a))


def get_nearby_locations(lat, lon):
    locations = []

    for bank in FOOD_BANKS:
        dist = distance_miles(lat, lon, bank["lat"], bank["lon"])
        locations.append({
            "type": "Regional Food Bank",
            "name": bank["name"],
            "address": f"{bank['address']}, {bank['city']}, {bank['state']} {bank['zip']}",
            "phone": bank["phone"],
            "hours": bank["hours"],
            "distance": round(dist, 1),
            "lat": float(bank["lat"]),
            "lon": float(bank["lon"]),
        })

    for pantry in PANTRIES:
        dist = distance_miles(lat, lon, pantry["lat"], pantry["lon"])
        locations.append({
            "type": "Local Pantry",
            "name": pantry["name"],
            "address": f"{pantry['address']}, {pantry['city']}, {pantry['state']} {pantry['zip']}",
            "phone": pantry["phone"],
            "hours": pantry["hours"],
            "distance": round(dist, 1),
            "lat": float(pantry["lat"]),
            "lon": float(pantry["lon"]),
        })

    locations.sort(key=lambda loc: loc["distance"])
    return locations


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results")
def results():
    zip_code = request.args.get("zip", "").strip()

    zip_info = find_zip(zip_code)
    if not zip_info:
        return render_template("results.html", error=True, zip_code=zip_code)

    locations = get_nearby_locations(zip_info["lat"], zip_info["lon"])

    return render_template(
        "results.html",
        error=False,
        zip_code=zip_code,
        city=zip_info["city"],
        locations=locations,
        user_lat=float(zip_info["lat"]),
        user_lon=float(zip_info["lon"]),
    )


if __name__ == "__main__":
    app.run(debug=True)