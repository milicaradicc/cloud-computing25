import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
song_table = dynamodb.Table("Song")
album_table = dynamodb.Table("Album")
artist_table = dynamodb.Table("Artists")
artist_album_table = dynamodb.Table("ArtistAlbum")
artist_song_table = dynamodb.Table("ArtistSong")

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
    genre = params.get("Genre")
    artist_id = params.get("Id")

    if not genre or not artist_id:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Missing 'Genre' or 'Id' parameter"})
        }

    try:
        # 1️⃣ Soft delete artist
        print(genre, artist_id)
        artist_table.update_item(
            Key={"Genre": genre, "Id": artist_id},
            UpdateExpression="SET deleted = :val",
            ExpressionAttributeValues={":val": "true"},
            ConditionExpression="attribute_exists(Id)"
        )
        print("Artist deleted successfully")

        # 2️⃣ Dohvati albume preko invertovanog indexa
        albums = artist_album_table.query(
            KeyConditionExpression=Key('ArtistId').eq(artist_id)
        )['Items']

        for artist_album in albums:
            album_id = artist_album['AlbumId']
            album = album_table.get_item(Key={'Genre': genre, 'Id': album_id}).get('Item')
            if not album:
                continue

            if len(album.get('artists', [])) > 1:
                # ukloni artist-a iz liste
                album['artists'].remove(artist_id)
                album_table.update_item(
                    Key={'Genre': album['Genre'], 'Id': album_id},
                    UpdateExpression='SET artists = :a',
                    ExpressionAttributeValues={':a': album['artists']}
                )
            else:
                # Soft delete albuma
                album_table.update_item(
                    Key={'Genre': album['Genre'], 'Id': album_id},
                    UpdateExpression='SET deleted = :val',
                    ExpressionAttributeValues={':val': "true"}
                )

                # Soft delete pesama u albumu preko invertovanog indexa
                songs = artist_song_table.query(
                    KeyConditionExpression=Key('ArtistId').eq(artist_id)
                )['Items']

                for s in songs:
                    if s['AlbumId'] == album_id:
                        song_item = song_table.get_item(Key={'Album': album_id, 'Id': s['SongId']}).get('Item')
                        if not song_item:
                            continue

                        if len(song_item.get('artists', [])) > 1:
                            song_item['artists'].remove(artist_id)
                            song_table.update_item(
                                Key={'Album': album_id, 'Id': s['SongId']},
                                UpdateExpression='SET artists = :a',
                                ExpressionAttributeValues={':a': song_item['artists']}
                            )
                        else:
                            # Soft delete pesme
                            song_table.update_item(
                                Key={'Album': album_id, 'Id': s['SongId']},
                                UpdateExpression='SET deleted = :val',
                                ExpressionAttributeValues={':val': "true"}
                            )

                        # --- Pravi delete iz invertovanog indexa ---
                        artist_song_table.delete_item(Key={'ArtistId': artist_id, 'SongId': s['SongId']})

            # --- Pravi delete iz invertovanog indexa albuma ---
            artist_album_table.delete_item(Key={'ArtistId': artist_id, 'AlbumId': album_id})

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": f"Artist {artist_id} marked deleted. Album and song cleanup done."})
        }

    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return {
            "statusCode": 404,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Artist not found"})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
