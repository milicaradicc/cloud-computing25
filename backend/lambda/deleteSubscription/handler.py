import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

table_name = os.environ["SUBSCRIPTIONS_TABLE"]
score_table_name = os.environ["SCORE_TABLE"]
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(table_name)
score_table = dynamodb.Table(score_table_name)

def lambda_handler(event, context):
    subscription_id = event.get("pathParameters", {}).get("id")
    if not subscription_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Missing subscription id in path"})
        }

    try:
        response = table.query(
            IndexName="id-index",
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

        update_response = table.update_item(
            Key={"Target": pk, "User": sk},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"},
            ReturnValues="UPDATED_NEW"
        )

        # Reset score u score tabeli
        target_type, target_id_or_name = pk.split("#")
        score_key = {"User": sk}
        if target_type.lower() == "genre":
            score_key["Content"] = f"GENRE#{target_id_or_name}"
        elif target_type.lower() == "artist":
            score_key["Content"] = f"ARTIST#{target_id_or_name}"
        else:
            score_key = None

        if score_key:
            try:
                # Update score
                score_table.update_item(
                    Key=score_key,
                    UpdateExpression="SET Subscribed = :val",
                    ExpressionAttributeValues={":val": 0}
                )
            except Exception as e:
                print("Score table update error:", e)

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
