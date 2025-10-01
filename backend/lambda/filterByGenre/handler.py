import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os

# Dohvat imena tabela iz environment var
ARTISTS_TABLE_NAME = os.environ["ARTISTS_TABLE"]
ALBUMS_TABLE_NAME = os.environ["ALBUMS_TABLE"]

dynamodb = boto3.resource("dynamodb")
artists_table = dynamodb.Table(ARTISTS_TABLE_NAME)
albums_table = dynamodb.Table(ALBUMS_TABLE_NAME)

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
}

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    # Preflight request (OPTIONS)
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"message": "CORS preflight"})
        }

    try:
        query_params = event.get("queryStringParameters") or {}
        genre = query_params.get("genre")

        if not genre:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Missing 'genre' query parameter"})
            }

        # Query za umetnike po žanru
        artists_response = artists_table.query(
            KeyConditionExpression=Key("Genre").eq(genre)
        )

        # Query za albume po žanru
        albums_response = albums_table.query(
            KeyConditionExpression=Key("Genre").eq(genre)
        )

        result = {
            "artists": artists_response.get("Items", []),
            "albums": albums_response.get("Items", [])
        }

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps(result, cls=DecimalEncoder)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e), "trace": error_trace})
        }
