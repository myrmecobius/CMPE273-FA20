from app import app
import flask
from flask import request
from sqlitedict import SqliteDict
import qrcode
import io

bookmark_dict = SqliteDict('./my_db.sqlite', autocommit=True)

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/api/bookmarks', methods=["GET", "POST"])
def set_bookmark():
    if request.method == "POST":
        name = request.form['name']
        url = request.form['url']
        description = request.form['description']
        bId = name
        if bookmark_dict.get(bId, False):
            return {
                "reason": "The given URL already existed in the system."
            }, 400
        else:
            payload = {"name": name,"url": url,"description": description,"id":name,"count":0}
            bookmark_dict[bId] = payload
            return {
                "id": f"{bId}"
            }, 201
    else:
        return "Nothing Posted"

@app.route('/api/bookmarks/<gid>', methods=['GET','DELETE'])
def get_bookmark(gid):
    if bookmark_dict.get(gid, False):
        if request.method == "GET":
            d = bookmark_dict[gid]
            d["count"] += 1
            bookmark_dict[gid] = d
            del d['count']
            return d
        else:
            del bookmark_dict[gid]
            return "No Content", 204
    else:
        return "Not found", 404

@app.route('/api/bookmarks/<gid>/qrcode')
def getQRcode(gid):
    print(bookmark_dict.get(gid, "gid doesn't exist"))
    if bookmark_dict.get(gid, False):
        img_buf = io.BytesIO()
        url = bookmark_dict[gid]["url"]
        img = qrcode.make(url)
        img.save(img_buf)
        img_buf.seek(0)
        return flask.send_file(img_buf, mimetype='image/png')
    else:
        return "Not found", 404

@app.route("/api/bookmarks/<gid>/stats")
def getStats(gid):
    if bookmark_dict.get(gid, False):
        c = str(bookmark_dict[gid]["count"])
        if request.if_none_match.contains(str(c)):
            return "", 304
        else:
            return str(c), 200, {"ETag":c}
    else:
        return "Not found", 404

@app.route('/keys')
def printKeys():
    keyStr = ''
    for key in bookmark_dict.keys():
        keyStr += str(key) + "\n"
    return keyStr

@app.route('/clearKeys')
def clearKeys():
    for key in bookmark_dict.keys():
        del bookmark_dict[key]
    return "Keys deleted"