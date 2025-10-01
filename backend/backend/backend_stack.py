from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_apigateway as apigateway
)

from backend.utils.cognito_setup import setup_cognito
from backend.utils.create_lambda import create_lambda_function
#from backend.utils.create_lambda_role import create_lambda_role


class BackendStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        music_bucket = s3.Bucket(
            self, "my-music-app-files",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        songs_table = dynamodb.Table(
            self, "Songs",
            partition_key=dynamodb.Attribute(
                name="Album",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        albums_table = dynamodb.Table(
            self, "Albums",
            partition_key=dynamodb.Attribute(
                name="Genre",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table = dynamodb.Table(
            self, "Artists",
            partition_key=dynamodb.Attribute(
                name="Genre",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="Id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table.add_global_secondary_index(
            index_name="deleted-index",
            partition_key=dynamodb.Attribute(
                name="deleted",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        user_pool, user_pool_client = setup_cognito(self)

        api = apigateway.RestApi(
            self, "MusicStreamingApi",
            rest_api_name="MusicStreamingApi",
            deploy_options=apigateway.StageOptions(
                stage_name="dev",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            )
        )

        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool],
        )


        #Artists api
        artists_api_resource = api.root.add_resource("artists")

        create_artist_lambda = create_lambda_function(self,"CreateArtistLambda","handler.lambda_handler","lambda/createArtist",[],{'TABLE_NAME': artists_table.table_name})
        artists_table.grant_write_data(create_artist_lambda)

        create_artist_integration = apigateway.LambdaIntegration(create_artist_lambda, proxy=True)

        artists_api_resource.add_method(
            "POST",
            create_artist_integration,
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        get_artists_lambda = create_lambda_function(self,"GetArtistsLambda","handler.lambda_handler","lambda/getArtists",[],{'TABLE_NAME': artists_table.table_name})
        artists_table.grant_read_data(get_artists_lambda)

        get_artists_integration = apigateway.LambdaIntegration(get_artists_lambda, proxy=True)

        artists_api_resource.add_method(
            "GET",
            get_artists_integration,
        )

        get_artist_lambda = create_lambda_function(self,"GetArtistLambda","handler.lambda_handler","lambda/getArtist",[],{'TABLE_NAME': artists_table.table_name})
        artists_table.grant_read_data(get_artist_lambda)

        artist_id_resource = artists_api_resource.add_resource("{id}")

        get_artist_integration = apigateway.LambdaIntegration(get_artist_lambda, proxy=True)

        artist_id_resource.add_method(
            "GET",
            get_artist_integration,
        )

        #Genres api
        genres_api_resource = api.root.add_resource("genres")

        get_all_genres_lambda = create_lambda_function(
            self,
            "GetGenresLambda",
            "handler.lambda_handler",
            "lambda/getGenres", 
            [],
            {'TABLE_NAME': artists_table.table_name}
        )

        artists_table.grant_read_data(get_all_genres_lambda)

        get_all_genres_integration = apigateway.LambdaIntegration(get_all_genres_lambda, proxy=True)
        genres_api_resource.add_method(
            "GET",
            get_all_genres_integration
        )


        #filters

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

