import logging
import os
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
    except Exception:
        return func.HttpResponse('Invalid JSON', status_code=400)
    if not isinstance(data, list):
        return func.HttpResponse('Expected JSON array', status_code=400)
    endpoint = os.environ.get('COSMOS_ENDPOINT')
    database_name = os.environ.get('COSMOS_DATABASE')
    container_name = os.environ.get('COSMOS_CONTAINER')
    if not endpoint or not database_name or not container_name:
        return func.HttpResponse('COSMOS_* env vars not set', status_code=500)
    cred = DefaultAzureCredential()
    client = CosmosClient(endpoint, credential=cred)
    db = client.get_database_client(database_name)
    container = db.get_container_client(container_name)
    count = 0
    for item in data:
        doc = {
            'id': item.get('set_number'),
            'set_number': item.get('set_number'),
            'name': item.get('name'),
            'theme_name': item.get('theme_name'),
            'year_released': item.get('year_released'),
            'number_of_parts': item.get('number_of_parts'),
            'type': item.get('type'),
            'image_url': item.get('image_url')
        }
        container.upsert_item(doc)
        count += 1
    return func.HttpResponse(f"Upserted {count} items", status_code=200)
