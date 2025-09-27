import json
import base64
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

ALBUM_TABLE = "Album"
ARTIST_ALBUM_TABLE = "ArtistAlbum"

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
album_table = dynamodb.Table(ALBUM_TABLE)
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE)

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        album_id = body.get('Id')
        album_title = body['title']
        genre = body['Genre']
        genres = body['genres']
        description = body.get('description', '')
        artists = body['artists']
        cover_image = body.get('coverImage', '')

        if not album_id:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album ID is required"})
            }

        if not genres or len(genres) == 0:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album must have at least one genre"})
            }

        print(f"Updating album '{album_title}' in DynamoDB table {ALBUM_TABLE}")
        print(genre)
        response = album_table.get_item(
            Key={
                'Genre': genre,
                'Id': album_id
            }
        )
        print(response)

        if 'Item' not in response:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album not found"})
            }

        existing_album = response['Item']
        old_artists = existing_album.get('artists', [])

        # Ako trenutni Genre nije u novim genres, postavi prvi iz genres
        if genre not in genres:
            genre = genres[0]

        updated_item = {
            "Genre": genre,
            "Id": album_id,
            "title": album_title,
            "artists": artists,
            "genres": genres,
            "releaseDate": existing_album.get('releaseDate', str(datetime.now())),
            "description": description,
            "coverImage": cover_image,
            "createdDate": existing_album.get('createdDate', str(datetime.now())),
            "modifiedDate": str(datetime.now()),
            "deleted": "false"
        }

        album_table.put_item(Item=updated_item)
        print(f"Updated album '{album_title}' in DynamoDB table {ALBUM_TABLE}")

        # Ažuriraj ArtistAlbum veze
        # Ukloni sve stare veze
        for old_artist_id in old_artists:
            try:
                artist_album_table.delete_item(
                    Key={
                        'ArtistId': old_artist_id,
                        'AlbumId': album_id
                    }
                )
                print(f"Removed artist {old_artist_id} from album {album_id}")
            except Exception as e:
                print(f"Could not remove artist {old_artist_id}: {e}")

        # Dodaj nove veze
        for artist_id in artists:
            try:
                artist_album_table.put_item(Item={
                    "ArtistId": artist_id,
                    "AlbumId": album_id,
                    "AlbumGenre": genre,
                    "createdDate": str(datetime.now())
                })
                print(f"Added artist {artist_id} to album {album_id}")
            except Exception as e:
                print(f"Could not add artist {artist_id}: {e}")

        print(f"Updated {len(artists)} entries in ArtistAlbum table")

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Album '{album_title}' updated successfully.",
                "albumId": album_id,
                "item": updated_item
            }, default=str)
        }

    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
