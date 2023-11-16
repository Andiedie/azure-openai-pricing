import conf
from az import OpenAIMetrics
from feishu import Feishu
import pandas as pd
from datetime import datetime, timedelta
import pytz

tz8 = pytz.timezone('Asia/Shanghai')

for task in conf.tasks:
    print(f'processing {task.name}')
    feishu = Feishu(conf.feishu_app_id, conf.feishu_app_secret)
    bitable = feishu.bitable(task.bitable_app_token)
    table = bitable.table(task.bitable_table_id)
    for resource in task.resources:
        last_records = table.list(limit=1, sort=['时间 DESC'],
                                  filter=f"CurrentValue.[资源名]=\"{resource.azure_resource_name}\"")
        if len(last_records) > 0:
            start_time = datetime.fromtimestamp(last_records[0].fields['时间'] / 1000).astimezone(tz8)
            start_time -= timedelta(hours=5)
            print(f"got start time {start_time} from records")
        else:
            start_time = datetime.fromisoformat(resource.start_time).astimezone(tz8)
            print(f"got start time {start_time} from task")
        end_time = datetime.now().astimezone(tz8)
        if end_time <= start_time:
            print(f"skip {resource.azure_resource_name} because of too short time range")
            continue

        m = OpenAIMetrics(
            tenant_id=conf.azure_app_tenant_id,
            client_id=conf.azure_app_client_id,
            client_secret=conf.azure_app_client_secret,
            subscription_id=resource.azure_subscription_id,
            resource_group=resource.azure_resource_group,
            resource_name=resource.azure_resource_name
        )

        print(f"getting metrics for {resource.azure_resource_name} from {start_time} to {end_time}")
        data = m.get(
            ['ProcessedPromptTokens', 'GeneratedTokens', 'AzureOpenAIRequests'],
            start_time, end_time)
        records = []
        for one_metric in data.value:
            for one_model in one_metric.timeseries:
                for one_time in one_model.data:
                    records.append({
                        '资源名': resource.azure_resource_name,
                        '时间': one_time.time_stamp.timestamp() * 1000,
                        '模型': one_model.metadatavalues[0].value,
                        'Requests': one_time.total if one_metric.name.value == 'AzureOpenAIRequests' else 0,
                        'Prompt Tokens': one_time.total if one_metric.name.value == 'ProcessedPromptTokens' else 0,
                        'Completion Tokens': one_time.total if one_metric.name.value == 'GeneratedTokens' else 0
                    })

        df = pd.DataFrame(records).groupby(['资源名', '时间', '模型']).sum().reset_index()
        df = df[(df['Prompt Tokens'] > 0) | (df['Completion Tokens'] > 0)]
        for scale in resource.scale:
            start_time = datetime.fromisoformat(scale.start_time).astimezone(tz8).timestamp() * 1000
            end_time = datetime.fromisoformat(scale.end_time).astimezone(tz8).timestamp() * 1000
            mask = (df['时间'] >= start_time) & (df['时间'] < end_time)
            df.loc[mask, 'Prompt Tokens'] *= scale.scale
            df.loc[mask, 'Completion Tokens'] *= scale.scale

        df['Prompt Tokens'] = df['Prompt Tokens'].astype(int)
        df['Completion Tokens'] = df['Completion Tokens'].astype(int)
        final_records = df.to_dict('records')
        if len(final_records) > 0:
            print(f"upserting {len(final_records)} records")
            table.upsert(final_records, ['资源名', '时间', '模型'])
