import os
import json
import logging
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
    except Exception:
        return func.HttpResponse('Invalid JSON', status_code=400)

    if not isinstance(body, list):
        return func.HttpResponse('Expected JSON array', status_code=400)

    endpoint = os.environ.get('COSMOS_ENDPOINT')
    database = os.environ.get('COSMOS_DATABASE', 'LegoDatabase')
    container_name = os.environ.get('COSMOS_CONTAINER', 'legoSets')

    if not endpoint:
        return func.HttpResponse('COSMOS_ENDPOINT not configured', status_code=500)

    credential = DefaultAzureCredential()
    client = CosmosClient(url=endpoint, credential=credential)
    db = client.get_database_client(database)
    container = db.get_container_client(container_name)

    upserted = 0
    for item in body:
        # map set_number to id if present
        if 'set_number' in item:
            item['id'] = str(item.pop('set_number'))
        elif 'id' not in item:
            # require id or set_number
            continue
        try:
            container.upsert_item(item)
            upserted += 1
        except Exception as e:
            logging.error(f"Failed to upsert item: {e}")

    return func.HttpResponse(json.dumps({"upserted": upserted}), mimetype="application/json")
