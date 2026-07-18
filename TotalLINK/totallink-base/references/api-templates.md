# TotalLINK API 调用模板参考

所有调用统一走 AIAction 端点，服务端根据 `scriptType` 自动区分查询/提交。
**日常使用建议通过 `scripts/totallink_api.py` 脚本调用，避免手拼 JSON 出错。**

---

## 通用约定

- 统一响应：`{ isSuccess, data, message }`，`isSuccess` 为字符串 `"true"`/`"false"`
- `Para` 为字符串数组，空位传 `""`，不传 `null`/`undefined`
- `data.Table` 格式：`{ schema: ["字段名", ...], data: [["值", ...]] }`
- 超时：连接 5s，读写 30s
- Content-Type: `application/json`

---

## AIAction — 统一调用

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIAction

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dm": {
      "dmCode": "<dmCode>",
      "dmNum": <dmNum>,
      "Para": ["参数1", "参数2", "..."]
    },
    "scriptType": <工具的 call_type>,
    "rowData": {},
    "tableData": []
  }
}
```

- `scriptType`：取工具的 `call_type` 值（整数 0-4），服务端据此自动区分查询/提交
- `rowData` / `tableData`：根据工具说明按需传入
  - 纯查询场景：`rowData` 和 `tableData` 传空 `{}`/`[]`
  - 行提交场景：传入 `rowData`
  - 批量提交场景：同时传入 `rowData` 和 `tableData`
