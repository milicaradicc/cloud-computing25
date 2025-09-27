import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
RATING_TABLE = 'Rating'
rating_table = dynamodb.Table(RATING_TABLE)

def lambda_handler(event, context):
    # Ako je preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            },
            "body": ""
        }

    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    headers = {
        "Access-Control-Allow-Origin": "*"
    }

    if role != "admin":
        return {
            "statusCode": 403,
            "headers": headers,
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        song_id = event['pathParameters']['songId']
        user_id = event['queryStringParameters']['userId']

        response = rating_table.query(
            KeyConditionExpression=Key('User').eq(user_id) & Key('Content').eq(song_id)
        )

        items = response.get('Items', [])
        rating = items[0] if items else {"rating": 0}

        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps(rating)
        }

    except Exception as e:
        print("Error fetching rating:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"error": str(e)})
        }
