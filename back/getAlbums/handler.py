import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

table_name = "Album"
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # možeš da biraš: int ili float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    try:
        response = table.query(
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
