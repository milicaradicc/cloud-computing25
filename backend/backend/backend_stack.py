from constructs import Construct

from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_apigateway as apigateway,
    aws_iam as iam,
    Duration,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
)

from backend.utils.create_lambda import create_lambda_function
from backend.utils.cognito_setup import setup_cognito
from backend.utils.transcription_sf_setup import setup_transcription_sf

from backend.constructs.songs_construct import SongsConstruct
from backend.constructs.albums_construct import AlbumConstruct
from backend.constructs.artists_construct import ArtistsConstruct
from backend.constructs.subscriptions_construct import SubscriptionsConstruct

class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        music_bucket = s3.Bucket(
            self, "my-music-app-files",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=False,
                ignore_public_acls=True,
                restrict_public_buckets=False
            ),
            public_read_access=True,
            website_index_document="index.html",
            website_error_document="error.html"
        )

        CfnOutput(
            self,
            "MusicBucketURL",
            value=f"https://{music_bucket.bucket_name}.s3.{self.region}.amazonaws.com/",
            description="Music Bucket URL",
        )

        # ARISTS TABLE AND GSI
        artists_table = dynamodb.Table(
            self, "Artists",
            partition_key=dynamodb.Attribute(name="Genre", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table.add_global_secondary_index(
            index_name="deleted-index",
            partition_key=dynamodb.Attribute(name="deleted", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        artists_table.add_global_secondary_index(
            index_name="Id-index",
            partition_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # SONGS TABLE AND GSI
        songs_table = dynamodb.Table(
            self, "Songs",
            partition_key=dynamodb.Attribute(name="Album", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        songs_table.add_global_secondary_index(
            index_name="deleted-index",
            partition_key=dynamodb.Attribute(name="deleted", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        songs_table.add_global_secondary_index(
            index_name="Album-index",
            partition_key=dynamodb.Attribute(name="Album", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        songs_table.add_global_secondary_index(
            index_name="Id-index",
            partition_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # ALBUMS TABLE AND GSI
        albums_table = dynamodb.Table(
            self, "Albums",
            partition_key=dynamodb.Attribute(name="Genre", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        albums_table.add_global_secondary_index(
            index_name="deleted-index",
            partition_key=dynamodb.Attribute(name="deleted", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        albums_table.add_global_secondary_index(
            index_name="Id-index",
            partition_key=dynamodb.Attribute(name="Id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # ARTIST SONG TABLE
        artist_song_table = dynamodb.Table(
            self, "ArtistSong",
            partition_key=dynamodb.Attribute(name="ArtistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SongId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        artist_song_table.add_global_secondary_index(
            index_name="AlbumId-index",
            partition_key=dynamodb.Attribute(name="AlbumId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="ArtistId", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )


        # ARTIST ALBUM TABLE
        artist_album_table = dynamodb.Table(
            self, "ArtistAlbum",
            partition_key=dynamodb.Attribute(name="ArtistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="AlbumId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        artist_album_table.add_global_secondary_index(
            index_name="AlbumId-index",
            partition_key=dynamodb.Attribute(name="AlbumId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="ArtistId", type=dynamodb.AttributeType.STRING),  # opcionalno
            projection_type=dynamodb.ProjectionType.ALL
        )


        # RATING TABLE
        rating_table = dynamodb.Table(
            self, "Ratings",
            partition_key=dynamodb.Attribute(name="User", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Song", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        # SUBSCRIPTIONS TABLE
        subscriptions_table = dynamodb.Table(
            self, "Subscriptions",
            partition_key=dynamodb.Attribute(name="Target", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="User", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        subscriptions_table.add_global_secondary_index(
            index_name="id-index",
            partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )

        subscriptions_table.add_global_secondary_index(
            index_name="User-index",
            partition_key=dynamodb.Attribute(name="User", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL
        )


        user_pool, user_pool_client = setup_cognito(self)

        # SNS :(
        new_content_topic = sns.Topic(
            self, "NewContentTopic",
            display_name="NewContentTopic"
        )
        # SQS Queue
        new_content_queue = sqs.Queue(
            self, "NewContentQueue",
            queue_name="NewContentQueue"
        )

        new_content_topic.add_subscription(subs.SqsSubscription(new_content_queue))

        send_email_lambda = create_lambda_function(
            self,
            "SendEmail",
            "handler.lambda_handler",
            "lambda/sendEmail",
            [],
            {
                "SUBSCRIPTIONS_TABLE": subscriptions_table.table_name,
                "SES_REGION": "eu-central-1",
                "SES_SOURCE_EMAIL": "milica.t.radic@gmail.com"
            }
        )

        subscriptions_table.grant_read_data(send_email_lambda)

        send_email_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(new_content_queue)
        )

        send_email_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=["*"]
            )
        )

        transcription_bucket = s3.Bucket(
            self, "my-music-app-transcriptions",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=False,
                ignore_public_acls=True,
                restrict_public_buckets=False
            ),
            public_read_access=True,
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.GET],
                    allowed_origins=["*"],
                    allowed_headers=["*"]
                )
            ]
        )

        CfnOutput(
            self,
            "TranscriptionBucketURL",
            value=f"https://{transcription_bucket.bucket_name}.s3.{self.region}.amazonaws.com/",
            description="Transcription Bucket URL",
        )

        state_machine = setup_transcription_sf(self, transcription_bucket, music_bucket, songs_table)

        new_transcription_topic = sns.Topic(
            self, "NewTranscriptionTopic",
            display_name="NewTranscriptionTopic"
        )
        # SQS Queue
        new_transcription_queue = sqs.Queue(
            self, "NewTranscriptionQueue",
            queue_name="NewTranscriptionQueue"
        )

        new_transcription_topic.add_subscription(subs.SqsSubscription(new_transcription_queue))

        handle_new_transcription_lambda = create_lambda_function(
            self,
            "HandleNewTranscription",
            "handler.lambda_handler",
            "lambda/handleNewTranscription",
            [],
            {
                "MUSIC_BUCKET_NAME": music_bucket.bucket_name,
                "TRANSCRIPTION_STEP_FUNCTION_ARN": state_machine.state_machine_arn
            }
        )

        handle_new_transcription_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(new_transcription_queue)
        )

        state_machine.grant_start_execution(handle_new_transcription_lambda)

        # API
        api = apigateway.RestApi(
            self, "MusicStreamingApi",
            rest_api_name="MusicStreamingApi",
            deploy_options=apigateway.StageOptions(stage_name="dev", throttling_rate_limit=100, throttling_burst_limit=200),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            )
        )

        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
        )

        # API constructs (sve Artists rute idu preko ArtistsConstruct!)
        ArtistsConstruct(self, "ArtistsConstruct", api, artists_table, songs_table, albums_table, artist_album_table, artist_song_table, authorizer)
        SongsConstruct(self, "SongsConstruct", api, songs_table, albums_table, artist_song_table, music_bucket, new_content_topic, new_transcription_topic, authorizer, artists_table, rating_table)
        AlbumConstruct(self, "AlbumConstruct", api, songs_table, albums_table, artist_album_table, artist_song_table, artists_table, music_bucket, new_content_topic, authorizer)
        SubscriptionsConstruct(self, "SubscriptionsConstruct", api, subscriptions_table, authorizer)

        # FILTERS
        filter_api_resource = api.root.add_resource("discover").add_resource("filter")

        get_filtered_lambda = create_lambda_function(
            self,
            "GetFilteredContentLambda",
            "handler.lambda_handler",
            "lambda/filterByGenre",
            [],
            environment={
                'ARTISTS_TABLE': artists_table.table_name,
                'ALBUMS_TABLE': albums_table.table_name
            }
        )
        artists_table.grant_read_data(get_filtered_lambda)
        albums_table.grant_read_data(get_filtered_lambda)

        get_filtered_integration = apigateway.LambdaIntegration(get_filtered_lambda, proxy=True)

        filter_api_resource.add_method("GET", get_filtered_integration)

        # DOWNLOAD
        generate_download_lambda = create_lambda_function(
            self,
            "GenerateDownloadUrlLambda",
            "handler.lambda_handler",
            "lambda/downloadSong",
            [],
            environment={
                "SONG_BUCKET_NAME": music_bucket.bucket_name,
                "SONGS_TABLE": songs_table.table_name,
                "CORS_ORIGIN": "*",
            }
        )

        music_bucket.grant_read(generate_download_lambda)
        songs_table.grant_read_data(generate_download_lambda)

        download_resource = api.root.add_resource("download")
        download_id_resource = download_resource.add_resource("{songId}")

        download_integration = apigateway.LambdaIntegration(generate_download_lambda, proxy=True)

        download_id_resource.add_method(
            "GET",
            download_integration,
            authorization_type=apigateway.AuthorizationType.NONE,
        )

        # OFFLINE LISTENING
        songs_resource = api.root.get_resource("songs")
        song_id_resource = songs_resource.get_resource("{id}")

        presigned_resource = song_id_resource.add_resource("presigned-url")

        presigned_integration = apigateway.LambdaIntegration(
            generate_download_lambda,
            proxy=True
        )

        presigned_resource.add_method(
            "GET",
            presigned_integration,
            authorization_type=apigateway.AuthorizationType.NONE
        )
