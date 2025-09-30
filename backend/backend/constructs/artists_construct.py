from constructs import Construct
from aws_cdk import aws_apigateway as apigateway, aws_lambda as _lambda, aws_dynamodb as dynamodb
from backend.utils.create_lambda import create_lambda_function

class ArtistsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, api: apigateway.RestApi, table: dynamodb.Table, authorizer):
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
