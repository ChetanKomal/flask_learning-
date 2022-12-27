import time
st = time.time()
from flask_restful import Resource,Api,reqparse
from flask import Flask,jsonify,request,redirect, url_for,render_template
import PyPDF2
import warnings
import nltk
import os
import urllib.request
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from nltk.tokenize import blankline_tokenize
from PyPDF2 import PdfReader
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
import table_upload
from pdfCropMargins import crop
import threading
import wget
from dotenv import load_dotenv
import requests
load_dotenv()


global_path = "C:\\Users\\Hp\\Desktop\\flask learning\\"
project_name = ""
guid = ""


max_len = 500

conn_str = os.getenv("CONN_STR")
container_name = "samplecontiner"
storage_acc_name = "qnai"
storage_acc_key = os.getenv("STR_ACC_KEY")

warnings.filterwarnings("ignore")
nlp = pipeline("question-generation")
model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_paraphraser')
tokenizer = T5Tokenizer.from_pretrained('t5-base')
device = torch.device("cpu")
model = model.to(device)

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
        global  project_name
        global guid 
        project_name = self.__project_name
        guid = self.__guid
        return f"{project_name} {guid}"


api.add_resource(get_guid_project,"/get_name_id/")


#reading blob 
def read_blob(project_name,guid):
    url = f"https://qnai.blob.core.windows.net/{project_name}/{guid}/2.pdf"
    response = requests.get(url)
    open(f"{guid}.pdf", "wb").write(response.content)


#function for range of pages to read from pdf file.    
def page_range():
    request_url = urllib.request.urlopen(f"https://qnai.blob.core.windows.net/{project_name}/{guid}/from_to.txt")
    values = request_url.read().decode('utf-8')
    a = int(values.split(" ")[0])
    b = int(values.split(" ")[1])
    return a,b  

#uploading output to Blob storage
def upload_blob(file_path , file_name):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)

    #for uploading output.csv
    with open(file_path,'rb') as data:
        blob_client.upload_blob(data)
    data.close()
    print("uploaded to blob")

#function for writing qnas without paraphrasing into csv file.(output_without_paraphrasing.csv)
def write_csv(op_list):
      f = open('output_without_paraphrasing.csv', 'a',newline='')
      writer = csv.writer(f)
      for i in op_list:
       data = [i['question'],i['answer']]    
       writer.writerow(data)
      f.close()

#function to write qnas with paraphrasing into csv file.(output.csv)
def pphrase(q_lst):     
    for qa in q_lst:
     sentence = qa['question']     
     text =  "paraphrase: " + sentence + " </s>"
     encoding = tokenizer.encode_plus(text,pad_to_max_length=True, return_tensors="pt")
     input_ids, attention_masks = encoding["input_ids"].to(device), encoding["attention_mask"].to(device)
     beam_outputs = model.generate(
         input_ids=input_ids, attention_mask=attention_masks,
         do_sample=True,
         max_length=256,
         top_k=120,
         top_p=0.98,
         early_stopping=True,
         num_return_sequences=10
     )
     final_outputs =[]
     for beam_output in beam_outputs:
         sent = tokenizer.decode(beam_output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
         if sent.lower() != sentence.lower() and sent not in final_outputs:
             final_outputs.append(sent)

     f1 = open(f'{global_path}output.csv', 'a',newline='')
     writer = csv.writer(f1)
     data = [qa['question'],qa['answer']]
     for i in final_outputs:
       data = [i,qa['answer']]    
       writer.writerow(data)
    f1.close()

#function for reading the pdf file and extracting text from it page by page.
def read_page(a,b):
    reader = PdfReader(f"{guid}_cropped.pdf")
    pdf_txt_object = open("ip.txt", "a")
    for i in range(a,b):
     page = reader.pages[i]
     text_body = page.extract_text()
     pdf_txt_object.write(text_body)
    pdf_txt_object.close()

#main function for qna generation
def gen_qna():
  
  print(threading.current_thread().name, 'Starting')
  #croping pdf pages
  crop(["-u", "-p", "10.0", "-m4", "0", "2", "0", "3","-prw","1.0","1.0","1.0","1.0", "-ap4", "52.0", "30.0", "50.0", "62.0"  ,f"{guid}.pdf"])
  print("cropping successfull")

  #checking the files if they are empty or contain data from previous run.
  if os.stat(f"{global_path}ip.txt").st_size != 0:
      open(f"{global_path}ip.txt","w").close() 

  open(f"{global_path}output.csv","w").close()
  open(f"{global_path}output_without_paraphrasing.csv","w").close()

  read_page(page_range()[0],page_range()[1])
  
  read_txt = open("ip.txt", "r")
  content = read_txt.read()

  ai_blank = blankline_tokenize(content)
  ai_blank_copy = ai_blank

  
  for i in range(0,len(ai_blank_copy)-2):
     x = ai_blank_copy[i]
     while len(x) < 500:
       if len(x) < 500:
         ai_blank_copy.pop(i)
         x = x + " " + ai_blank_copy[i]
       else:
         break
     
     str_input_txt = x
     print("generating qna pair.....")
     q_lst = nlp(str_input_txt)


     write_csv(q_lst)   
     print("qna pair generated")
     #max_len = 500

     print(q_lst)

     print("paraphrasing questions.....")
     pphrase(q_lst)
     print("paraphrasing completed")
   


     print("<================================================================>")
  upload_blob(f"{global_path}output.csv",f"{guid}/output.csv")
  upload_blob(f"{global_path}output_without_paraphrasing.csv",f"{guid}/output_without_paraphrasing.csv")
  upload_blob(f"{global_path}ip.txt",f"{guid}/ip.txt")
  os.remove(f"{guid}_cropped.pdf")
  os.remove(f"{guid}.pdf")
  open(f"{global_path}output.csv","w").close()
  open(f"{global_path}output_without_paraphrasing.csv","w").close()
     

@app.route("/")
def home():
    return f"{project_name} {guid}"

@app.route("/qna")
def index():
    with app.app_context():
     if len(project_name) == 0 and len(guid) == 0:
        return "project_name and guid not found , maybe call \"/get_name_id/?project_name=project_name&guid=guid\" this url first "   
     else:
      read_blob(project_name,guid)
      threading.Thread(target=gen_qna).start()
     return "ALL STEPS DONE"    

@app.route("/info")
def info():
    return "info page"



if __name__ == "__main__": 
    app.run(debug=True, host="192.168.1.3")