from flask import Flask,jsonify,request,redirect, url_for
import time
import warnings
import docx
import csv
import docx2txt
import openpyxl
import torch
from transformers import T5ForConditionalGeneration,T5Tokenizer
import pandas as pd
from openpyxl import load_workbook
from pipelines import pipeline



app = Flask(__name__)

#passing a variable in the url
@app.route("/<name>")
def index(name):
    return "Hello World! from {}".format(name)

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


@app.route("/qna")
def generate_qna():
    st=time.time()
    nlp = pipeline("question-generation")


    model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_paraphraser')
    tokenizer = T5Tokenizer.from_pretrained('t5-base')
    device = torch.device("cpu")
    model = model.to(device) 


    file = open("ip.txt","r")
    str_input_txt = file.read()
    print("generating qna pair.....")
    q_lst = nlp(str_input_txt) 
    print("qna pair generated")
    print(q_lst)
    et=time.time()
    return jsonify({"time":et-st,"qna":q_lst})


if __name__ == "__main__":
    app.run(debug=True)