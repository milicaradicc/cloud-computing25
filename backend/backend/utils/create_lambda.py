import aws_cdk.aws_lambda as _lambda
from aws_cdk import BundlingOptions, Duration
import aws_cdk.aws_iam as iam

def create_lambda_function(stack, id, handler, include_dir, layers, environment):
    role = iam.Role(
            stack, id+"Role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
    role.add_managed_policy(
        iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
    )

    function = _lambda.Function(
        stack, id,
        runtime=_lambda.Runtime.PYTHON_3_9,
        layers=layers,
        handler=handler,
        code=_lambda.Code.from_asset(include_dir,
            bundling=BundlingOptions(
                image=_lambda.Runtime.PYTHON_3_9.bundling_image,
                command=[
                    "bash", "-c",
                    "pip install --no-cache -r requirements.txt -t /asset-output && cp -r . /asset-output"
                ],
            ),),
        memory_size=128,
        timeout=Duration.seconds(10),
        environment=environment,
        role=role
    )
    fn_url = function.add_function_url(
        auth_type=_lambda.FunctionUrlAuthType.NONE,
        cors=_lambda.FunctionUrlCorsOptions(
            allowed_origins=["*"]
        )
    )
    
    return function