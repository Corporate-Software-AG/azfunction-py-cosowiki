import logging
import azure.functions as func
import urllib.request
from bs4 import BeautifulSoup

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"URI: {myblob.uri}\n"
                 f"Blob Size: {myblob.length} bytes")

    with urllib.request.urlopen(myblob.uri) as f:
        html = f.read().decode('utf-8')

    with open(html) as fp:
        soup = BeautifulSoup(fp, "html.parser")
    

    logging.info(soup)
