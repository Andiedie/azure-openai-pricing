import lark_oapi as lark
from typing import Optional, List, Dict, Any


class Feishu:
    def __init__(self, app_id: str, app_secret):
        self.client = lark.Client.builder().app_id(app_id).app_secret(app_secret).build()

    def bitable(self, app_token: str) -> 'Bitable':
        return Bitable(self.client, app_token)


class Bitable:
    def __init__(self, client: lark.Client, app_token: str):
        self.client = client
        self.app_token = app_token

    def table(self, table_id: str) -> 'Table':
        return Table(self.client, self.app_token, table_id)


class Table:
    def __init__(self, client: lark.Client, app_token: str, table_id: str):
        self.client = client
        self.app_token = app_token
        self.table_id = table_id

    def list_records(self) -> List[lark.bitable.v1.AppTableRecord]:
        results = []
        page_token: Optional[str] = None
        page_size = 500
        while True:
            builder = lark.bitable.v1.ListAppTableRecordRequest.builder()
            builder = builder.app_token(self.app_token).table_id(self.table_id).page_size(page_size)
            if page_token is not None:
                builder = builder.page_token(page_token)
            resp = self.client.bitable.v1.app_table_record.list(builder.build())
            assert resp.code == 0, resp.msg
            results += resp.data.items
            if resp.data.has_more:
                page_token = resp.data.page_token
            else:
                break
        return results

    def insert(self, records: List[Dict[str, Any]]):
        app_records = [
            lark.bitable.v1.AppTableRecord.builder().fields(record).build()
            for record in records
        ]
        body_builder = lark.bitable.v1.BatchCreateAppTableRecordRequestBody.builder()
        body_builder.records(app_records)

        builder = lark.bitable.v1.BatchCreateAppTableRecordRequest.builder()
        builder = builder.app_token(self.app_token).table_id(self.table_id)
        builder = builder.request_body(body_builder.build())
        resp = self.client.bitable.v1.app_table_record.batch_create(builder.build())
        assert resp.code == 0, resp.msg
