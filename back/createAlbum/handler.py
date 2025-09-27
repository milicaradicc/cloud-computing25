import json
import base64
import uuid
from datetime import datetime
import boto3

# Konstante
BUCKET_NAME = "my-music-app-files"
TABLE_NAME = "Album"  # tabela za albume sa Genre kao partition i Id kao sort

# AWS resursi
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    print("Claims:", claims)
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }
    try:
        body = json.loads(event.get('body', '{}'))
        album_title = body['title']
        genres = body.get('genres', [])
        cover_file_base64 = body.get('coverFileBase64')
        cover_filename = body.get('coverFileName')

        if not genres or len(genres) == 0:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Album must have at least one genre"})
            }

        # Upload cover image u S3 (ako postoji)
        if cover_file_base64 and cover_filename:
            cover_content = base64.b64decode(cover_file_base64)
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=cover_filename,
                Body=cover_content
            )
            print(f"Uploaded cover {cover_filename} to S3 bucket {BUCKET_NAME}")

        # Generisanje jedinstvenog ID-a albuma
        album_id = str(uuid.uuid4())
        primary_genre = genres[0]  # partition key

        # Kreiranje DynamoDB item-a
        item = {
            "Genre": primary_genre,    # partition key
            "Id": album_id,            # sort key
            "title": album_title,
            "artists": body.get('artists', []),
            "genres": genres,
            "releaseDate": body.get('releaseDate', str(datetime.now())),
            "description": body.get('description', ''),
            "coverImage": cover_filename,
            "createdDate": body.get('createdDate', str(datetime.now())),
            "modifiedDate": body.get('modifiedDate', str(datetime.now())),
            "deleted":"false"
        }

        # Upis u DynamoDB
        table.put_item(Item=item)
        print(f"Saved album '{album_title}' to DynamoDB table {TABLE_NAME}")

        return {
            "statusCode": 201,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"Album '{album_title}' uploaded and saved successfully.",
                "albumId": album_id,
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
