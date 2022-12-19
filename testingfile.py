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



warnings.filterwarnings("ignore")
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


    
