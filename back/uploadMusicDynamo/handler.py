import json
import uuid

import boto3

TABLE_NAME = 'MusicStreamingApp'
table = boto3.resource(TABLE_NAME)

def lambda_handler(event, context):
    try:
        request_body = json.loads(event['body'])

        # Put item into table
        response = table.put_item(
            Item={
                'PK': f"SONG#{str(uuid.uuid4())}",
                'SK': "PROFILE",
                'name': request_body['name'],
                'type': request_body['type'],
                'size': request_body['size'],
                'time_created': request_body['time_created'],
                'last_modified': request_body['last_modified'],
                # these are given by admin
                'genres': request_body['genres'],
                'artists': request_body['artists'],
                'album_id': request_body['album_id'],
                'picture': request_body['picture'],
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "File metadata uploaded successfully."})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }