import aws_cdk.aws_iam as iam

from backend.utils.create_lambda import create_lambda_function
import aws_cdk.aws_stepfunctions as sfn
import aws_cdk.aws_stepfunctions_tasks as tasks
from aws_cdk import Duration



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

    create_job_task = tasks.LambdaInvoke(
            stack,
            "CreateTranscriptionJobTask",
            lambda_function=create_transcription_job_lambda,
            payload=sfn.TaskInput.from_object({
                "songId": sfn.JsonPath.string_at("$.songId"),
                "songFilePath": sfn.JsonPath.string_at("$.songFilePath")
            }),
            result_selector={
                "jobName": sfn.JsonPath.string_at("$.Payload.jobName")
            },
            result_path="$.createJobResult",
        )

    # Wait 3 seconds before checking status
    wait_state = sfn.Wait(
        stack,
        "WaitForTranscription",
        time=sfn.WaitTime.duration(Duration.seconds(3))
    )

    # Check transcript job status task
    check_job_task = tasks.LambdaInvoke(
        stack,
        "CheckTranscriptionJobTask",
        lambda_function=check_transcription_job_lambda,
        payload=sfn.TaskInput.from_object({
            "jobName": sfn.JsonPath.string_at("$.createJobResult.jobName")
        }),
        result_selector={
            "status": sfn.JsonPath.string_at("$.Payload.status"),
            "transcriptFilePath": sfn.JsonPath.string_at("$.Payload.transcriptFilePath")
        },
        result_path="$.checkJobResult",
    )

    # Save transcript task
    save_transcript_task = tasks.LambdaInvoke(
        stack,
        "SaveTranscriptTask",
        lambda_function=save_transcript_lambda,
        payload=sfn.TaskInput.from_object({
            "songId": sfn.JsonPath.string_at("$.songId"),
            "jobName": sfn.JsonPath.string_at("$.createJobResult.jobName")
        }),
        result_path="$.saveResult",
    )

    # Increment retry counter
    handle_failure = sfn.Pass(
        stack,
        "HandleFailure",
        parameters={
            "retryCount": sfn.JsonPath.math_add(
                sfn.JsonPath.number_at("$.retryCount"), 1
            )
        },
        result_path="$.retryInfo"
    )

    # Reset state for retry
    retry_job = sfn.Pass(
        stack,
        "RetryJob",
        parameters={
            "songId": sfn.JsonPath.string_at("$.songId"),
            "songFilePath": sfn.JsonPath.string_at("$.songFilePath"),
            "retryCount": sfn.JsonPath.number_at("$.retryInfo.retryCount")
        }
    )

    # Success state
    job_succeeded = sfn.Succeed(stack, "JobSucceeded")

    # Failure state
    job_failed = sfn.Fail(
        stack,
        "JobFailed",
        error="TranscriptionJobFailed",
        cause="The transcription job failed after maximum retries or encountered an error"
    )

    # Check retry limit
    check_retry_limit = sfn.Choice(stack, "CheckRetryLimit")
    check_retry_limit.when(
        sfn.Condition.number_less_than("$.retryInfo.retryCount", 5),
        retry_job.next(create_job_task)
    ).otherwise(job_failed)

    # Evaluate job status
    evaluate_status = sfn.Choice(stack, "EvaluateJobStatus")
    evaluate_status.when(
        sfn.Condition.string_equals("$.checkJobResult.status", "COMPLETED"),
        save_transcript_task.next(job_succeeded)
    ).when(
        sfn.Condition.string_equals("$.checkJobResult.status", "FAILED"),
        handle_failure.next(check_retry_limit)
    ).when(
        sfn.Condition.string_equals("$.checkJobResult.status", "IN_PROGRESS"),
        wait_state
    ).when(
        sfn.Condition.string_equals("$.checkJobResult.status", "QUEUED"),
        wait_state
    ).otherwise(wait_state)

    # Chain the states together
    definition = create_job_task.next(wait_state).next(check_job_task).next(evaluate_status)

    # Create the state machine
    state_machine = sfn.StateMachine(
        stack,
        "TranscriptionStateMachine",
        definition_body=sfn.DefinitionBody.from_chainable(definition),
        timeout=Duration.minutes(30),
    )

    # Add error handling with retries for Lambda invocations
    create_job_task.add_retry(
        errors=["Lambda.ServiceException", "Lambda.AWSLambdaException", 
                "Lambda.SdkClientException", "Lambda.TooManyRequestsException"],
        interval=Duration.seconds(2),
        max_attempts=3,
        backoff_rate=2.0
    )
    create_job_task.add_catch(
        job_failed,
        errors=["States.ALL"],
        result_path="$.error"
    )

    check_job_task.add_retry(
        errors=["Lambda.ServiceException", "Lambda.AWSLambdaException", 
                "Lambda.SdkClientException", "Lambda.TooManyRequestsException"],
        interval=Duration.seconds(2),
        max_attempts=3,
        backoff_rate=2.0
    )
    check_job_task.add_catch(
        job_failed,
        errors=["States.ALL"],
        result_path="$.error"
    )

    save_transcript_task.add_retry(
        errors=["Lambda.ServiceException", "Lambda.AWSLambdaException", 
                "Lambda.SdkClientException", "Lambda.TooManyRequestsException"],
        interval=Duration.seconds(2),
        max_attempts=3,
        backoff_rate=2.0
    )
    save_transcript_task.add_catch(
        job_failed,
        errors=["States.ALL"],
        result_path="$.error"
    )

    return state_machine