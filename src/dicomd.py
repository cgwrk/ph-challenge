#!/usr/bin/env python3

import json, pydicom, os, wand
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from wand.image import Image

#FIXME.  It is trusted that the file is what it says it is.  Some form of check to see if it is what it says it is maybe nice.
#FIXME.  Check local permissons when making file
#FIXME.  There likely is a maximum length on file that can be uploaded.  I don't know what that is.
#FIXME.  What if 2 clients use this api at once?  chaos.  Some form of Auth and tracy by user? Path included in filename would work, but outside my ability at the moment.

#FIXME.  write api and build docs

port=8080
rootDir="/data/"
apiVersion='/api/v1'

#As I am only handling 1 file at a time, I'll hard code it's internal path.  This is not ideal.
internalFile = rootDir + 'current_dicom_file.dcm'
internalFileImg = rootDir + 'current_dicom_file.png'

app = Flask(__name__)

# I am unsure if uploading a file like this is valid Rest. 
# base64 encoding the file at the client and decoding it at the server maybe more valid, but would have more overhead on client and server.
@app.route(apiVersion + '/upload', methods=['POST'])
def upload():
  if 'file' not in request.files:
    resp = jsonify({'message': 'No file part in the request'})
    resp.status_code = 400
    return resp
    
  file = request.files['file']

#FIXME: will this code ever run?  I don't think so, maybe empty filename?  test it
  if file.filename == '':
    resp = jsonify({'message': 'No file selected for uploading'})
    resp.status_code = 400
    return resp
    
  if file:
    #FIXME:  what if someone has something evil in filename.  I'm not sure this matters here.
    filename = secure_filename(file.filename) 
    if os.path.exists(internalFile):
      resp = jsonify({'message': 'file already exists.  Please remove it first.'})
      resp.status_code = 400
      return resp
    file.save(internalFile)
    try:
      ds = pydicom.dcmread(internalFile)
    except:
      os.remove(internalFile)
      resp = jsonify({'message': 'Uploaded file does not appear to be a valid dicom file.  Please troubleshoot and re-upload it.'})
      resp.status_code = 400
      return resp

#FIXME: return link to file, like successfully created object?
    resp = jsonify({'message': 'File successfully uploaded'})
    resp.status_code = 201
    return resp
    
  resp.status_code = 400
  return resp

#maybe it would be better to put this under the upload url
@app.route(apiVersion + '/remove', methods=['DELETE'])
def remove():
  os.remove(internalFile)
  resp = jsonify({'message': 'removed uploaded file.'})
  resp.status_code = 200
  return resp

@app.route(apiVersion + '/tag', methods=['GET'], defaults={'tag': '*'})
@app.route(apiVersion + '/tag/<tag>', methods=['GET'])
def tag(tag):
  try:
    ds = pydicom.dcmread(internalFile)
  except:
    resp = jsonify({'message': 'No file has been uploaded yet.  Please upload a file first'})
    resp.status_code = 400
    return resp

  if not tag:
    #I pretty sure this code won't run ever.. I have default value now
    resp = jsonify({'message': 'No tag part in the request'})
    resp.status_code = 400
    return resp
  if tag == '*':
    print("FixThis.  show All Tags")
    taglist = []
    for x in ds:
      taglist.append(str(x.tag)[1:-1].replace(" ", ""))
#FIXME.  As a rest api, I'm pretty sure it's supposed to return links to the proper url, not just text.
    resp = jsonify({'Improper usage': 'These are the avalable tags for the uploaded file.  Please append it to the end after the tag in your url.  eg /v1/tag/0010,0001',
                    'avalable tags': taglist
                   })
    resp.status_code = 200
    return resp

  # I have a tag, format it the way the api wants it
  formattedTag = '0x' + tag[0:4] + tag[5:]
  resp = jsonify(ds[formattedTag].to_json())
  resp.status_code = 200
  return resp

@app.route(apiVersion + '/image', methods=['GET'])
def getImage():
  try:
    ds = pydicom.dcmread(internalFile)
  except:
    resp = jsonify({'message': 'No file has been uploaded yet.  Please upload a file first'})
    resp.status_code = 400
    return resp
  try:
    with Image(filename=internalFile) as img:
      img.save(filename=internalFileImg)
    return send_file(internalFileImg, mimetype='image/png')
  except:
    resp = jsonify({'message': 'Something went wrong in converting the image.  The uploaded file may not even be an image.  Please investigate.'})
    resp.status_code = 400
    return resp

@app.route('/')
def index():
#FIXME, output better usage
  return json.dumps({'endpoints': [apiVersion + "upload",
                                  apiVersion + "tag",
                                  apiVersion + "image"]
                   })
# json.dumps({'endpoints': apiVersion + 'upload'})
# Endpoints

#FIXME, just for testing, not prod.
app.run(host='0.0.0.0', port=port, debug=True)


