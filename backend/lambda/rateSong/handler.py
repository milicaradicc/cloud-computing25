import json
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

table_name = os.environ["RATING_TABLE"]
song_table_name = os.environ["SONGS_TABLE"]
score_table_name = os.environ["SCORE_TABLE"]

dynamodb = boto3.resource("dynamodb")
rating_table = dynamodb.Table(table_name)
song_table = dynamodb.Table(song_table_name)
score_table = dynamodb.Table(score_table_name)

def update_score(user, content, rating_value):
    try:
        response = score_table.get_item(Key={"User": user, "Content": content})
        item = response.get("Item")

        if item:
            new_sum = Decimal(item.get("sum", 0)) + Decimal(rating_value)
            new_number = item.get("number", 0) + 1
            new_average = float(new_sum / new_number)
            score_table.update_item(
                Key={"User": user, "Content": content},
                UpdateExpression="SET #s = :s, #n = :n, #a = :a",
                ExpressionAttributeNames={"#s": "sum", "#n": "number", "#a": "average"},
                ExpressionAttributeValues={":s": new_sum, ":n": new_number, ":a": Decimal(str(new_average))}
            )
        else:
            score_table.put_item(
                Item={
                    "User": user,
                    "Content": content,
                    "sum": Decimal(str(rating_value)),
                    "number": 1,
                    "average": Decimal(str(rating_value))
                }
            )
    except Exception as e:
        print(f"Error updating score for {content}: {str(e)}")

def lambda_handler(event, context):
    headers = {"Access-Control-Allow-Origin": "*"}

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
                "rating": Decimal(str(rating_value))
            }
        )

        song_response = song_table.query(
            IndexName="Id-index",
            KeyConditionExpression=Key("Id").eq(song_id)
        )
        song_items = song_response.get("Items", [])
        if song_items:
            song_item = song_items[0]
            artists = song_item.get("artists", [])
            genres = song_item.get("genres", [])

            for artist in artists:
                update_score(user_id, f"ARTIST#{artist}", rating_value)

            for genre in genres:
                update_score(user_id, f"GENRE#{genre}", rating_value)

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
