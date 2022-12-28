import csv
import pandas as pd
import os
from dotenv import load_dotenv
from azure.data.tables import TableServiceClient

def configure():
    load_dotenv()


def table_storage_upload(tb_name):
 connection_string = os.getenv('CONN_STR') 
 table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
 table_client = table_service_client.create_table(table_name=tb_name)
 table_client = table_service_client.get_table_client(table_name=tb_name)

 counter = 0 #counter for the rowkey of table.
 my_entity = {
    'PartitionKey': str(tb_name),
    'RowKey': '',
    'question': '',
    'answer': ''
 }

 #read_length_pandas = pd.read_csv('output.csv') #for reading csv length.
 f = open("output.csv", 'r')
 csvreader = csv.reader(f)

 #iterate through each row in the csv file and uploading to table storage.
 for row in csvreader:
    counter += 1    
    my_entity['RowKey'] = str(counter)
    my_entity['question'] = row[0]
    my_entity['answer'] = row[1]
    my_entity['PartitionKey'] = str(tb_name)
    entity = table_client.create_entity(entity=my_entity)
    my_entity = {} #resetting the dictionary.     
 f.close()


def main(guid):
 configure()
 tb_name = guid
 table_storage_upload(tb_name)
 #with open('guid_generated.txt','w') as x: x.write(tb_name)
 return "upload completed with GUID:" + str(tb_name)