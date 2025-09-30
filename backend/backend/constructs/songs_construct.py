from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_s3 as s3,
    aws_dynamodb as dynamodb
)
from backend.utils.create_lambda import create_lambda_function

class SongsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        table: dynamodb.Table,
        albums_table: dynamodb.Table,
        artist_song_table: dynamodb.Table,
        bucket: s3.Bucket,
        topic: sns.Topic,
        authorizer
    ):
        super().__init__(scope, id)

        songs_api_resource = api.root.add_resource("songs")

        # Create Song
        create_song_lambda = create_lambda_function(
            self,
            "UploadFileLambda",
            "handler.lambda_handler",
            "lambda/uploadMusicFile",
            [],
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "SONGS_TABLE": table.table_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name,
                "SNS_TOPIC_ARN": topic.topic_arn,
            }
        )
        bucket.grant_read_write(create_song_lambda)
        table.grant_write_data(create_song_lambda)
        artist_song_table.grant_write_data(create_song_lambda)
        topic.grant_publish(create_song_lambda)

        songs_api_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Songs
        get_songs_lambda = create_lambda_function(
            self,
            "GetSongsLambda",
            "handler.lambda_handler",
            "lambda/getSongs",
            [],
            {"SONGS_TABLE": table.table_name}
        )
        table.grant_read_data(get_songs_lambda)

        songs_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_songs_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Update Song
        update_song_lambda = create_lambda_function(
            self,
            "UpdateSongLambda",
            "handler.lambda_handler",
            "lambda/updateSong",
            [],
            {
                "SONGS_TABLE": table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name
            }
        )
        table.grant_read_write_data(update_song_lambda)
        bucket.grant_read_write(update_song_lambda)
        artist_song_table.grant_read_write_data(update_song_lambda)

        songs_api_resource.add_method(
            "PUT",
            apigateway.LambdaIntegration(update_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Delete Song
        delete_song_lambda = create_lambda_function(
            self,
            "DeleteSongLambda",
            "handler.lambda_handler",
            "lambda/deleteSong",
            [],
            {
                "SONGS_TABLE": table.table_name,
                "ALBUMS_TABLE": albums_table.table_name
            }
        )
        table.grant_write_data(delete_song_lambda)
        albums_table.grant_write_data(delete_song_lambda)

        # /songs/{id} → DELETE
        song_id_resource = songs_api_resource.add_resource("{id}")
        song_id_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
