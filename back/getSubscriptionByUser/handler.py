import json
import boto3

table_name = "Subscriptions"
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    print("event:", event)
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "user":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    userId = event.get("queryStringParameters", {}).get("userId")
    if not userId:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing userId query parameter"})
        }

    try:
        table = dynamodb.Table(table_name)
        response = table.query(
            IndexName="User-index",
            KeyConditionExpression="#usr = :uid",
            ExpressionAttributeNames={"#usr": "User"},
            ExpressionAttributeValues={":uid": userId}
        )

        items = response.get("Items", [])
        subscriptions = []

        for item in items:
            created_at_val = item.get("createdAt")
            created_at = int(created_at_val) if created_at_val is not None else 0

            subscriptions.append({
                "id": item.get("id"),
                "User": item.get("User"),
                "Target": item.get("Target"),
                "type": item.get("type"),
                "createdAt": created_at,
                "targetName": item.get("targetName")
            })

        print("subs:", subscriptions)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(subscriptions)
        }

    except Exception as e:
        print("DynamoDB error:", e)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }
