import os
import json
import boto3
from botocore.exceptions import ClientError

S3_BUCKET_NAME = os.environ.get('SONG_BUCKET_NAME')
SONGS_TABLE_NAME = os.environ.get('SONGS_TABLE')
CORS_ORIGIN = os.environ.get('CORS_ORIGIN', '*')

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


def lambda_handler(event, context):
    # Podrška za CORS preflight OPTIONS
    if event.get("httpMethod") == "OPTIONS":
        return _response(200, {})

    if not S3_BUCKET_NAME or not SONGS_TABLE_NAME:
        return _response(500, {'message': 'Server configuration error: Environment variables not set.'})

    # Čitanje song_id iz path ili query parametara
    song_id = None
    path_params = event.get('pathParameters')
    if path_params:
        # Ispravka: API Gateway šalje parametar kao "id", ne "songId"
        song_id = path_params.get('songId') or path_params.get('id')
    if not song_id:
        query_params = event.get('queryStringParameters')
        if query_params:
            song_id = query_params.get('songId')

    if not song_id:
        return _response(400, {'message': 'Song ID is required in path or query parameter.'})

    try:
        table = dynamodb.Table(SONGS_TABLE_NAME)

        # Dohvatanje pesme po GSI 'Id-index'
        response = table.query(
            IndexName='Id-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('Id').eq(song_id)
        )
        items = response.get('Items', [])
        if not items:
            return _response(404, {'message': f'Song with ID {song_id} not found.'})

        song_item = items[0]
        s3_key = song_item.get('fileName')
        song_title = song_item.get('title', 'UnknownSong')

        if not s3_key:
            return _response(500, {'message': 'Song metadata error: S3 Filename not found.'})

        file_name_for_download = f"{song_title}.mp3"
        presigned_url = s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': S3_BUCKET_NAME,
                'Key': s3_key,
                'ResponseContentDisposition': f'attachment; filename="{file_name_for_download}"'
            },
            ExpiresIn=300  # 5 minuta
        )

        return _response(200, {'url': presigned_url, 'filename': file_name_for_download})

    except ClientError as e:
        print(f"DynamoDB Client Error: {e}")
        return _response(500, {'message': 'Failed to retrieve song data (ClientError).', 'errorDetail': str(e)})

    except Exception as e:
        print(f"General Error: {e}")
        return _response(500, {'message': 'Failed to generate download link.', 'errorDetail': str(e)})


def _response(status_code, body_dict):
    """Helper function za response sa CORS header-ima"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': CORS_ORIGIN,
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        },
        'body': json.dumps(body_dict)
    }
