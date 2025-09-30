import json
import os

import boto3
from boto3.dynamodb.conditions import Key, Attr

songs_table_name = os.environ["SONGS_TABLE"]
albums_table_name = os.environ["ALBUMS_TABLE"]
bucket_name = os.environ["BUCKET_NAME"]

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)
albums_table = dynamodb.Table(albums_table_name)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role != "admin":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }

    path_params = event.get("pathParameters") or {}
    album_id = path_params.get("id")

    if not album_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing 'albumid' in path"})
        }

    try:
        album_response = albums_table.query(
            IndexName="Id-index",
            KeyConditionExpression=Key("Id").eq(album_id)
        )

        if not album_response.get("Items"):
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Album not found"})
            }

        album_item = album_response["Items"][0]

        albums_table.update_item(
            Key={"Genre": album_item["Genre"], "Id": album_item["Id"]},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"}
        )

        songs_response = songs_table.query(
            IndexName="Album-index",
            KeyConditionExpression=Key("Album").eq(album_id),
            FilterExpression=Attr("deleted").eq("false")
        )

        for song in songs_response.get("Items", []):
            songs_table.update_item(
                Key={"Album": album_id, "Id": song["Id"]},
                UpdateExpression="SET deleted = :val",
                ExpressionAttributeValues={":val": "true"}
            )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": f"Album {album_id} and its songs marked deleted."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
