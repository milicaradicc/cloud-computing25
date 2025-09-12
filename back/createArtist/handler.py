import json
import os
import boto3
import uuid

# Extract environment variable (better than hardcoding)
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

    name = body.get("name")
    biography = body.get("biography")
    genres = body.get("genres")

    # Validate required fields
    if not name or not biography or not genres:
        return {
            "statusCode": 400,
            "headers": {
            "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"message": "Missing required fields"})
        }

    # Generate artistId
    artist_id = str(uuid.uuid4())

    # Build DynamoDB item
    item = {
        "Entity type identifier": f"ARTIST#{artist_id}",
        "Entity-specific identifier": "PROFILE",
        "artistId": artist_id,#TODO:is this needed?
        "name": name,
        "biography": biography,
        "genres": genres,
        "entityType":"artist"
    }

    # Put item into DynamoDB
    table = dynamodb.Table(table_name)
    table.put_item(Item=item)

    # Successful response
    response_body = {
        "message": "Successfully created artist profile",
        "artist": item
    }
    return {
        "statusCode": 201,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(response_body, default=str)
    }
