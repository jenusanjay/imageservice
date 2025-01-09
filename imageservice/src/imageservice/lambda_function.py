import os
from mangum import Mangum
from imageservice.api import app

lambda_handler = Mangum(
    app,
    lifespan="off",
    api_gateway_base_path=os.environ.get("API_GATEWAY_BASE_PATH")
) 

