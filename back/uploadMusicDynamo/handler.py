import json
import uuid
from datetime import datetime

import boto3

TABLE_NAME = 'MusicStreamingApp'
table = boto3.resource(TABLE_NAME)


def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden: Insufficient permissions"})
        }

    try:
        data = json.loads(event['body'])

        item = {
            "id": str(uuid.uuid4()),
            "title": data['title'],
            "type": data.get('type', 'single'),
            "artists": data['artists'],
            "genres": data.get('genres', []),
            "releaseDate": data.get('releaseDate', str(datetime.now())),
            "description": data.get('description', ''),
            "songs": data.get('songs', [])
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Metadata saved", "itemId": item["id"]})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }