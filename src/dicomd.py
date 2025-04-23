#!/usr/bin/env python3

import json, pydicom, os, wand, re
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
@app.route(apiVersion + '/upload/<path:path>', methods=['POST'])
def upload(path):
  if 'file' not in request.files:
    resp = jsonify({'message': 'No file part in the request.  You need pass in a file to upload.'})
    resp.status_code = 400
    return resp
    
  data = request.files['file']

  #FIXME: will this code ever run?  I don't think so, maybe empty filename?  test it?  A clinet could pass it along.
  if data.filename == '':
    resp = jsonify({'message': 'No file selected for uploading'})
    resp.status_code = 400
    return resp
    
  if data:
    #FIXME:  what if someone has something evil in filename.  I'm not sure this matters here.
#    filename = secure_filename(data.filename) 
    filename = secure_filename(rootDir + path) 
    if os.path.exists(rootDir + path):
      resp = jsonify({'message': 'file ' + path + ' already exists.  Please remove it first.'})
      resp.status_code = 400
      return resp
    os.makedirs(os.path.dirname(rootDir + path), exist_ok=True)
    data.save(rootDir + path)
    try:
      ds = pydicom.dcmread(rootDir + path)
    except:
      os.remove(rootDir + path)
      resp = jsonify({'message': 'Uploaded file ' + path + ' does not appear to be a valid dicom file.  Please troubleshoot and re-upload it.'})
      resp.status_code = 400
      return resp

    resp = jsonify({'message': 'File ' + path + ' successfully uploaded'})
    resp.status_code = 201
    return resp
    
  resp.status_code = 400
  return resp

@app.route(apiVersion + '/remove/<path:path>', methods=['DELETE'])
def remove(path):
  #FIXME: program never cleans up its directory structure.
  if os.path.exists(rootDir + path):
    os.remove(rootDir + path)
    #try to clean up the image incase it got created
    if os.path.exists(rootDir + path + '.png'):
      os.remove(filename=rootDir + path + '.png')
    resp = jsonify({'message': 'File ' + path + ' was removed.'})
    resp.status_code = 200
    return resp
  resp = jsonify({'message': 'File ' + path + ' does not exist.  It may have already been removed.'})
  resp.status_code = 400
  return resp


@app.route(apiVersion + '/tags/<path:path>', methods=['GET'])
def tag(path):
  tag = request.args.get('tag')

  try:
    ds = pydicom.dcmread(rootDir + path)
  except:
    resp = jsonify({'message': 'File ' + path + ' has not been uploaded yet.  Please upload a file first'})
    resp.status_code = 400
    return resp

#  if not tag:
#    resp = jsonify({'message': 'No tag part in the request'})
#    resp.status_code = 400
#    return resp
#  if tag == '*':

  # if no tag specified, display all tags options
  if not tag:
    taglist = []
    for x in ds:
      taglist.append(str(x.tag)[1:-1].replace(" ", ""))
    resp = jsonify({'message': 'These are the avalable tags for the uploaded file.  Please append it to the end after the tag in your url.  EG ?tag=0010,0001',
                    'avalable tags': taglist
                   })
    resp.status_code = 200
    return resp
  else:
    tag = tag.lower()

    if re.match('^[0-9a-f]{4}\,[0-9a-f]{4}$', tag):
      formattedTag = '0x' + tag[0:4] + tag[5:]
    else:
      resp = jsonify({'message': 'invalid tag.  Tags have to be two sets 4 hex charicters, seporated by a comma.  EG ?tag=0010,0001' })
      resp.status_code = 400
      return resp
    
  resp = jsonify(ds[formattedTag].to_json())
  resp.status_code = 200
  return resp

@app.route(apiVersion + '/image/<path:path>', methods=['GET'])
def getImage(path):
  #FIXME: images maybe dark?  I'm not sure.  I don't want to increas the gain blind
  #FIXME: this code never removes the created image files
  try:
    ds = pydicom.dcmread(rootDir + path)
  except:
    resp = jsonify({'message': 'File ' + path + ' has not been uploaded yet.  Please upload it first.'})
    resp.status_code = 400
    return resp
  try:
    with Image(filename=rootDir + path) as img:
      img.save(filename=rootDir + path + '.png')
    return send_file(rootDir + path + '.png', mimetype='image/png')
  except:
    resp = jsonify({'message': 'Something went wrong in converting the image ' + path + ',  The uploaded file may not even be an image.  Please investigate.'})
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


