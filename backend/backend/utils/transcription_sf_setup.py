import aws_cdk.aws_iam as iam

from backend.utils.create_lambda import create_lambda_function


def setup_transcription_sf(stack, transcription_bucket, music_bucket, songs_table):
    create_transcription_job_lambda = create_lambda_function(
            stack,
            "CreateTranscriptionJob",
            "handler.lambda_handler",
            "lambda/createTranscriptionJob",
            [],
            {
                'OUTPUT_BUCKET_NAME':transcription_bucket.bucket_name
            }
        )

    create_transcription_job_lambda.add_to_role_policy(
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:ListTranscriptionJobs",
                "transcribe:DeleteTranscriptionJob",
            ],
            resources=["*"],
        )
    )

    music_bucket.grant_read(create_transcription_job_lambda)
    transcription_bucket.grant_write(create_transcription_job_lambda)

    check_transcription_job_lambda = create_lambda_function(
        stack,
        "CheckTranscriptionJob",
        "handler.lambda_handler",
        "lambda/checkTranscriptionJob",
        [],
        {}
    )

    check_transcription_job_lambda.add_to_role_policy(
        iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "transcribe:ListTranscriptionJobs",
                "transcribe:DeleteTranscriptionJob",
            ],
            resources=["*"],
        )
    )

    transcription_bucket.grant_read(check_transcription_job_lambda)

    save_transcript_lambda = create_lambda_function(
        stack,
        "SaveTranscript",
        "handler.lambda_handler",
        "lambda/saveTranscript",
        [],
        {
            'SONGS_TABLE': songs_table.table_name,
            'SONGS_TABLE_PK': "Album",
            'SONGS_TABLE_SK': "Id"
        }
    )
    
    songs_table.grant_read_write_data(save_transcript_lambda)