import io
import random
from base64 import encodebytes

import qrcode
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template
from flask_moment import Moment

from client import Client

BASE_SHARE_URL = "https://share.toogoodtogo.com"
LATITUDE = 40.6913289
LONGITUDE = -73.985069
RADIUS = 5

items = None

def get_random_theme():
    themes = ['cheese', 'loops', 'pie', 'salmon']
    return random.choice(themes)


def get_osrm_directions(store_longitude, store_latitude):
    response = requests.get(
        f"http://router.project-osrm.org/route/v1/foot/{LONGITUDE},{LATITUDE};{store_longitude},{store_latitude}?geometries=geojson"
    )
    return response


def fetch_items(tgtg_client: Client):
    global items

    items = tgtg_client.client.get_items(
        favorites_only=False, latitude=LATITUDE, longitude=LONGITUDE, radius=RADIUS, with_stock_only=True, page_size=20
    )

    # TODO: only extract important information to send to the client
    # TODO: either delete keys or buildup new list

    for item in items:
        item_id = item["item"]["item_id"]
        url = f"{BASE_SHARE_URL}/item/{item_id}"
        qr_img = qrcode.make(url)
        qr_bytes = io.BytesIO()
        qr_img.save(qr_bytes, format=qr_img.format)
        item["qrcode"] = encodebytes(qr_bytes.getvalue()).decode("ascii")

        store_longitude = item["pickup_location"]["location"]["longitude"]
        store_latitude = item["pickup_location"]["location"]["latitude"]

        osrm_response = get_osrm_directions(store_longitude=store_longitude, store_latitude=store_latitude)
        if osrm_response.status_code == 200:
            osrm_response = osrm_response.json()
            item["osrm_geojson"] = osrm_response["routes"][0]["geometry"]
            item["osrm_duration"] = osrm_response["routes"][0]["duration"]


def create_app():
    global items

    app = Flask(__name__)
    moment = Moment(app)
    tgtg_client = Client()

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=fetch_items, args=[tgtg_client], trigger="interval", minutes=10)
    scheduler.start()

    fetch_items(tgtg_client)

    @app.route("/")
    def tgtg_main():
        return render_template("index.html", items=items, theme=get_random_theme())

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
