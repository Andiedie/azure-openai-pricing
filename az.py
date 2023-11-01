from typing import TypedDict, Optional
from datetime import datetime, timezone, timedelta

import requests


class Name(TypedDict):
    value: str
    localizedValue: str


class MetadataValue(TypedDict):
    name: Name
    value: str


class Metric(TypedDict):
    timeStamp: str
    total: int


class Timeseries(TypedDict):
    metadatavalues: list[MetadataValue]
    data: list[Metric]


def _format_time(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


class AZ:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = requests.Session()
        self.session.headers['Authorization'] = 'Bearer ' + self.get_access_token()

    def get_access_token(self) -> str:
        url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'resource': 'https://management.azure.com/'
        }
        resp = requests.post(url, data=data)
        return resp.json().get('access_token')

    def get_metrics(
            self,
            subscription_id: str,
            resource_group: str,
            resource_name: str,
            metric_name: str,
            start_time: Optional[datetime],
            end_time: Optional[datetime]
    ) -> list[Timeseries]:
        if (start_time is None and end_time is not None) or (end_time is None and start_time is not None):
            raise ValueError('start_time and end_time must be both None or not None')
        url = (f'https://management.azure.com/'
               f'subscriptions/{subscription_id}/'
               f'resourceGroups/{resource_group}/'
               f'providers/Microsoft.CognitiveServices/accounts/{resource_name}/'
               f'providers/Microsoft.Insights/metrics')
        params = {
            'api-version': '2019-07-01',
            'metricnames': metric_name,
            '$filter': "FeatureName eq '*'",
        }
        if start_time is not None:
            params['timespan'] = f'{_format_time(start_time)}/{_format_time(end_time)}'

        resp = self.session.get(url, params=params)
        return resp.json()['value'][0]['timeseries']
