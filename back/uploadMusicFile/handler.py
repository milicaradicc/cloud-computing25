import json
import base64
import boto3

s3 = boto3.client('s3')
BUCKET_NAME = "my-music-app-files"

def lambda_handler(event, context):
    try:
        print(event)
        file_content = base64.b64decode(event['body'])
        filename = event.get("queryStringParameters", {}).get("filename", "uploaded_file")

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=file_content
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"File '{filename}' uploaded successfully."})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
