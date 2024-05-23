import io
from base64 import encodebytes
from datetime import datetime

import qrcode
import requests
from flask import Flask, render_template
from flask_moment import Moment

from client import Client
from config import get_config

BASE_SHARE_URL = "https://share.toogoodtogo.com"
LATITUDE = 40.6913289
LONGITUDE = -73.985069
RADIUS = 5

items = None


def get_osm_directions(store_longitude, store_latitude):
    config = get_config()
    api_key = config["OSM_API_KEY"]
    headers = {
        "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
    }
    response = requests.get(
        f"https://api.openrouteservice.org/v2/directions/foot-walking?api_key={api_key}&start={LONGITUDE},{LATITUDE}&end={store_longitude},{store_latitude}",
        headers=headers,
    )
    return response


def fetch_items():
    global items

    tgtg_client = Client()

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

        item["pickup_interval"]["start"] = datetime.fromisoformat(item["pickup_interval"]["start"])
        item["pickup_interval"]["end"] = datetime.fromisoformat(item["pickup_interval"]["end"])
        item["purchase_end"] = datetime.fromisoformat(item["purchase_end"])
        store_longitude = item["pickup_location"]["location"]["longitude"]
        store_latitude = item["pickup_location"]["location"]["latitude"]
        osm_response = get_osm_directions(store_longitude=store_longitude, store_latitude=store_latitude)
        item["osm_geojson"] = osm_response.json()


def create_app():
    global items

    app = Flask(__name__)
    moment = Moment(app)

    fetch_items()

    @app.route("/")
    def tgtg_main():
        return render_template("index.html", items=items)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8080)
