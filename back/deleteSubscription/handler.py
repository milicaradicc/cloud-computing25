import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

table_name = "Subscriptions"
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    subscription_id = event.get("pathParameters", {}).get("subscriptionId")
    if not subscription_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing subscription id in path"})
        }

    table = dynamodb.Table(table_name)

    try:
        response = table.query(
            IndexName="id-index",  # GSI
            KeyConditionExpression=Key("id").eq(subscription_id),
            FilterExpression=Attr("deleted").eq("false")
        )
        items = response.get("Items", [])

        if not items:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Subscription not found or already deleted"})
            }

        item = items[0]
        pk = item["Target"]
        sk = item["User"]

        print(pk,sk)

        # Soft delete
        update_response = table.update_item(
            Key={"Target": pk, "User": sk},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"},
            ReturnValues="UPDATED_NEW"
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "success": True,
                "message": f"Subscription {subscription_id} marked as deleted",
                "updatedAttributes": update_response.get("Attributes")
            })
        }

    except Exception as e:
        print("DynamoDB error:", e)
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Internal server error"})
        }
