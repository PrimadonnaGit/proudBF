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

@app.route('/seoulbitz')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000, debug=True)
