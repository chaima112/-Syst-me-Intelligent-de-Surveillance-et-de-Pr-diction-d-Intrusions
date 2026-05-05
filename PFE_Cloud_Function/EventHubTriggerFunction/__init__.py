import logging
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
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        image_data = event.get_body()
        
        # Nom unique basé sur le numéro de séquence
        blob_name = f"capture_{event.sequence_number}.jpg"
        
        container_name = "captures"
        container_client = blob_service_client.get_container_client(container_name)
        
        if not container_client.exists():
            container_client.create_container()
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(image_data, overwrite=True)
        
        logging.info(f"✅ Image saved: {blob_name}")
    except Exception as e:
        logging.error(f"Error: {e}")