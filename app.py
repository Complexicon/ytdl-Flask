from __future__ import unicode_literals
from flask import abort, Flask
from markupsafe import escape
from flask import jsonify
from flask_cors import CORS
import urllib
import youtube_dl

app = Flask(__name__)
CORS(app)
ydl = youtube_dl.YoutubeDL()
# init youtube-dl
ydl.extract_info("https://www.youtube.com/watch?v=2-Y2yWYnn7U", download=False)


def decodeVid(video):
    dl = {}
    dl["id"] = video["id"]
    dl["thumburl"] = video["thumbnail"]
    dl["uploader"] = video["uploader"]

    if video["creator"] is not None and video["track"] is not None:
        dl["title"] = video["creator"].replace(
            ",", " &") + " - " + video["track"]
    else:
        dl["title"] = video["title"]

    for i in video["formats"]:
        if i["format_id"] == video["format_id"].split('+')[1]:
            if "DASH" not in i["format_note"]:
                dl["url"] = i["url"]
                return dl
            else:
                return None


@app.route('/get/<string:id>')
def get(id):
    ydl.params["geo_bypass_ip_block"] = "DE"
    info = ydl.extract_info(id, download=False)
    if "_type" not in info:
        return jsonify(decodeVid(info))
    else:
        abort(400)


@app.route('/query/<string:q>')
def query(q):
    info = ydl.extract_info("ytsearch10:" + q, download=False, process=False)
    result = []
    for e in info["entries"]:
        try:
            result.append(decodeVid(ydl.extract_info(e["id"], download=False)))
        except:
            pass
    return jsonify(result)


@app.route('/list/<string:id>')
def list(id):
    info = ydl.extract_info(id, download=False, process=False)
    result = []
    for e in info["entries"]:
        try:
            result.append(decodeVid(ydl.extract_info(e["id"], download=False)))
        except:
            pass
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
