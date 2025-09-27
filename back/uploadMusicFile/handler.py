import json
import base64
import uuid
from datetime import datetime
import boto3

# Konstante
BUCKET_NAME = "my-music-app-files"
TABLE_NAME = "Song"  # nova tabela sa Album kao partition i Id kao sort

# AWS resursi
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        # Parsiranje DTO sa frontenda
        body = json.loads(event.get('body', '{}'))
        filename = body['fileName']
        fileBase64 = body['fileBase64']

        # Upload fajla u S3
        file_content = base64.b64decode(fileBase64)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )
        print(f"Uploaded {filename} to S3 bucket {BUCKET_NAME}")

        # Generisanje jedinstvenog ID-a pesme
        song_id = str(uuid.uuid4())

        # Kreiranje DynamoDB item-a
        item = {
            "Album": body.get('album', 'Unknown'),  # partition key
            "Id": song_id,                           # sort key
            "title": body['title'],
            "type": body.get('type', 'single'),
            "artists": body['artists'],
            "genres": body.get('genres', []),
            "releaseDate": body.get('releaseDate', str(datetime.now())),
            "description": body.get('description', ''),
            "fileName": filename,
            "fileSize": body.get('fileSize'),
            "fileType": body.get('fileType'),
            "coverImage": body.get('coverImage'),
            "createdDate": body.get('createdDate', str(datetime.now())),
            "modifiedDate": body.get('modifiedDate', str(datetime.now())),
            "duration": body.get('duration'),
            "deleted":"false"
        }

        # Upis u DynamoDB
        table.put_item(Item=item)
        print(f"Saved metadata for {filename} to DynamoDB table {TABLE_NAME}")

        # Vraćanje uspešnog odgovora
        return {
            "statusCode": 201,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"File '{filename}' uploaded and metadata saved successfully.",
                "songId": song_id,
                "item": item
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
