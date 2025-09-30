import json
import os

import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

songs_table_name = os.environ["SONGS_TABLE"]
dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    print(role)
    if role != "admin" and role != "user":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }
    try:
        response = songs_table.query(
            IndexName="deleted-index",
            KeyConditionExpression=Key("deleted").eq("false")
        )
        items = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(items, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
