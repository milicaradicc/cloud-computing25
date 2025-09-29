import json
import base64
import uuid
from datetime import datetime
import boto3
import traceback

BUCKET_NAME = "my-music-app-files"
SONG_TABLE = "Song"
ARTIST_SONG_TABLE = "ArtistSong"
SNS_TOPIC_ARN = "arn:aws:sns:eu-north-1:138881450188:NewContentTopic"

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
song_table = dynamodb.Table(SONG_TABLE)
artist_song_table = dynamodb.Table(ARTIST_SONG_TABLE)
sns = boto3.client("sns")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        filename = body['fileName']
        fileBase64 = body['fileBase64']
        artists = body.get('artists', [])
        genres = body.get('genres', [])
        single = body.get('single', False)
        album_id = body.get('album', 'Unknown')

        s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=base64.b64decode(fileBase64))
        print(f"Uploaded {filename} to S3 bucket {BUCKET_NAME}")

        song_id = str(uuid.uuid4())
        item = {
            "Album": album_id,
            "Id": song_id,
            "title": body['title'],
            "type": body.get('type', 'single'),
            "artists": artists,
            "genres": genres,
            "releaseDate": body.get('releaseDate', str(datetime.now())),
            "description": body.get('description', ''),
            "fileName": filename,
            "fileSize": body.get('fileSize'),
            "fileType": body.get('fileType'),
            "coverImage": body.get('coverImage'),
            "createdDate": str(datetime.now()),
            "modifiedDate": str(datetime.now()),
            "duration": body.get('duration'),
            "deleted": "false"
        }
        song_table.put_item(Item=item)

        # Artist -> song mapping
        for artist_id in artists:
            artist_song_table.put_item(Item={
                "ArtistId": artist_id,
                "SongId": song_id,
                "AlbumId": album_id,
                "createdDate": str(datetime.now())
            })

        # publish to SNS (event-driven)
        if single:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=json.dumps(item, default=str),
                MessageAttributes={
                    "contentType": {
                        "DataType": "String",
                        "StringValue": "song"
                    }
                },
                Subject="New Single"
            )
            print(f"Published single '{body['title']}' to SNS topic {SNS_TOPIC_ARN}")

        return {
            "statusCode": 201,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Song '{filename}' uploaded successfully.",
                "songId": song_id,
                "item": item
            }, default=str)
        }

    except Exception as e:
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }
