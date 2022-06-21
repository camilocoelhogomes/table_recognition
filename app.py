from unicodedata import name
from flask import Flask, Response, request, send_file
from flask_cors import CORS, cross_origin
import base64
import os
from textract import *

app = Flask(__name__)
CORS(app, support_credentials=True)


@app.route('/', methods=['POST'])
@cross_origin(support_credentials=True)
def getImage():
    body = request.get_json()['img']
    base64_img = body[(body.find(',')+1):]
    imgdata = base64.b64decode(base64_img)
    base64_format = body[(body.find('image/')+6):body.find(';')]
    filename = 'outuput.'+base64_format
    with open(filename, 'wb') as f:
        f.write(imgdata)
    with open(filename, 'rb') as binary_file:
        binary_file_data = binary_file.read()
        main(binary_file_data)

    final_file = open('output.csv', 'rb')
    os.remove(filename)
    os.remove('output.csv')
    return send_file(final_file, download_name="output.csv", as_attachment=True, mimetype="text/csv")


app.run()
