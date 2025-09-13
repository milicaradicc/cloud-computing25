import json
import os
import boto3
import uuid

table_name = "MusicStreamingApp"
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            },
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }


    body = json.loads(event['body'])

    createdDate = body["createdDate"]
    modifiedDate = body["modifiedDate"]
    title = body["title"]
    description = body["description"]
    artists = body["artists"]
    genres = body["genres"]
    coverImage = body["coverImage"]


    album_id = str(uuid.uuid4())

    item = {
        "Entity type identifier": f"ALBUM#{album_id}",
        "Entity-specific identifier": "PROFILE",
        "entityType":"album",
        "createdDate": createdDate,
        "modifiedDate": modifiedDate,
        "title": title,
        "description": description,
        "artists": artists,
        "genres": genres,
        "coverImage": coverImage,
    }

    table = dynamodb.Table(table_name)
    table.put_item(Item=item)

    response_body = {
        "message": "Successfully created artist profile",
        "album": item
    }
    return {
        "statusCode": 201,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response_body, default=str)
    }
