from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb
)
from backend.utils.create_lambda import create_lambda_function

class ListeningHistoryConstruct(Construct):
    def __init__(
        self,
        scope: Construct,
        id: str,
        api: apigateway.RestApi,
        table: dynamodb.Table,
        songs_table: dynamodb.Table,
        authorizer
    ):
        super().__init__(scope, id)

        listening_history_api_resource = api.root.add_resource("listening-history")

        # === POST ===
        record_listen_lambda = create_lambda_function(
            self,
            "RecordListenLambda",
            "handler.handler",
            "lambda/recordListen",
            [],
            { # 2. DODATA ENVIROMENT VARIJABLA
                "LISTENING_HISTORY_TABLE": table.table_name,
                "SONGS_TABLE": songs_table.table_name 
            }
        )
        table.grant_write_data(record_listen_lambda)
        songs_table.grant_read_data(record_listen_lambda)

        listening_history_api_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(record_listen_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )

        # === GET ===
        get_history_lambda = create_lambda_function(
            self,
            "GetListeningHistoryLambda",
            "handler.handler",
            "lambda/getListeningHistory", # Pretpostavka za lokaciju
            [],
            {"LISTENING_HISTORY_TABLE": table.table_name}
        )
        table.grant_read_data(get_history_lambda)

        listening_history_api_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(get_history_lambda, proxy=True),
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO
        )