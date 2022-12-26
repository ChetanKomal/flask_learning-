from flask import Flask,jsonify,request,redirect, url_for
from flask_restful import Resource,Api,reqparse
import time
import warnings
import docx
import csv
import docx2txt
import openpyxl
import torch
import pandas as pd
from openpyxl import load_workbook
import threading

project_name = ""
guid= ""
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("project_name" , type=str , required=True , help="enter project name")
parser.add_argument("guid" , type=str , required=True , help="enter guid")

class get_guid_project(Resource):
    def __init__(self):
        self.__project_name = parser.parse_args().get('project_name',None)
        self.__guid = parser.parse_args().get('guid',None)
    def get(self): 
        project_name = self.__project_name
        guid = self.__guid
        return {"project_name":project_name,"guid":guid}

api.add_resource(get_guid_project,"/get_name_id/")

@app.route("/info")
def inde():
   user_agent = request.headers.get('User-Agent')
   return jsonify({"user_agent":user_agent,"ip":request.remote_addr})

#passing a variable in the url
@app.route("/<string:name>/<string:name2>")
def index(name,name2):
    return f"{name,name2}"

#passing a json object
@app.route("/hello")
def index2():
    data = {
        "message": "Hello World!"
    }
    return jsonify(data)

#redirecting to another page
@app.route("/admin")
def index3():
    return redirect(url_for("index2"))


 

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.3", port=5000)