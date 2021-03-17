import logging
import azure.functions as func
import urllib.request
import os
import time

from bs4 import BeautifulSoup
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"URI: {myblob.uri}\n"
                 f"Blob Size: {myblob.length} bytes")
    
    qna_list = create_qna_list_from_blob(myblob=myblob)
    write_txt(blob_id=''.join(e for e in myblob.name if e.isalnum()), qna_list=qna_list)

    logging.info("FINISHED")


def create_qna_list_from_blob(myblob):
    logging.info("Create QnA List from Blob")
    with urllib.request.urlopen(myblob.uri) as f:
        html = f.read().decode('utf-8')
        soup = BeautifulSoup(html, "html.parser")
        
        qna_list = []
        for title in soup.findAll(id=lambda x: x and x.startswith('wiki-mht-section-title-')):
            number = title['id'][-1]
            section_id = "wiki-mht-section-content-" + number
            answer=soup.find(id=section_id).decode_contents()
            if (len(answer) <= 1):
                answer = "No Content"
            qna_list.append({"answer":answer, "title":title.string})
        
    return qna_list

def write_txt(blob_id, qna_list):
    logging.info("Write QnA List into TXT")
    local_file_name = str(blob_id) + ".txt"
    with open(local_file_name, "w") as file:
        for num, qna in enumerate(qna_list, start=1):
            file.write("{}. {}\n".format(str(num), qna['title']))
            file.write("{}\n\n".format(qna['answer']))
        file.close()
    upload_txt(local_file_name, "faqtxt")

def upload_txt(local_file_name, container_name):
    logging.info("Upload TXT into Blob Container {}".format(container_name))
    # Create a blob client using the local file name as the name for the blob
    
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the created file
    with open(local_file_name, "rb") as data:
        blob_client.upload_blob(data)