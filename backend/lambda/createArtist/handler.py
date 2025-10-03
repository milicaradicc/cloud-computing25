import json
import boto3
import uuid
import os

table_name = os.environ.get('TABLE_NAME')
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    print("Claims:", claims)
    role = claims.get("custom:role")
    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event.get('body', '{}'))
    except Exception as e:
        print("JSON parse error:", e)
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Invalid JSON"})
        }

    name = body.get("name")
    biography = body.get("biography")
    genres = body.get("genres")
    print("Parsed body:", name, biography, genres)

    if not name or not biography or not genres or len(genres) == 0:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing required fields"})
        }

    artist_id = str(uuid.uuid4())
    primary_genre = genres[0]

    item = {
        "Genre": primary_genre,
        "Id": artist_id,
        "artistId": artist_id,
        "name": name,
        "biography": biography,
        "genres": genres,
        "deleted":"false"
    }

    try:
        table = dynamodb.Table(table_name)
        table.put_item(Item=item)
    except Exception as e:
        print("DynamoDB error:", e)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }

    return {
        "statusCode": 201,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"message": "Successfully created artist profile", "artist": item})
    }
