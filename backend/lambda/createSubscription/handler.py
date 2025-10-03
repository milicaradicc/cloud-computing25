import json
import os
import boto3
import uuid
import time

table_name = os.environ["SUBSCRIPTIONS_TABLE"]
score_table_name = os.environ["SCORE_TABLE"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)
score_table = dynamodb.Table(score_table_name)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "user":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message": "Forbidden: Insufficient permissions"})
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

    userId = body.get("userId")
    targetId = body.get("targetId")
    targetType = body.get("type")
    targetName = body.get("targetName")
    email = body.get("email")

    if not userId or not targetId or not targetType:
        print("Missing required fields")
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing required fields"})
        }

    subscription_id = str(uuid.uuid4())
    createdAt = int(time.time())

    item = {
        "Target": f"{targetType}#{targetId}",
        "User": userId,
        "id": subscription_id,
        "type": targetType,
        "createdAt": createdAt,
        "targetName": targetName,
        "email": email,
        "deleted": "false"
    }

    try:
        table.put_item(Item=item)
    except Exception as e:
        print("DynamoDB error:", e)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }

    score_item = {
        "User": userId,
        "Content": None,
        "Timestamp": createdAt,
        "Genre": None,
        "Subscribed": 1
    }

    if targetType.lower() == "genre":
        score_item["Content"] = f"GENRE#{targetName}"
        score_item["Genre"] = targetName
    elif targetType.lower() == "artist":
        score_item["Content"] = f"ARTIST#{targetId}"
        score_item["Genre"] = None
    else:
        score_item = None

    if score_item:
        try:
            score_table.put_item(Item=score_item)
        except Exception as e:
            print("Score table error:", e)

    return {
        "statusCode": 201,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "message": "Successfully created subscription",
            "subscription": item,
            "scoreItem": score_item
        })
    }
