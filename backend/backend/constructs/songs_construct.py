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
        authorizer,
        artists_table: dynamodb.Table,
        rating_table: dynamodb.Table,
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
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name,
                "BUCKET_NAME": bucket.bucket_name,
            }
        )
        table.grant_read_write_data(update_song_lambda)
        albums_table.grant_read_write_data(update_song_lambda)
        artist_song_table.grant_read_write_data(update_song_lambda)
        bucket.grant_read_write(update_song_lambda)

        song_id_resource = songs_api_resource.add_resource("{id}")
        song_id_resource.add_method(
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
        table.grant_read_write_data(delete_song_lambda)
        albums_table.grant_read_write_data(delete_song_lambda)

        # /songs/{id} → DELETE
        song_id_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Song by Id
        get_song_lambda = create_lambda_function(
            self,
            "GetSongLambda",
            "handler.lambda_handler",
            "lambda/getSong",
            [],  # lambda environment variables if any additional
            {
                "SONGS_TABLE": table.table_name,
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTISTS_TABLE": artists_table.table_name
            }
        )

        table.grant_read_data(get_song_lambda)
        albums_table.grant_read_data(get_song_lambda)
        artists_table.grant_read_data(get_song_lambda)

        song_id_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        rating_resource = song_id_resource.add_resource("rating")

        # Rate Song Lambda (POST /songs/{songId}/rating)
        rate_song_lambda = create_lambda_function(
            self,
            "RateSongLambda",
            "handler.lambda_handler",
            "lambda/rateSong",
            [],
            {
                "RATING_TABLE": rating_table.table_name,
            }
        )
        rating_table.grant_read_write_data(rate_song_lambda)

        rating_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(rate_song_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Song Rating Lambda (GET /songs/{songId}/rating?userId=xxx)
        get_song_rating_lambda = create_lambda_function(
            self,
            "GetSongRatingLambda",
            "handler.lambda_handler",
            "lambda/getSongRating",
            [],
            {
                "RATING_TABLE": rating_table.table_name,
            }
        )
        rating_table.grant_read_data(get_song_rating_lambda)

        rating_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_song_rating_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
