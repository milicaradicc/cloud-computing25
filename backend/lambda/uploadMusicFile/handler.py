import json
import base64
import uuid
from datetime import datetime
import boto3
import traceback
import os

BUCKET_NAME = os.environ["BUCKET_NAME"]
SONG_TABLE = os.environ["SONGS_TABLE"]
ARTIST_SONG_TABLE = os.environ["ARTIST_SONG_TABLE"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

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
        single = body.get('single')
        album_id = body.get('album', 'Unknown')

        # Upload pesme u S3
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
        print(song_id)
        # Artist → Song mapping
        for artist_id in artists:
            artist_song_table.put_item(Item={
                "ArtistId": artist_id,
                "SongId": song_id,
                "AlbumId": album_id,
                "createdDate": str(datetime.now())
            })

        # Publish SNS event SAMO ako je single
        print(f"Single: {single}")
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