import json
import os
import boto3
import uuid
import os
from urllib.request import urlopen


def lambda_handler(event, context):
    transcribe = boto3.client('transcribe')
    job_name = event.get('jobName')

    response = transcribe.get_transcription_job(
        TranscriptionJobName=job_name
    )
    
    job = response['TranscriptionJob']
    job_status = job['TranscriptionJobStatus']

    if job_status != 'COMPLETED':
        return {'status': job_status,
                'transcriptFilePath': None }
    
    transcript_uri = job['Transcript']['TranscriptFileUri']
    
    with urlopen(transcript_uri) as response:
        transcript_data = json.loads(response.read().decode('utf-8'))

    transcript = transcript_data['results']['transcripts'][0]['transcript']

    if transcript=="":
        return {'status': 'FAILED',
                'transcriptFilePath': None }
    
    return {
        'status': 'COMPLETED',
        'transcriptFilePath': transcript_uri
    }
