import json
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Key

ALBUMS_TABLE_NAME = os.environ["ALBUMS_TABLE"]
SONGS_TABLE_NAME = os.environ["SONGS_TABLE"]
ARTIST_ALBUM_TABLE_NAME = os.environ["ARTIST_ALBUM_TABLE"]
ARTISTS_TABLE_NAME = os.environ["ARTISTS_TABLE"]
ARTIST_SONG_TABLE_NAME = os.environ["ARTIST_SONG_TABLE"]

dynamodb = boto3.resource("dynamodb")
albums_table = dynamodb.Table(ALBUMS_TABLE_NAME)
songs_table = dynamodb.Table(SONGS_TABLE_NAME)
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE_NAME)
artists_table = dynamodb.Table(ARTISTS_TABLE_NAME)
artist_song_table = dynamodb.Table(ARTIST_SONG_TABLE_NAME)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        role = claims.get("custom:role") if claims else None
        if role is not None and role not in ("admin", "user"):
            return {
                "statusCode": 403,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Forbidden"})
            }

        album_id = event.get("pathParameters", {}).get("id")
        if not album_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Missing album id"})
            }

        response = albums_table.query(
            IndexName="Id-index",
            KeyConditionExpression=Key("Id").eq(album_id)
        )
        items = response.get("Items", [])
        if not items:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album not found"})
            }

        album = items[0]

        artist_album_resp = artist_album_table.query(
            IndexName="AlbumId-index", 
            KeyConditionExpression=Key("AlbumId").eq(album_id)
        )
        artist_ids = [item["ArtistId"] for item in artist_album_resp.get("Items", [])]

        artist_data = []
        for artist_id in artist_ids:
            r = artists_table.query(
                IndexName="Id-index",
                KeyConditionExpression=Key("Id").eq(artist_id)
            )
            artist_item = r.get("Items", [{}])[0]
            artist_name = artist_item.get("name")

            artist_songs_resp = artist_song_table.query(
                IndexName="AlbumId-index",  
                KeyConditionExpression=Key("AlbumId").eq(album_id) & Key("ArtistId").eq(artist_id)
            )

            song_ids = [s["SongId"] for s in artist_songs_resp.get("Items", [])]

            songs = []
            for song_id in song_ids:
                song_resp = songs_table.get_item(Key={"Album": album_id, "Id": song_id})
                if "Item" in song_resp:
                    songs.append({
                        "Id": song_id,
                        "title": song_resp["Item"].get("title"),
                        "duration": song_resp["Item"].get("duration"),
                        "genres": song_resp["Item"].get("genres"),
                        "type": song_resp["Item"].get("type"),
                        "artists": [{
                            "Id": artist_id,
                            "name": artist_name,
                        }]
                    })

            artist_data.append({
                "Id": artist_id,
                "Name": artist_name,
                "Songs": songs
            })

        album["Artists"] = artist_data

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps(album, cls=DecimalEncoder)
        }

    except Exception as e:
        import traceback
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "error": str(e),
                "trace": traceback.format_exc()
            })
        }
