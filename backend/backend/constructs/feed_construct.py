from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb
)
from backend.utils.create_lambda import create_lambda_function

class FeedConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        score_table: dynamodb.Table,
        songs_table: dynamodb.Table,
        albums_table: dynamodb.Table,
        artist_song_table: dynamodb.Table,
        artist_album_table: dynamodb.Table,
        authorizer
    ):
        super().__init__(scope, id)

        feed_api_resource = api.root.add_resource("feed")

        # === GET ===
        # Jedna, kompletna definicija Lambda funkcije
        get_feed_lambda = create_lambda_function(
            self,
            "GetFeedLambda",
            "handler.handler",
            "lambda/getFeed",
            [],
            {
                # IZMENJENO: Sve potrebne environment varijable
                "SCORE_TABLE": score_table.table_name,
                "SONGS_TABLE": songs_table.table_name,
                "ALBUMS_TABLE": albums_table.table_name,
                "ARTIST_SONG_TABLE": artist_song_table.table_name,
                "ARTIST_ALBUM_TABLE": artist_album_table.table_name
            }
        )
        
        # IZMENJENO: Sve potrebne dozvole
        score_table.grant_read_data(get_feed_lambda)
        songs_table.grant_read_data(get_feed_lambda)
        albums_table.grant_read_data(get_feed_lambda)
        artist_song_table.grant_read_data(get_feed_lambda)
        artist_album_table.grant_read_data(get_feed_lambda)

        # Povezivanje Lambde na API endpoint (ovo je ostalo isto)
        feed_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_feed_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )