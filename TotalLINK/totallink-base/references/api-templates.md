# TotalLINK API 调用模板参考

本文档详细描述 TotalLINK 后端三种 API 的 Payload 结构，供需要直接手写 JSON 时查阅。
**日常使用建议通过 `scripts/totallink_api.py` 脚本调用，避免手拼 JSON 出错。**

---

## 通用约定

- 统一响应：`{ isSuccess, data, message }`，`isSuccess` 为字符串 `"true"`/`"false"`
- `Para` 为字符串数组，空位传 `""`，不传 `null`/`undefined`
- `data.Table` 格式：`{ schema: ["字段名", ...], data: [["值", ...]] }`
- 超时：连接 5s，读写 30s
- Content-Type: `application/json`

---

## AIResult — 数据查询

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIResult

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dmCode": "<dmCode>",
    "dmNum": <dmNum>,
    "Para": ["参数1", "参数2", "..."]
  }
}
```

---

## AIRowSubmit — 行数据提交

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIRowSubmit

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dm": {
      "dmCode": "<dmCode>",
      "dmNum": <dmNum>,
      "Para": ["参数1", "..."]
    },
    "scriptType": <操作类型>,
    "rowData": { "字段": "值" }
  }
}
```

`scriptType` 从工具描述中获取（格式 `script_type: N`）。

---

## AIDataSubmit — 批量数据提交

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIDataSubmit

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dm": {
      "dmCode": "<dmCode>",
      "dmNum": <dmNum>,
      "Para": ["参数1", "..."]
    },
    "scriptType": <操作类型>,
    "rowData": { "字段": "值" },
    "tableData": [{ "字段1": "值1" }, { "字段1": "值2" }]
  }
}
```

---

## AIAction — 功能操作

```
POST ${TOTALLINK_BASE_URL}/api/DataModel/linkDMAIAction

{
  "loginID": "${TOTALLINK_AUTH_TOKEN}",
  "par": {
    "dm": {
      "dmCode": "<dmCode>",
      "dmNum": <dmNum>,
      "Para": ["参数1", "..."]
    },
    "scriptType": <操作类型>,
    "rowData": { "字段": "值" },
    "tableData": [{ "字段1": "值1" }]
  }
}
```

`scriptType` 使用工具自身的 `call_type`（整数 0-4）。参数结构与 `AIDataSubmit` 一致。
