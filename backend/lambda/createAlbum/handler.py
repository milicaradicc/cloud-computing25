import json
import base64
import uuid
from datetime import datetime
import boto3
import traceback
import os

BUCKET_NAME = os.environ["BUCKET_NAME"]
TABLE_NAME = os.environ["ALBUMS_TABLE"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
ARTIST_ALBUM_TABLE = os.environ["ARTIST_ALBUM_TABLE"]

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)
sns = boto3.client("sns")
artist_album_table = dynamodb.Table(ARTIST_ALBUM_TABLE)

CORS_HEADERS = {"Access-Control-Allow-Origin": "*"}

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': CORS_HEADERS,
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event.get('body', '{}'))
        album_title = body['title']
        genres = body.get('genres', [])
        cover_file_base64 = body.get('coverFileBase64')
        cover_filename = body.get('coverFileName')
        single = body.get('single')

        if not genres or len(genres) == 0:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "Album must have at least one genre"})
            }

        if cover_file_base64 and cover_filename:
            cover_content = base64.b64decode(cover_file_base64)
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=cover_filename,
                Body=cover_content
            )

        album_id = str(uuid.uuid4())
        primary_genre = genres[0]

        item = {
            "Genre": primary_genre,    
            "Id": album_id,            
            "title": album_title,
            "artists": body.get('artists', []),
            "genres": genres,
            "releaseDate": body.get('releaseDate', str(datetime.now())),
            "description": body.get('description', ''),
            "coverImage": cover_filename,
            "createdDate": str(datetime.now()),
            "modifiedDate": str(datetime.now()),
            "deleted":"false"
        }

        table.put_item(Item=item)

        artists = body.get('artists', [])
        for artist_id in artists:
            artist_album_table.put_item(
                Item={
                    "ArtistId": artist_id,
                    "AlbumId": album_id,
                    "createdDate": str(datetime.now())
                }
            )

        # Publish SNS event SAMO ako NIJE single
        if not single:
            try:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=json.dumps(item, default=str),
                    MessageAttributes={
                        "contentType": {
                            "DataType": "String",
                            "StringValue": "album"
                        }
                    },
                    Subject="New Album"
                )
            except Exception as sns_err:
                print("SNS Publish ERROR:", str(sns_err))
                print(traceback.format_exc())

        return {
            "statusCode": 201,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"Album '{album_title}' uploaded and saved successfully.",
                "albumId": album_id,
                "item": item
            }, default=str)
        }

    except Exception as e:
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"error": str(e)})
        }
