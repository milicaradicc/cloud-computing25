import json
import os

import boto3

table_name = os.environ["RATING_TABLE"]
dynamodb = boto3.resource("dynamodb")
rating_table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*"
    }

    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role != "user":
        return {
            "statusCode": 403,
            "headers": headers,
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        song_id = event['pathParameters']['id']
        user_id = body.get('userId')
        rating_value = body.get('rating')

        if not user_id or rating_value is None:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({"message": "userId and rating are required"})
            }

        rating_table.put_item(
            Item={
                "User": user_id,
                "Song": song_id,
                "rating": rating_value
            }
        )

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({"message": "Rating saved successfully"})
        }

    except Exception as e:
        print("Error saving rating:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
