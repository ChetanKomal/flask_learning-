from flask import Flask,jsonify,request,redirect, url_for
import time
st = time.time()
import PyPDF2
import warnings
import nltk
import os
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
max_len = 500

warnings.filterwarnings("ignore")
nlp = pipeline("question-generation")
model = T5ForConditionalGeneration.from_pretrained('ramsrigouthamg/t5_paraphraser')
tokenizer = T5Tokenizer.from_pretrained('t5-base')
device = torch.device("cpu")
model = model.to(device)

app = Flask(__name__)


#reading blob 
def read_blob(blob):
    pass


#uploading output to Blob storage
def upload_blob():
    pass

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

     f1 = open('C:\\Users\\Hp\\Desktop\\flask learning\\output.csv', 'a',newline='')
     writer = csv.writer(f1)
     data = [qa['question'],qa['answer']]
     for i in final_outputs:
       data = [i,qa['answer']]    
       writer.writerow(data)
    f1.close()

#function for reading the pdf file and extracting text from it page by page.
def read_page(a,b):
    reader = PdfReader("2_cropped.pdf")
    pdf_txt_object = open("ip.txt", "a")
    for i in range(a,b):
     page = reader.pages[i]
     text_body = page.extract_text()
     pdf_txt_object.write(text_body)
    pdf_txt_object.close()


def gen_qna():
  print(threading.current_thread().name, 'Starting')
  #croping pdf pages
  crop(["-u", "-p", "10.0", "-m4", "0", "2", "0", "3","-prw","1.0","1.0","1.0","1.0", "-ap4", "52.0", "30.0", "50.0", "62.0"  ,"2.pdf"])
  print("cropping successfull")

  #checking the files if they are empty or contain data from previous run.
  if os.stat("C:\\Users\\Hp\\Desktop\\flask learning\\ip.txt").st_size != 0:
      open("C:\\Users\\Hp\\Desktop\\flask learning\\ip.txt","w").close() 

  open("C:\\Users\\Hp\\Desktop\\flask learning\\output.csv","w").close()
  open("C:\\Users\\Hp\\Desktop\\flask learning\\output_without_paraphrasing.csv","w").close()

  read_page(0,2)

  read_txt = open("ip.txt", "r")
  content = read_txt.read()

  ai_blank = blankline_tokenize(content)
  ai_blank_copy = ai_blank

  try:
   for i in range(len(ai_blank_copy)):
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
  except:
      print("Done")
  return jsonify(q_lst)    


@app.route("/qna")
def index():
    threading.Thread(target=gen_qna).start()
    return "Hello World!"

@app.route("/info")
def info():
    return "info page"

if __name__ == "__main__":
    app.run(debug=True, host="192.168.1.3")