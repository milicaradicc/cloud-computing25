import json
import uuid
from datetime import datetime

import boto3

table_name = "MusicStreamingApp"
dynamodb = boto3.resource("dynamodb")


def lambda_handler(event, context):
    try:
        print(event)
        data = event
        song_id = str(uuid.uuid4())

        item = {
            "Entity type identifier": f"SONG#{song_id}",
            "Entity-specific identifier": "PROFILE",
            "entityType": "song",
            "title": data['title'],
            "type": data.get('type', 'single'),
            "artists": data['artists'],
            "genres": data.get('genres', []),
            "releaseDate": data.get('releaseDate', str(datetime.now())),
            "description": data.get('description', ''),
            "fileName": data.get('fileName'),
            "fileSize": data.get('fileSize'),
            "fileType": data.get('fileType'),
            "coverImage": data.get('coverImage'),
            "album": data.get('album'),
            "createdDate": data.get('createdDate'),
            "modifiedDate": data.get('modifiedDate'),
            "duration": data.get('duration'),
        }

        table = dynamodb.Table(table_name)
        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Metadata saved", "itemId": song_id})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }