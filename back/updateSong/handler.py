import json
import base64
import boto3
from datetime import datetime
from decimal import Decimal

BUCKET_NAME = "my-music-app-files"
SONG_TABLE = "Song"
ARTIST_SONG_TABLE = "ArtistSong"

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
song_table = dynamodb.Table(SONG_TABLE)
artist_song_table = dynamodb.Table(ARTIST_SONG_TABLE)

def convert_to_dynamodb_types(obj):
    if isinstance(obj, dict):
        return {k: convert_to_dynamodb_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_dynamodb_types(v) for v in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, int):
        return Decimal(obj)
    else:
        return obj

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": "Forbidden"})
        }

    try:
        body = json.loads(event.get('body', '{}'))

        if 'Id' not in body or 'Album' not in body:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing required fields: Id and Album"})
            }

        song_id = str(body['Id'])
        album = str(body['Album'])

        response = song_table.get_item(
            Key={'Album': album, 'Id': song_id}
        )

        item = response.get('Item')
        if not item:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Song not found"})
            }

        # handle file upload if provided
        filename = body.get('fileName')
        fileBase64 = body.get('fileBase64')

        if filename and fileBase64:
            try:
                file_content = base64.b64decode(fileBase64)

                content_type = 'audio/mpeg'
                if filename.lower().endswith('.mp3'):
                    content_type = 'audio/mpeg'
                elif filename.lower().endswith('.wav'):
                    content_type = 'audio/wav'
                elif filename.lower().endswith('.flac'):
                    content_type = 'audio/flac'

                s3.put_object(
                    Bucket=BUCKET_NAME,
                    Key=filename,
                    Body=file_content,
                    ContentType=content_type
                )

                item['fileName'] = filename
                if 'fileSize' in body:
                    item['fileSize'] = body['fileSize']
                if 'fileType' in body:
                    item['fileType'] = body['fileType']
                if 'duration' in body:
                    item['duration'] = body['duration']

            except Exception as e:
                print(f"S3 upload error: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": f"File upload failed: {str(e)}"})
                }

        if 'title' in body:
            item['title'] = str(body['title'])
        if 'description' in body:
            item['description'] = str(body['description'])
        if 'coverImage' in body:
            item['coverImage'] = str(body['coverImage'])
        if 'genres' in body:
            item['genres'] = body['genres']

        item['modifiedDate'] = datetime.now().isoformat()

        item = convert_to_dynamodb_types(item)

        song_table.put_item(Item=item)

        new_artists = body.get('artists')
        if new_artists is not None:
            try:
                old_artists = item.get('artists', [])

                for artist_id in old_artists:
                    try:
                        artist_song_table.delete_item(
                            Key={'ArtistId': str(artist_id), 'SongId': song_id}
                        )
                    except Exception as e:
                        print(f"Warning: Failed to delete artist association {artist_id}: {str(e)}")

                for artist_id in new_artists:
                    artist_song_table.put_item(Item={
                        'ArtistId': str(artist_id),
                        'SongId': song_id,
                        'AlbumId': album,
                        'createdDate': datetime.now().isoformat()
                    })

                item['artists'] = [str(artist_id) for artist_id in new_artists]

                item = convert_to_dynamodb_types(item)
                song_table.put_item(Item=item)

            except Exception as e:
                print(f"Artist update error: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": f"Artist update failed: {str(e)}"})
                }

        def convert_decimals(obj):
            if isinstance(obj, list):
                return [convert_decimals(v) for v in obj]
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, Decimal):
                return float(obj) if obj % 1 != 0 else int(obj)
            else:
                return obj

        response_item = convert_decimals(item)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": "Song updated successfully",
                "item": response_item
            })
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }

    except Exception as e:
        import traceback
        error_msg = str(e)
        print("ERROR:", error_msg)
        print(traceback.format_exc())

        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": f"Internal server error: {error_msg}"})
        }