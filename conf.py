import json
import os
import dotenv
from pydantic import BaseModel, Field


class Resource(BaseModel):
    azure_subscription_id: str
    azure_resource_group: str
    azure_resource_name: str
    start_time: str
    scale: float = Field(default=1)


class Task(BaseModel):
    name: str
    bitable_app_token: str
    bitable_table_id: str
    resources: list[Resource]


dotenv.load_dotenv()

azure_app_tenant_id = os.environ.get('AZURE_APP_TENANT_ID')
azure_app_client_id = os.environ.get('AZURE_APP_CLIENT_ID')
azure_app_client_secret = os.environ.get('AZURE_APP_CLIENT_SECRET')
feishu_app_id = os.environ.get('FEISHU_APP_ID')
feishu_app_secret = os.environ.get('FEISHU_APP_SECRET')
tasks: list[Task] = [Task.model_validate(one) for one in json.loads(os.environ.get('TASKS'))]
