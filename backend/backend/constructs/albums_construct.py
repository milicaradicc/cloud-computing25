from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam
)

from backend.utils.create_lambda import create_lambda_function

class AlbumConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        songs_table: dynamodb.Table,
        albums_table: dynamodb.Table,
        artist_album_table: dynamodb.Table,
        artist_song_table: dynamodb.Table,  
        artists_table: dynamodb.Table, 
        bucket: s3.Bucket,
        topic: sns.Topic,
        authorizer
    ):
        super().__init__(scope, id)

        albums_api_resource = api.root.add_resource("albums")

        # Create Album
        create_album_lambda = create_lambda_function(
            self,
            "CreateAlbumLambda",
            "handler.lambda_handler",
            "lambda/createAlbum",
            [],
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTIST_ALBUM_TABLE": artist_album_table.table_name,
                "SNS_TOPIC_ARN": topic.topic_arn,
            }
        )
        bucket.grant_read_write(create_album_lambda)
        # Changed from grant_write_data to grant_read_write_data
        albums_table.grant_read_write_data(create_album_lambda)
        artist_album_table.grant_read_write_data(create_album_lambda)
        topic.grant_publish(create_album_lambda)

        albums_api_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_album_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Albums
        get_albums_lambda = create_lambda_function(
            self,
            "GetAlbumsLambda",
            "handler.lambda_handler",
            "lambda/getAlbums",
            [],
            {"ALBUMS_TABLE": albums_table.table_name,
             "ARTISTS_TABLE": artists_table.table_name,}
        )
        albums_table.grant_read_data(get_albums_lambda)
        artists_table.grant_read_data(get_albums_lambda)

        albums_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_albums_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Update Album
        update_album_lambda = create_lambda_function(
            self,
            "UpdateAlbumLambda",
            "handler.lambda_handler",
            "lambda/updateAlbum",
            [],
            {
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTIST_ALBUM_TABLE": artist_album_table.table_name,
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        albums_table.grant_read_write_data(update_album_lambda)
        artist_album_table.grant_read_write_data(update_album_lambda)
        bucket.grant_read_write(update_album_lambda)

        # /albums/{id} → PUT
        album_id_resource = albums_api_resource.add_resource("{id}")
        album_id_resource.add_method(
            "PUT",
            apigateway.LambdaIntegration(update_album_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Delete Album
        delete_album_lambda = create_lambda_function(
            self,
            "DeleteAlbumLambda",
            "handler.lambda_handler",
            "lambda/deleteAlbum",
            [],
            {
                "SONGS_TABLE": songs_table.table_name,
                "ALBUMS_TABLE": albums_table.table_name
            }
        )
        # Changed from grant_write_data to grant_read_write_data
        songs_table.grant_read_write_data(delete_album_lambda)
        albums_table.grant_read_write_data(delete_album_lambda)

        # /albums/{id} → DELETE
        album_id_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_album_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Album by Id
        get_album_lambda = create_lambda_function(
            self,
            "GetAlbumByIdLambda",
            "handler.lambda_handler",
            "lambda/getAlbumById",
            [],
            environment={
                "ALBUMS_TABLE": albums_table.table_name,
                "SONGS_TABLE": songs_table.table_name,
                "ARTIST_ALBUM_TABLE": artist_album_table.table_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name,  
                "ARTISTS_TABLE": artists_table.table_name           
            }
        )

        # Policy za AlbumId-index
        get_album_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["dynamodb:Query", "dynamodb:GetItem"],
                resources=[
                    artist_album_table.table_arn,
                    f"{artist_album_table.table_arn}/index/AlbumId-index"
                ]
            )
        )

        albums_table.grant_read_data(get_album_lambda)
        artist_album_table.grant_read_data(get_album_lambda)
        artist_song_table.grant_read_data(get_album_lambda)
        songs_table.grant_read_data(get_album_lambda)
        artists_table.grant_read_data(get_album_lambda)

        # GET /albums/{id}
        get_album_integration = apigateway.LambdaIntegration(get_album_lambda, proxy=True)
        album_id_resource.add_method(
            "GET",
            get_album_integration,
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )
