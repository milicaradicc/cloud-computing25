from constructs import Construct
from aws_cdk import aws_apigateway as apigateway, aws_lambda as _lambda, aws_dynamodb as dynamodb
from backend.utils.create_lambda import create_lambda_function

class ArtistsConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        table: dynamodb.Table,
        songs_table: dynamodb.Table,
        albums_table: dynamodb.Table,
        artist_album_table: dynamodb.Table,
        artist_song_table: dynamodb.Table,
        authorizer
    ):
        super().__init__(scope, id)

        artists_api_resource = api.root.add_resource("artists")

        # Create Artist
        create_artist_lambda = create_lambda_function(
            self,
            "CreateArtistLambda",
            "handler.lambda_handler",
            "lambda/createArtist",
            [],
            {"TABLE_NAME": table.table_name}
        )
        table.grant_write_data(create_artist_lambda)

        artists_api_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(create_artist_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Artists
        get_artists_lambda = create_lambda_function(
            self,
            "GetArtistsLambda",
            "handler.lambda_handler",
            "lambda/getArtists",
            [],
            {"TABLE_NAME": table.table_name}
        )
        table.grant_read_data(get_artists_lambda)

        artists_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_artists_lambda, proxy=True),
        )

        # Delete artist
        delete_artist_lambda = create_lambda_function(
            self,
            "DeleteArtistLambda",
            "handler.lambda_handler",
            "lambda/deleteArtist",
            [],
            {
             "ARTISTS_TABLE":table.table_name,
             "SONGS_TABLE": songs_table.table_name,
             "ALBUMS_TABLE": albums_table.table_name,
             "ARTIST_ALBUM_TABLE": artist_album_table.table_name,
             "ARTIST_SONG_TABLE": artist_song_table.table_name}
        )
        table.grant_read_write_data(delete_artist_lambda)
        songs_table.grant_read_write_data(delete_artist_lambda)
        albums_table.grant_read_write_data(delete_artist_lambda)
        artist_song_table.grant_read_write_data(delete_artist_lambda)
        artist_album_table.grant_read_write_data(delete_artist_lambda)

        artist_id_resource = artists_api_resource.add_resource("{id}")
        artist_id_resource.add_method(
            "DELETE",
            apigateway.LambdaIntegration(delete_artist_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # Get Artist by Id + Albums/Songs
        get_artist_lambda = create_lambda_function(
            self,
            "GetArtistByIdLambda",
            "handler.lambda_handler",
            "lambda/getArtistById",
            [],
            environment={
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTIST_ALBUM_TABLE": artist_album_table.table_name,
                "ARTISTS_TABLE": table.table_name,
                "SONGS_TABLE": songs_table.table_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name
            }
        )

        albums_table.grant_read_data(get_artist_lambda)
        artist_album_table.grant_read_data(get_artist_lambda)
        artist_song_table.grant_read_data(get_artist_lambda)
        songs_table.grant_read_data(get_artist_lambda)
        table.grant_read_data(get_artist_lambda)

        get_artist_integration = apigateway.LambdaIntegration(get_artist_lambda, proxy=True)

        artist_id_resource.add_method(
            "GET",
            get_artist_integration,
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

