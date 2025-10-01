import json
import os

import boto3
from boto3.dynamodb.conditions import Key

songs_table_name = os.environ["SONGS_TABLE"]
albums_table_name = os.environ["ALBUMS_TABLE"]
artists_table_name = os.environ["ARTISTS_TABLE"]
artist_song_table_name = os.environ["ARTIST_SONG_TABLE"]
artist_album_table_name = os.environ["ARTIST_ALBUM_TABLE"]

dynamodb = boto3.resource("dynamodb")
songs_table = dynamodb.Table(songs_table_name)
albums_table = dynamodb.Table(albums_table_name)
artists_table = dynamodb.Table(artists_table_name)
artist_song_table = dynamodb.Table(artist_song_table_name)
artist_album_table = dynamodb.Table(artist_album_table_name)

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
    artist_id = path_params.get("id")

    if not artist_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing 'id' in path"})
        }

    try:
        artist_resp = artists_table.query(
            IndexName="Id-index",
            KeyConditionExpression=Key("Id").eq(artist_id)
        )
        if not artist_resp["Items"]:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Artist not found"})
            }
        artist = artist_resp["Items"][0]
        genre = artist["Genre"]

        artists_table.update_item(
            Key={"Genre": genre, "Id": artist_id},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"},
            ConditionExpression="attribute_exists(Id)"
        )
        print(f"Artist {artist_id} marked deleted")

        albums = artist_album_table.query(
            KeyConditionExpression=Key('ArtistId').eq(artist_id)
        )['Items']

        for artist_album in albums:
            album_id = artist_album['AlbumId']
            album = albums_table.get_item(
                Key={'Genre': artist_album["AlbumGenre"], 'Id': album_id}
            ).get('Item')
            if not album:
                continue

            if len(album.get('artists', [])) > 1:
                album['artists'].remove(artist_id)
                albums_table.update_item(
                    Key={'Genre': album['Genre'], 'Id': album_id},
                    UpdateExpression='SET artists = :a',
                    ExpressionAttributeValues={':a': album['artists']}
                )
            else:
                albums_table.update_item(
                    Key={'Genre': album['Genre'], 'Id': album_id},
                    UpdateExpression='SET deleted = :val',
                    ExpressionAttributeValues={':val': "true"}
                )

            songs = artist_song_table.query(
                KeyConditionExpression=Key('ArtistId').eq(artist_id)
            )['Items']

            for s in songs:
                if s['AlbumId'] != album_id:
                    continue

                song_item = songs_table.get_item(
                    Key={'Album': album_id, 'Id': s['SongId']}
                ).get('Item')
                if not song_item:
                    continue

                if len(song_item.get('artists', [])) > 1:
                    song_item['artists'].remove(artist_id)
                    songs_table.update_item(
                        Key={'Album': album_id, 'Id': s['SongId']},
                        UpdateExpression='SET artists = :a',
                        ExpressionAttributeValues={':a': song_item['artists']}
                    )
                else:
                    songs_table.update_item(
                        Key={'Album': album_id, 'Id': s['SongId']},
                        UpdateExpression='SET deleted = :val',
                        ExpressionAttributeValues={':val': "true"}
                    )

                artist_song_table.delete_item(
                    Key={'ArtistId': artist_id, 'SongId': s['SongId']}
                )

            artist_album_table.delete_item(
                Key={'ArtistId': artist_id, 'AlbumId': album_id}
            )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Artist {artist_id} marked deleted. Albums and songs cleaned up."
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
