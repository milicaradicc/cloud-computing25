import json
import base64
import boto3

BUCKET_NAME = "my-music-app-files"

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')


def lambda_handler(event, context):
    try:
        # Dobijamo DTO sa frontenda
        body = json.loads(event['body'])
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

        response = lambda_client.invoke(
            FunctionName="arn:aws:lambda:eu-north-1:138881450188:function:uploadMusicDynamo",
            InvocationType="RequestResponse",  # synchronous
            Payload=json.dumps(body)
        )

        # Pročitamo odgovor druge Lambda
        response_payload = json.loads(response['Payload'].read())
        print("Response from uploadMusicDynamo:", response_payload)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "message": f"File '{filename}' uploaded successfully.",
                "dynamoResponse": response_payload
            })
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
