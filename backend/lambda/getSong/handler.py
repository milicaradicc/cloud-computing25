import json
import os
import boto3
from decimal import Decimal

songs_table_name = os.environ["SONGS_TABLE"]
albums_table_name = os.environ["ALBUMS_TABLE"]
artists_table_name = os.environ["ARTISTS_TABLE"]

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)
albums_table = dynamodb.Table(albums_table_name)
artist_table = dynamodb.Table(artists_table_name)


def decimal_default(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        path_params = event.get("pathParameters", {})
        song_id = path_params.get("id")
        if not song_id:
            return {"statusCode": 400, "body": json.dumps({"error": "songId is required"})}

        # Učitaj pesmu
        response = songs_table.query(
            IndexName="Id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("Id").eq(song_id)
        )
        items = response.get("Items", [])
        if not items:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Song not found"})
            }

        item = items[0]

        album_id = item.get("album")
        album_title = None
        if album_id:
            album_resp = albums_table.query(
                IndexName="Id-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("Id").eq(album_id)
            )
            album_items = album_resp.get("Items", [])
            if album_items:
                album_title = album_items[0].get("title")

        artist_ids = item.get("artists", [])
        artists_full = []
        for aid in artist_ids:
            artist_resp = artist_table.query(
                IndexName="Id-index",
                KeyConditionExpression=boto3.dynamodb.conditions.Key("Id").eq(aid)
            )
            artist_items = artist_resp.get("Items", [])
            if artist_items:
                a = artist_items[0]
                artists_full.append({
                    "Id": a.get("Id"),
                    "name": a.get("name", "Unknown"),
                    "biography": a.get("biography", ""),
                    "genres": a.get("genres", []),
                    "Genre": a.get("Genre", "")
                })

        song = {
            "id": item.get("Id"),
            "title": item.get("title"),
            "artists": artists_full,
            "genres": item.get("genres", []),
            "description": item.get("description", ""),
            "coverImage": item.get("coverImage"),
            "album": album_title,
            "duration": item.get("duration"),
            "releaseDate": item.get("releaseDate"),
            "type": item.get("type", "single"),
            "fileName": item.get("fileName", ""),
            "transcriptFileName": item.get("transcriptFileName", "")
        }

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps(song, default=decimal_default)
        }

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error occurred: {error_trace}")
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*", "Content-Type": "application/json"},
            "body": json.dumps({"error": str(e), "trace": error_trace})
        }
