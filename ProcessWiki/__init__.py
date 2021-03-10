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
    
    qna_list = create_qna_list_from_blob(myblob)
    update_kb(qna_list)

    logging.info("FINISHED")

def create_qna_list_from_blob(myblob):
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
            qna_list.append(create_kb_faq_dto(answer, [title.string]))
        
    return qna_list



def update_kb(qna_list):
    logging.info("Updating knowledge base...")

    subscription_key = os.environ["subscription_key"]
    endpoint = os.environ["endpoint"]
    kb_id = os.environ["kb_id"]

    client = QnAMakerClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))
    
    update_kb_operation_dto = UpdateKbOperationDTO(
        add=UpdateKbOperationDTOAdd(
            qna_list=qna_list,
            urls =[],
            files = []
        ),
        delete=None,
        update=None
    )

    update_op = client.knowledgebase.update(kb_id=kb_id, update_kb=update_kb_operation_dto)
    _monitor_operation(client=client, operation=update_op)
    logging.info("Updated knowledge base.")
    publish_kb(client=client, kb_id=kb_id)

def create_kb_faq_dto(answer, questions):
    return QnADTO(
        answer=answer,
        questions=questions,
        metadata=[
            MetadataDTO(name="Category", value="FAQ"),
            MetadataDTO(name="FAQ", value=questions[0]),
        ]
    )

def _monitor_operation(client, operation):
    for i in range(20):
        if operation.operation_state in [OperationStateType.not_started, OperationStateType.running]:
            logging.info("Waiting for operation: {} to complete.".format(operation.operation_id))
            time.sleep(5)
            operation = client.operations.get_details(operation_id=operation.operation_id)
        else:
            break
    if operation.operation_state != OperationStateType.succeeded:
        raise Exception("Operation {} failed to complete.".format(operation.operation_id))

    return operation

def publish_kb(client, kb_id):
    print("Publishing knowledge base...")
    client.knowledgebase.publish(kb_id=kb_id)
    print("Published knowledge base.")