import requests
from flask import Flask, render_template, request
from pprint import pprint 
import os, uuid, sys
import datetime
import json
from azure.storage.blob import BlobClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials


# Instantiate a new ContainerClient


app = Flask(__name__)

#
#  set some variables
#
local_path="upload"
container = "upload"
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
computervision_key = os.getenv("COMPUTERVISION_SUBSCRIPTION_KEY")
computervision_location = os.environ.get("COMPUTERVISION_LOCATION", "eastus")
container_name = "upload"
#storage_account = os.getenv("STORAGE_ACCOUNT")
storage_account = os.getenv("STORAGE_ACCOUNT")

#  set the region to use and the url/resource_path for the API nethond
#


@app.route('/')
def index():
  return render_template("index.html") 

@app.route("/about")
def about():
  req = requests.get('https://github.com/timeline.json')
  treq = req.url 
  resp = req.json()
  return render_template("about.html", url=treq, result=resp)

@app.route("/vision")
def vision():

  print("in vision , filename is " + current_file)
 
 

  return render_template("vision.html", url=endpoint, result=curent_file, pic=local_file_name)

  
@app.route('/selcvfile')
def selcvfile():
  return render_template("selcvfile.html") 
  
@app.route("/upload", methods = {'GET', 'POST'})
def upload():
  
  if request.method == 'POST':
     
     req_file = request.files['file']
     tstamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
     local_file_name = tstamp + "-" + req_file.filename
     req_file.save(os.path.join(local_path, local_file_name))
     upfile = os.path.join(local_path, local_file_name) 

     blob_client = BlobClient.from_connection_string(conn_str=connection_string,
      container_name=container_name, blob_name=local_file_name)
     with open(upfile, "rb") as data:
                blob_client.upload_blob(data, blob_type="BlockBlob")

# Now we send it off for analysis
 
     client = ComputerVisionClient(
        endpoint="https://" + computervision_location + ".api.cognitive.microsoft.com/",
        credentials=CognitiveServicesCredentials(computervision_key)
     )

     with open(upfile, "rb") as image_stream:
           image_analysis = client.analyze_image_in_stream(
           image=image_stream,
           visual_features=[
                VisualFeatureTypes.image_type,  # Could use simple str "ImageType"
                VisualFeatureTypes.faces,      # Could use simple str "Faces"
                VisualFeatureTypes.categories,  # Could use simple str "Categories"
                VisualFeatureTypes.objects,      # Could use simple str "Color"
                VisualFeatureTypes.tags,       # Could use simple str "Tags"
                VisualFeatureTypes.description  # Could use simple str "Description"
            ]     
        )
     
     if (len(image_analysis.objects) == 0):
         print("No objects detected.")
         objs="No Objects detected"
     else: 
         objs = [] 
         for tag in image_analysis.objects:
             print("'{}' with confidence {:.2f}%".format(tag.object_property, tag.confidence * 100))
             objs.append("'{}' with confidence {:.2f}%".format(tag.object_property, tag.confidence * 100)) 
     
     if (len(image_analysis.description.captions) == 0):
         print("No captions detected.")
     else:
        for caption in image_analysis.description.captions:
            desc = []
            tstr = "'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100)
            desc.append(tstr)
            print(tstr) 

     if (len(image_analysis.faces) == 0):
         print("No faces detected.")
         facs="No Objects detected"
     else: 
         facs = [] 
         for face in image_analysis.faces:
             #print("'{}' with confidence {:.2f}%".format(tag.object_property, tag.confidence * 100))
             facs.append("Gender:  {}  Age: {:d}".format(face.gender, face.age)) 
             print( facs )

     #desc = image_analysis.description.captions[0].text
     img = "https://" + storage_account + ".blob.core.windows.net/" + container_name + "/" + local_file_name
     
     os.remove(upfile)
 
  return render_template("upload.html",file=local_file_name,
   container=container,descr=desc,pic=img,object=objs,faces=facs)
  
@app.route('/listcont')
def listcont():

  block_blob_service = BlockBlobService(account_name=storage_account, account_key=account_key)
  list = block_blob_service.list_blobs(container_name)
  return render_template("listcont.html",container=container_name,list=list,account=storage_account)   

if __name__ == '__main__':
  app.run()
