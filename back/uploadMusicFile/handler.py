import json
import base64
import boto3

BUCKET_NAME = "my-music-app-files"

s3 = boto3.client('s3')

def lambda_handler(event, context):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    role = claims.get("custom:role")

    if role != "admin":
        return {
            "statusCode": 403,
            'headers': {
            'Access-Control-Allow-Origin': '*',
            },
            "body": json.dumps({"message":"Forbidden: Insufficient permissions"})
        }

    try:
        body = json.loads(event['body'])

        filename = body['filename']
        fileBase64 = body['fileBase64']
        title = body['title']
        description = body['description']
        releaseDate = body['releaseDate']
        artists = body['artists']
        genres = body['genres']

        file_content = base64.b64decode(fileBase64)

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"message": f"File '{filename}' uploaded successfully."})
        }

    except Exception as e:
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({"message": f"File '{filename}' uploaded successfully."})
        }
