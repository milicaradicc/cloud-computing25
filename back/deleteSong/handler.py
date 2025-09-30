import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
song_table = dynamodb.Table("Song")
album_table = dynamodb.Table("Album")

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role != "admin":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }

    params = event.get("queryStringParameters") or {}
    album_id = params.get("Album")
    song_id = params.get("Id")

    if not album_id or not song_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing 'Album' or 'Id' parameter"})
        }

    try:
        # 1️⃣ Označi pesmu kao deleted
        song_table.update_item(
            Key={"Album": album_id, "Id": song_id},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"},
            ConditionExpression="attribute_exists(Id)"
        )

        # 2️⃣ Proveri da li ima još neobrisanih pesama
        response = song_table.query(
            IndexName="Album-index",  # GSI za query po albumu
            KeyConditionExpression=Key("Album").eq(album_id),
            FilterExpression=Attr("deleted").eq("false")
        )

        print("ovo je odgovor: ", response)

        if response['Count'] == 0:
            # 3️⃣ Ako nema više pesama, query-uj album po Id preko GSI
            album_response = album_table.query(
                IndexName="Id-index",
                KeyConditionExpression=Key("Id").eq(album_id)
            )

            print("ovo je odgovor: ", album_response)

            for album_item in album_response.get("Items", []):
                # Update-uj album koristeći originalni PK (Genre)
                album_table.update_item(
                    Key={"Genre": album_item["Genre"], "Id": album_item["Id"]},
                    UpdateExpression="SET deleted = :val",
                    ExpressionAttributeValues={":val": "true"}
                )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": f"Song {song_id} marked deleted. Album cleanup checked."})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Song not found"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
