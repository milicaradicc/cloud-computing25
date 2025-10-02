import json
import os
import boto3
from botocore.exceptions import ClientError

# Inicijalizacija S3 klijenta
s3_client = boto3.client('s3', region_name='eu-central-1')
BUCKET_NAME = 'backendstack-mymusicappfilesac4e028d-dvynytregsi6'

def lambda_handler(event, context):
    # Pretpostavljamo da je songId poslat kao path parameter: /songs/{songId}/presigned-url
    song_id = event.get('pathParameters', {}).get('id')
    
    if not song_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing songId'})
        }

    # Key fajla u S3
    file_key = f"{song_id}.mp3"  # promeni ako je drugačiji format ili folder

    try:
        # Generisanje Presigned URL-a sa 5 minuta (300 sekundi) trajanja
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_key},
            ExpiresIn=300  # trajanje u sekundama
        )
    except ClientError as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Could not generate presigned URL'})
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # za razvoj, u produkciji stavi frontend URL
        },
        'body': json.dumps({'url': presigned_url})
    }
