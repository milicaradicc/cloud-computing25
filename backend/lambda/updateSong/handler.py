import json
import base64
import os
from datetime import datetime
from decimal import Decimal

import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource("dynamodb")
songs_table_name = os.environ["SONGS_TABLE"]
albums_table_name = os.environ["ALBUMS_TABLE"]
bucket_name = os.environ["BUCKET_NAME"]

SNS_NEW_TRANSCRIPTION_TOPIC_ARN = os.environ["SNS_NEW_TRANSCRIPTION_ARN"]
sns = boto3.client("sns")

songs_table = dynamodb.Table(songs_table_name)
albums_table = dynamodb.Table(albums_table_name)


def convert_to_dynamodb_types(obj, path="root"):
    if isinstance(obj, dict):
        return {k: convert_to_dynamodb_types(v, f"{path}.{k}") for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_dynamodb_types(v, f"{path}[{i}]") for i, v in enumerate(obj)]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, bool):
        return obj
    elif isinstance(obj, str):
        return obj
    elif obj is None:
        return obj
    elif isinstance(obj, (float, int)):
        return Decimal(str(obj))
    else:
        return str(obj)


def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 != 0 else int(obj)
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
        print("Received body:", json.dumps(body, default=str))

        if 'Id' not in body or 'Album' not in body:
            return {
                "statusCode": 400,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Missing required fields: Id and Album"})
            }

        song_id = str(body['Id'])
        album = str(body['Album']['Id'])

        response = songs_table.get_item(Key={'Album': album, 'Id': song_id})
        item = response.get('Item')
        if not item:
            return {
                "statusCode": 404,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"error": "Song not found"})
            }

        filename = body.get('fileName')
        fileBase64 = body.get('fileBase64')

        if filename and fileBase64:
            try:
                file_content = base64.b64decode(fileBase64)
                content_type = 'audio/mpeg'
                if filename.lower().endswith('.wav'):
                    content_type = 'audio/wav'
                elif filename.lower().endswith('.flac'):
                    content_type = 'audio/flac'

                s3.put_object(
                    Bucket=bucket_name,
                    Key=filename,
                    Body=file_content,
                    ContentType=content_type
                )
                print(f"Uploaded audio file: {filename}")

                item['fileName'] = filename
                item['fileType'] = body.get('fileType', item.get('fileType'))
                item['fileSize'] = body.get('fileSize', item.get('fileSize'))
                item['duration'] = body.get('duration', item.get('duration'))

                if item.get('transcribe'):
                    item['transcriptFileName'] = ''
                    sns.publish(
                        TopicArn=SNS_NEW_TRANSCRIPTION_TOPIC_ARN,
                        Message=json.dumps(item, default=str),
                        MessageAttributes={
                            "songId": {
                                "DataType": "String",
                                "StringValue": song_id
                            },
                            "songFileName": {
                                "DataType": "String",
                                "StringValue": filename
                            }
                        },
                        Subject="New Transcription Request"
                    )

            except Exception as e:
                print(f"S3 audio upload error: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": f"Audio upload failed: {str(e)}"})
                }

        cover_filename = body.get('coverImage')
        coverBase64 = body.get('coverBase64')

        if cover_filename and coverBase64:
            try:
                cover_content = base64.b64decode(coverBase64)
                content_type = 'image/jpeg'
                if cover_filename.lower().endswith('.png'):
                    content_type = 'image/png'
                elif cover_filename.lower().endswith('.jpg') or cover_filename.lower().endswith('.jpeg'):
                    content_type = 'image/jpeg'
                elif cover_filename.lower().endswith('.gif'):
                    content_type = 'image/gif'

                s3.put_object(
                    Bucket=bucket_name,
                    Key=cover_filename,
                    Body=cover_content,
                    ContentType=content_type
                )
                print(f"Uploaded cover image: {cover_filename}")

                item['coverImage'] = cover_filename

            except Exception as e:
                print(f"S3 cover upload error: {str(e)}")
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": f"Cover upload failed: {str(e)}"})
                }

        if 'title' in body:
            item['title'] = str(body['title'])
        if 'description' in body:
            item['description'] = str(body['description'])
        if 'genres' in body:
            item['genres'] = body['genres']

        item['modifiedDate'] = datetime.now().isoformat()

        print("Item before conversion:", json.dumps(item, default=str))
        item = convert_to_dynamodb_types(item)
        songs_table.put_item(Item=item)
        print("Item saved successfully")

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
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": f"Internal server error: {str(e)}"})
        }
