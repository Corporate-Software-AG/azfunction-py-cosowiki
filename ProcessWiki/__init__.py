import logging
import azure.functions as func
import urllib.request
from bs4 import BeautifulSoup

import os
import time

from azure.cognitiveservices.knowledge.qnamaker import QnAMakerClient
from azure.cognitiveservices.knowledge.qnamaker.models import QnADTO, MetadataDTO, CreateKbDTO, OperationStateType, UpdateKbOperationDTO, UpdateKbOperationDTOAdd, EndpointKeysDTO, QnADTOContext, PromptDTO, QueryDTO

from msrest.authentication import CognitiveServicesCredentials

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"URI: {myblob.uri}\n"
                 f"Blob Size: {myblob.length} bytes")

    subscription_key = os.environ["subscription_key"]
    endpoint = os.environ["endpoint"]

    logging.info(f"subscription_key_ {subscription_key}\n"
                 f"endpoint: {endpoint}\n"

    with urllib.request.urlopen(myblob.uri) as f:
        html = f.read().decode('utf-8')
        
        soup = BeautifulSoup(html, "html.parser")

        for title in soup.find_all('h3'):
            logging.info(title.string)

    

    logging.info("FINISHED")
