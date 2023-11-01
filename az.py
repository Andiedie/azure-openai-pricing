from typing import Optional, List
from datetime import datetime, timezone
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.monitor.models import ResultType


def _format_time(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


class OpenAIMetrics:
    def __init__(
            self,
            tenant_id: str,
            client_id: str,
            client_secret: str,
            subscription_id: str,
            resource_group: str,
            resource_name: str
    ):
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
        self.client = MonitorManagementClient(credential, subscription_id)
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.resource_name = resource_name

    def get_metrics(
            self,
            metric_names: List[str],
            start_time: Optional[datetime],
            end_time: Optional[datetime],
            interval: str = 'PT1H'
    ):
        if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
            raise ValueError('start_time and end_time must be both None or not None')

        resource_uri = (f'subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}'
                        f'/providers/Microsoft.CognitiveServices/accounts/{self.resource_name}')
        if start_time is None and end_time is None:
            return self.client.metrics.list(
                resource_uri,
                interval=interval,
                metricnames=','.join(metric_names),
                filter="ModelDeploymentName eq '*'",
                result_type=ResultType.DATA
            )
        else:
            return self.client.metrics.list(
                resource_uri,
                timespan=f'{_format_time(start_time)}/{_format_time(end_time)}',
                interval=interval,
                metricnames=','.join(metric_names),
                filter="ModelDeploymentName eq '*'",
                result_type=ResultType.DATA
            )
