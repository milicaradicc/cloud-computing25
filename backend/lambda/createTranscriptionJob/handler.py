import json
import os
import boto3
import uuid
import os


def lambda_handler(event, context):
    song_file_path = event['songFilePath']
    song_id = event['songId']
    transcribe = boto3.client('transcribe')

    job_name = str(uuid.uuid4())
    output_bucket = os.environ['OUTPUT_BUCKET_NAME']
    
    job_params = {
        'TranscriptionJobName': job_name,
        'Media': {
            'MediaFileUri': song_file_path
        },
        'OutputBucketName': output_bucket,
        'IdentifyLanguage': True,
    }
        
    transcribe.start_transcription_job(**job_params)

    return {
        'songId': song_id,
        'songFilePath': song_file_path,
        'jobName': job_name
    }