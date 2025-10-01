from constructs import Construct

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_s3 as s3,
    aws_apigateway as apigateway
)

from backend.utils.create_lambda import create_lambda_function
from backend.utils.cognito_setup import setup_cognito

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
            removal_policy=RemovalPolicy.DESTROY
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

        # ARTIST ALBUM TABLE
        artist_album_table = dynamodb.Table(
            self, "ArtistAlbum",
            partition_key=dynamodb.Attribute(name="ArtistId", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="AlbumId", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
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

        # SNS
        topic = sns.Topic(
            self, "NewContentTopic",
            display_name="NewContentTopic"
        )
        # SQS Queue za pesme
        new_song_queue = sqs.Queue(
            self, "NewSongQueue",
            queue_name="NewSongQueue"
        )

        # SQS Queue za albume
        new_album_queue = sqs.Queue(
            self, "NewAlbumQueue",
            queue_name="NewAlbumQueue"
        )

        topic.add_subscription(subs.SqsSubscription(new_song_queue))
        topic.add_subscription(subs.SqsSubscription(new_album_queue))

        # Lambda for sending single email (triggers from NewSongQueue)
        send_single_email_lambda = create_lambda_function(
            self,
            "SendSingleEmail",
            "handler.lambda_handler",
            "lambda/sendSingleEmail",
            [],
            {
                "SUBSCRIPTIONS_TABLE": subscriptions_table.table_name,
            }
        )
        subscriptions_table.grant_read_data(send_single_email_lambda)

        send_single_email_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(new_song_queue)
        )

        # Lambda for sending general email (triggers from NewAlbumQueue)
        send_email_lambda = create_lambda_function(
            self,
            "SendAlbumEmail",
            "handler.lambda_handler",
            "lambda/sendAlbumEmail",
            [],
            {
                "SUBSCRIPTIONS_TABLE": subscriptions_table.table_name,
            }
        )
        subscriptions_table.grant_read_data(send_email_lambda)

        send_email_lambda.add_event_source(
            lambda_event_sources.SqsEventSource(new_album_queue)
        )

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

        # API constructs
        ArtistsConstruct(self, "ArtistsConstruct", api, artists_table, songs_table, albums_table, artist_album_table, artist_song_table, authorizer)
        SongsConstruct(self, "SongsConstruct", api, songs_table, albums_table, artist_song_table, music_bucket, topic,authorizer, artists_table, rating_table)
        AlbumConstruct(self, "AlbumConstruct", api, songs_table, albums_table, artist_album_table, music_bucket, topic,authorizer)
        SubscriptionsConstruct(self, "SubscriptionsConstruct", api, subscriptions_table, authorizer)