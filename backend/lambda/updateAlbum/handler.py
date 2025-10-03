import json
import base64
import os
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = os.environ["ALBUMS_TABLE"]
ARTIST_ALBUM_TABLE = os.environ["ARTIST_ALBUM_TABLE"]
S3_BUCKET = os.environ.get("BUCKET_NAME")

dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

album_table = dynamodb.Table(TABLE_NAME)
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE)


def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message": "Forbidden: Insufficient permissions"})
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
        cover_base64 = body.get('coverBase64')  # Nova slika u base64

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
        old_cover_image = existing_album.get('coverImage', '')

        # Ako postoji nova slika, uploaduj na S3
        if cover_base64:
            try:
                # Dekoduj base64
                image_data = base64.b64decode(cover_base64)

                # Upload na S3
                s3_client.put_object(
                    Bucket=S3_BUCKET,
                    Key=cover_image,
                    Body=image_data,
                    ContentType='image/jpeg'  # Ili detektuj tip iz fajla
                )
                print(f"Uploaded new cover image: {cover_image}")

                # Opciono: obriši staru sliku sa S3
                if old_cover_image and old_cover_image != cover_image:
                    try:
                        s3_client.delete_object(
                            Bucket=S3_BUCKET,
                            Key=old_cover_image
                        )
                        print(f"Deleted old cover image: {old_cover_image}")
                    except Exception as e:
                        print(f"Could not delete old image: {e}")

            except Exception as e:
                print(f"Error uploading to S3: {e}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"message": f"Error uploading image: {str(e)}"})
                }

        # Ako nema nove slike, zadrži staru
        final_cover_image = cover_image if cover_image else old_cover_image

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
            "coverImage": final_cover_image,
            "createdDate": existing_album.get('createdDate', str(datetime.now())),
            "modifiedDate": str(datetime.now()),
            "deleted": "false"
        }

        album_table.put_item(Item=updated_item)

        # Ukloni stare artist-album veze
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

        # Dodaj nove artist-album veze
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