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
import threading 


app = Flask(__name__)

def gen_qna():
    print("qna generation started on thread:" + threading.current_thread().name)
    print(threading.current_thread().name)
    return print("generating qna pair.....")

@app.route("/")
def index():
    threading.Thread(target=gen_qna).start()
    return "Hello World!"






if __name__ == "__main__":
    app.run(debug=True)