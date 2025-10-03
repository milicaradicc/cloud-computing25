import json
import os
import boto3

MUSIC_BUCKET_NAME = os.environ["MUSIC_BUCKET_NAME"]
TRANSCRIPTION_STEP_FUNCTION_ARN = os.environ["TRANSCRIPTION_STEP_FUNCTION_ARN"]

sfn_client = boto3.client("stepfunctions")


def lambda_handler(event, context):
    for record in event["Records"]:
        sns_envelope = json.loads(record["body"])
        message = json.loads(sns_envelope["Message"])
        attributes = sns_envelope.get("MessageAttributes", {})

        song_id = attributes.get("songId", {}).get("Value")
        file_path = attributes.get("songFileName", {}).get("Value")

        step_input = {
            "songId": song_id,
            "songFilePath": f"s3://{MUSIC_BUCKET_NAME}/{file_path}",
            "retryCount": 0
        }

        sfn_client.start_execution(
            stateMachineArn=TRANSCRIPTION_STEP_FUNCTION_ARN,
            input=json.dumps(step_input)
        )


