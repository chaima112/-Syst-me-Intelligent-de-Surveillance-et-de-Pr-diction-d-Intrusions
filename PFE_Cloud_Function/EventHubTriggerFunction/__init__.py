import logging
import json
import base64
import azure.functions as func
from azure.storage.blob import BlobServiceClient
import os

def main(event: func.EventHubEvent):
    logging.info("Function triggered by Event Hub message")
    
    conn_str = os.getenv("STORAGE_CONNECTION_STRING")
    if not conn_str:
        logging.error("STORAGE_CONNECTION_STRING is missing")
        return

    try:
        # 1. Décoder le message (bytes -> string)
        message_body = event.get_body().decode('utf-8')
        payload = json.loads(message_body)
        
        # 2. Extraire l'image en Base64
        img_b64 = payload.get('image')
        if not img_b64:
            logging.error("No 'image' field in message")
            return
        
        # 3. Décoder le Base64 -> bytes
        img_bytes = base64.b64decode(img_b64)
        
        # 4. Stocker dans Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        container_name = "captures"
        container_client = blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
        
        blob_name = f"capture_{event.sequence_number}.jpg"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(img_bytes, overwrite=True)
        
        logging.info(f" Image saved: {blob_name}")
    except Exception as e:
        logging.error(f" Error: {e}")