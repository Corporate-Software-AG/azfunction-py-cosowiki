import logging
import azure.functions as func
import os

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
    kb_id = os.environ["kb_id"]

    client = QnAMakerClient(endpoint=endpoint, credentials=CognitiveServicesCredentials(subscription_key))

    update_kb(client=client, kb_id=kb_id, blob_url=myblob.uri)

    publish_kb(client=client, kb_id=kb_id)


def update_kb(client, kb_id, blob_url):
    logging.info("Updating knowledge base...")

    update_kb_operation_dto = UpdateKbOperationDTO(
        add=UpdateKbOperationDTOAdd(
            qna_list=[],
            urls =[
                blob_url
            ],
            files = []
        ),
        delete=None,
        update=None
    )
    
    logging.info(update_kb_operation_dto)

    update_op = client.knowledgebase.update(kb_id=kb_id, update_kb=update_kb_operation_dto)
    
    
    #_monitor_operation(client=client, operation=update_op)

    logging.info("Updated knowledge base.")

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