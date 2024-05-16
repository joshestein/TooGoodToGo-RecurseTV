from datetime import datetime
import io
from base64 import encodebytes

import qrcode
from flask import Flask, render_template
from flask_moment import Moment
from client import Client

app = Flask(__name__)

moment = Moment(app)

BASE_SHARE_URL = "https://share.toogoodtogo.com"
LATITUDE = 40.69
LONGITUDE = -73.98
RADIUS = 5


def make_qr_code(item_id: str):
    qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage)
    qr.add_data(f"{BASE_SHARE_URL}/item/{item_id}")
    qr.make(fit=True)
    return qr.to_string(encoding="unicode")


@app.route("/")
def tgtg_main():
    tgtg_client = Client()

    items = tgtg_client.client.get_items(
        favorites_only=False, latitude=LATITUDE, longitude=LONGITUDE, radius=RADIUS, with_stock_only=True, page_size=50
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


    return render_template("index.html", items=items)


if __name__ == "__main__":
    app.run()
