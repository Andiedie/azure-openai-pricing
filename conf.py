import json
import os
import dotenv
from typing import TypedDict


class Resource(TypedDict):
    azure_subscription_id: str
    azure_resource_group: str
    azure_resource_name: str
    start_time: str


class Task(TypedDict):
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
tasks: list[Task] = json.loads(os.environ.get('TASKS'))
