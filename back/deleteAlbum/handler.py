import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
album_table = dynamodb.Table("Album")
song_table = dynamodb.Table("Song")


def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role != "admin":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }

    try:
        params = event.get("queryStringParameters", {}) or {}

        genre = params.get("Genre")   
        album_id = params.get("Id")   

        if not genre or not album_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Missing 'Genre' or 'Id' parameter"})
            }

        print("sad treba da brise")
        album_table.update_item(
            Key={
                "Genre": genre,
                "Id": album_id
            },
            UpdateExpression="set deleted = :val",
            ExpressionAttributeValues={":val": "true"}
        )
        print("sad treba da je obrisao")
        response = song_table.query(
            KeyConditionExpression=Key("Album").eq(album_id)
        )
        songs = response.get("Items", [])

        for song in songs:
            song_table.update_item(
                Key={
                    "Album": song["Album"],
                    "Id": song["Id"]
                },
                UpdateExpression="set deleted = :val",
                ExpressionAttributeValues={":val": "true"}
            )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Album {album_id} and {len(songs)} songs marked as deleted"
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
