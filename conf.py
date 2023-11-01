import json
import os
import dotenv
from typing import TypedDict


class Resource(TypedDict):
    azure_subscription_id: str
    azure_resource_group: str
    azure_resource_name: str


class Task(TypedDict):
    feishu_app_id: str
    feishu_app_secret: str
    bitable_app_token: str
    bitable_table_id: str
    resources: list[Resource]
    start_time: int


dotenv.load_dotenv()

azure_app_tenant_id = os.environ.get('AZURE_APP_TENANT_ID')
azure_app_client_id = os.environ.get('AZURE_APP_CLIENT_ID')
azure_app_client_secret = os.environ.get('AZURE_APP_CLIENT_SECRET')
tasks: list[Task] = json.loads(os.environ.get('TASKS'))
