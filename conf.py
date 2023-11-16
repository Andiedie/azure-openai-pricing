import base64
import binascii
import json
import os
import dotenv
from pydantic import BaseModel, Field


class Scale(BaseModel):
    start_time: str
    end_time: str = Field(default='9999-12-31T23:59:59.999+08:00')
    scale: float


class Resource(BaseModel):
    azure_subscription_id: str
    azure_resource_group: str
    azure_resource_name: str
    start_time: str
    scale: list[Scale] = Field(default=[Scale(start_time='1970-01-01T00:00:00.000+00:00', scale=1)])


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
try:
    _raw_task_data = base64.b64decode(os.environ.get('TASKS', ''), validate=True).decode()
except binascii.Error:
    _raw_task_data = os.environ.get('TASKS', '')
tasks: list[Task] = [Task.model_validate(one) for one in json.loads(_raw_task_data)]
