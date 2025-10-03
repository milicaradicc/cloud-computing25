import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal

songs_table_name = os.environ["SONGS_TABLE"]
albums_table_name = os.environ["ALBUMS_TABLE"]
artists_table_name = os.environ["ARTISTS_TABLE"]

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)
albums_table = dynamodb.Table(albums_table_name)
artists_table = dynamodb.Table(artists_table_name)

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")
    if role not in ["admin", "user"]:
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }

    try:
        response = songs_table.query(
            IndexName="deleted-index",
            KeyConditionExpression=Key("deleted").eq("false")
        )
        songs = response.get("Items", [])

        enriched_songs = []

        for song in songs:
            album_obj = None
            if "Album" in song and song["Album"]:
                album_id = song["Album"]
                album_response = albums_table.query(
                    IndexName="Id-index",
                    KeyConditionExpression=Key("Id").eq(album_id)
                )
                album_items = album_response.get("Items")
                if album_items:
                    album_obj = album_items[0]

            artist_objs = []
            for artist_id in song.get("artists", []):
                artist_response = artists_table.query(
                    IndexName="Id-index",
                    KeyConditionExpression=Key("Id").eq(artist_id)
                )
                artist_items = artist_response.get("Items")
                if artist_items:
                    artist_objs.append(artist_items[0])

            enriched_song = dict(song)  # kopiramo original
            enriched_song["Album"] = album_obj
            enriched_song["Artists"] = artist_objs
            enriched_songs.append(enriched_song)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(enriched_songs, cls=DecimalEncoder)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
