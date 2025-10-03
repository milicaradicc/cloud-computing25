import json
import os

import boto3
from decimal import Decimal

table_name = os.environ["RATING_TABLE"]
dynamodb = boto3.resource("dynamodb")
rating_table = dynamodb.Table(table_name)

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET,PUT,DELETE",
        "Access-Control-Allow-Headers": "Content-Type,Authorization"
    }

    try:
        song_id = event.get("pathParameters", {}).get("id")
        user_id = event.get("queryStringParameters", {}).get("userId") if event.get("queryStringParameters") else None

        if not user_id or not song_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "userId and songId are required"})
            }

        response = rating_table.get_item(
            Key={
                "User": user_id,
                "Song": song_id
            }
        )

        item = response.get("Item")

        if not item:
            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({
                    "userId": user_id,
                    "songId": song_id,
                    "rating": 0
                }, default=decimal_default)
            }

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(item, default=decimal_default)
        }

    except Exception as e:
        print("Error loading rating:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)}, default=decimal_default)
        }
