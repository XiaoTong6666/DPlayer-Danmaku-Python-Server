import sys
import threading
import subprocess
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_pymongo import PyMongo
from urllib.parse import unquote

app = Flask(__name__)

CORS(app)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/danmaku'
mongo = PyMongo(app)

@app.route("/")
def hello():
    return "这是一个DPlayer的弹幕API<br><a href='https://github.com/XiaoTong6666/DPlayer-Danmaku-Python-Server'>项目地址</a>"
    
@app.route('/v3/', methods=['POST'])
def save_danmaku():
    data = request.json
    danmaku = {
        'text': data['text'],
        'color': data['color'],
        'time': data['time'],
        'videoId': data['id'],
        'author': data['author'],
        'type': data['type']
    }
    result = mongo.db.danmakus.insert_one(danmaku)
    danmaku['_id'] = str(result.inserted_id)
    return jsonify({'code': 0, 'data': danmaku})
    
def jsonify_no_nl(*args, **kwargs):
    kwargs.setdefault('indent', None)
    kwargs.setdefault('separators', (',', ':'))
    kwargs.setdefault('ensure_ascii', False)
    json_str = json.dumps(*args, **kwargs)
    response = Response(json_str, mimetype='application/json')
    response.headers['Content-Length'] = len(json_str)
    return response

@app.route('/v3/', methods=['GET'])
def get_danmaku():
    video_id = request.args.get('id')
    max_num = int(request.args.get('max', '3000'))
    danmakus = mongo.db.danmakus.find({'videoId': video_id}).limit(max_num)
    result = []
    for danmaku in danmakus:
        time = danmaku.get('time',0)
        type = danmaku.get('type',0)
        color = danmaku.get('color',16777215)
        author = danmaku.get('author','DPlayer')
        text = danmaku.get('text','')
        result.append([time,type,color,author,text])
    return unquote(jsonify_no_nl({'code': 0,'data': result}).data)
    
def start_flask(host):
    subprocess.call([sys.executable, sys.argv[0], host])
def main(argv):
    if argv:
        app.run(host=argv[0], port=200, debug=True)
    else:
        hosts = ["0.0.0.0", "::"]
        for host in hosts:
            thread = threading.Thread(target=start_flask, args=(host,))
            thread.start()
if __name__ == "__main__":
    main(sys.argv[1:])
