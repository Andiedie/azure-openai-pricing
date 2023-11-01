import json

import lark_oapi as lark
import lark_oapi.api.bitable.v1 as bitable
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

    def list(
            self,
            limit: int = 20000,
            sort: Optional[List[str]] = None,
            filter: Optional[str] = None
    ) -> List[bitable.AppTableRecord]:
        results = []
        page_token: Optional[str] = None
        page_size = min(500, limit)
        while True:
            builder = bitable.ListAppTableRecordRequest.builder()
            builder = builder.app_token(self.app_token).table_id(self.table_id).page_size(page_size)
            if page_token:
                builder = builder.page_token(page_token)
            if sort:
                builder = builder.sort(json.dumps(sort))
            if filter:
                builder = builder.filter(filter)
            resp = self.client.bitable.v1.app_table_record.list(builder.build())
            assert resp.code == 0, resp.msg
            if resp.data.items:
                results += resp.data.items
            if not resp.data.has_more:
                break
            if len(results) >= limit:
                break
            page_token = resp.data.page_token
        return results[:limit]

    def insert(self, records: List[Dict[str, Any]]):
        builder = bitable.BatchCreateAppTableRecordRequest.builder()
        builder = builder.app_token(self.app_token).table_id(self.table_id)
        builder = builder.request_body(
            bitable.BatchCreateAppTableRecordRequestBody.builder().records(
                [
                    bitable.AppTableRecord.builder().fields(record).build()
                    for record in records
                ]
            ).build()
        )
        resp = self.client.bitable.v1.app_table_record.batch_create(builder.build())
        assert resp.code == 0, resp.msg

    def delete(self, record_ids: List[str]):
        builder = bitable.BatchDeleteAppTableRecordRequest.builder()
        builder = builder.app_token(self.app_token).table_id(self.table_id)
        builder = builder.request_body(
            bitable.BatchDeleteAppTableRecordRequestBody.builder().records(record_ids).build()
        )
        resp = self.client.bitable.v1.app_table_record.batch_delete(builder.build())
        assert resp.code == 0, resp.msg

    def upsert(self, records: List[Dict[str, Any]], keys: List[str]):
        delete_keys = {
            tuple(record[key] for key in keys)
            for record in records
        }

        old_records = self.list()
        to_delete_record_ids = [
            record.record_id
            for record in old_records
            if tuple(record.fields[key] for key in keys) in delete_keys
        ]
        if len(to_delete_record_ids) > 0:
            self.delete(to_delete_record_ids)
        self.insert(records)
