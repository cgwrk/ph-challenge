#!/usr/bin/env python3

#FIXME, remove un-needed/wanted libs
import json, pydicom, os, PIL, wand
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from wand.image import Image

#FIXME.  It is trusted that the file is what it says it is.  Some form of check to see if it is what it says it is maybe nice.
#FIXME.  check local permissons when making file
#FIXME.  write api and build docs
#FIXME.  api does not catch or handle errors well and
#FIXME.  There likely is a maximum length on file that can be uploaded.  I don't know what that is.
#FIXME.  What if 2 clients use this api at once?  chaos.  some form of Auth?

port=8080
rootDir="/data/"
apiVersion='/v1'

#As I am only handling 1 file at a time, I'll hard code it's internal path.
internalFile = rootDir + 'current_dicom_file.dcm'
internalFileImg = rootDir + 'current_dicom_file.png'

app = Flask(__name__)

#FIXME.  What if the file is already there?  Protect? step on?
@app.route(apiVersion + '/upload', methods=['POST'])
def upload():
  if 'file' not in request.files:
    resp = jsonify({'message': 'No file part in the request'})
    resp.status_code = 400
    return resp
    
  file = request.files['file']

  if file.filename == '':
    resp = jsonify({'message': 'No file selected for uploading'})
    resp.status_code = 400
    return resp
    
  if file:
#FIXME.  what if someone has something evil in filename
    filename = secure_filename(file.filename) 
    file.save(internalFile)

#FIXME: DEBUG
    ds = pydicom.dcmread(internalFile)
    for e in ds:
      print(f'DEBUG: Tags: {e}')

    resp = jsonify({'message': 'File successfully uploaded'})
    resp.status_code = 201
    return resp
    
  resp.status_code = 400
  return resp

#FIXME: document this.  should return all tags if none give
@app.route(apiVersion + '/tag/<tag>', methods=['GET'])
def tag(tag):
  if not tag:
    resp = jsonify({'message': 'No tag part in the request'})
    resp.status_code = 400
    return resp
  ds = pydicom.dcmread(internalFile)
#FIXME match tag pattern 1234,5678
  formattedTag = '0x' + tag[0:4] + tag[5:]
  resp = jsonify(ds[formattedTag].to_json())
  resp.status_code = 200
  return resp

@app.route(apiVersion + '/image', methods=['GET'])
def getImage():
#FIXME:  What if this is not an image?
  with Image(filename=internalFile) as img:
    img.save(filename=internalFileImg)
  return send_file(internalFileImg, mimetype='image/png')


@app.route('/')
def index():
#FIXME, output usage
  return json.dumps({'usage': 'output a usage msg'})


app.run(host='0.0.0.0', port=port)


