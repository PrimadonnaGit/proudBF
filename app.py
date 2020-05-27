from flask import Flask, request, render_template, send_from_directory, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES

import os
import csv
import requests
import subprocess

app = Flask(__name__)

photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img/uploads/'
configure_uploads(app, photos)

def load_csv(filename):
    data = []
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        for r in reader:
            data.append({
                'title': r[1],
                'addr_s': r[2], 
                'addr': r[3],
                'like': r[4],
                'insta': r[5],
                'img': r[6]
                })
    return data

@app.route('/getData', methods= ['POST'])
def getData():
    data = load_csv('static/seoulbitz(05_26).csv')
    return jsonify({
        "data" : data
    })

@app.route('/seoulbitz')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=81, debug=True)
