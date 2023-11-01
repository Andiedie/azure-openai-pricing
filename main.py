import conf
from az import OpenAIMetrics
from feishu import Feishu
from datetime import datetime
import pandas as pd


for task in conf.tasks:
    feishu = Feishu(task['feishu_app_id'], task['feishu_app_secret'])
    bitable = feishu.bitable(task['bitable_app_token'])
    table = bitable.table(task['bitable_table_id'])
    for resource in task['resources']:
        m = OpenAIMetrics(
            tenant_id=conf.azure_app_tenant_id,
            client_id=conf.azure_app_client_id,
            client_secret=conf.azure_app_client_secret,
            subscription_id=resource['azure_subscription_id'],
            resource_group=resource['azure_resource_group'],
            resource_name=resource['azure_resource_name']
        )
        data = m.get_metrics(['ProcessedPromptTokens', 'GeneratedTokens'], None, None)
        records = []

        for one_metric in data.value:
            for one_model in one_metric.timeseries:
                for one_time in one_model.data:
                    records.append({
                        '资源名': resource['azure_resource_name'],
                        '时间': one_time.time_stamp.timestamp(),
                        '模型': one_model.metadatavalues[0].value,
                        'Prompt Tokens': one_time.total if one_metric.name.value == 'ProcessedPromptTokens' else 0,
                        'Completion Tokens': one_time.total if one_metric.name.value == 'GeneratedTokens' else 0
                    })
        final_records = pd.DataFrame(records).groupby(['资源名', '时间', '模型']).sum().reset_index().to_dict('records')
        table.insert(final_records)
