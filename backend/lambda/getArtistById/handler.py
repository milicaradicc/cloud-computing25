import json
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import os

ARTISTS_TABLE_NAME = os.environ["ARTISTS_TABLE"]
ARTIST_ALBUM_TABLE_NAME = os.environ["ARTIST_ALBUM_TABLE"]
ALBUMS_TABLE_NAME = os.environ["ALBUMS_TABLE"]

dynamodb = boto3.resource("dynamodb")

artists_table = dynamodb.Table(ARTISTS_TABLE_NAME)
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE_NAME)
albums_table = dynamodb.Table(ALBUMS_TABLE_NAME)


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)


def lambda_handler(event, context):
    try:
        path_params = event.get('pathParameters', {})
        artist_id = path_params.get('id')

        if not artist_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "'id' path parameter is required"})
            }

        response = artists_table.scan(
            FilterExpression=Key("Id").eq(artist_id)
        )
        items = response.get("Items", [])
        if not items:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Artist not found"})
            }

        artist_details = items[0]

        artist_album_response = artist_album_table.query(
            KeyConditionExpression=Key("ArtistId").eq(artist_id)
        )
        artist_album_items = artist_album_response.get("Items", [])

        albums = []
        for item in artist_album_items:
            album_id = item.get("AlbumId")
            if not album_id:
                continue

            album_response = albums_table.query(
                IndexName="Id-index",  
                KeyConditionExpression=Key("Id").eq(album_id)
            )
            album_items = album_response.get("Items", [])
            if album_items:
                albums.append(album_items[0])

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "artist": artist_details,
                "albums": albums  
            }, cls=DecimalEncoder)
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Internal Server Error", "details": str(e)})
        }
