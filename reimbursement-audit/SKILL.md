---
name: TotalLINK-reimbursement-audit
slug: totallink-reimbursement
description:
  TotalLINK 报销单全流程审计 Skill。自动完成：查询报销单 → 下载附件识别发票 → 生成审计报告（Markdown）→ 生成 PDF → 发送邮件。
metadata:
  dependencies:
    - totallink-base
    - totallink-email-sender
    - totallink-pdf-generator
  workbuddy:
    env:
      TOTALLINK_AUTH_TOKEN: ""
      TOTALLINK_BASE_URL: "http://124.71.144.80:8088"
      SMTP_HOST: "smtp.163.com"
      SMTP_PORT: "465"
      SMTP_FROM: ""
      SMTP_TO: ""
    note: "Token + SMTP 授权码需首次配置后持久化。SMTP 凭据存 ~/.totallink/smtp.json（chmod 600），严禁写入 MEMORY.md"
---

> **安全约定（上游自带，更新时勿回退）**
> 1. 发件人 / 收件人一律不硬编码，发送前必须向用户确认收件人地址
> 2. SMTP 授权码存 `~/.totallink/smtp.json`（权限 600），**禁止**写入 `~/.workbuddy/MEMORY.md` 等会被注入模型上下文的文件
> 3. Python 解释器路径通过 `TOTALLINK_PYTHON` 环境变量覆盖，仓库不内置机器相关的绝对路径

# TotalLINK 报销单审计

## 概述

从 TotalLINK 后端直接查询报销单数据，逐单下载附件并识别发票内容，生成合规审计报告（Markdown + PDF），自动发送邮件。所有 API 调用直连 TotalLINK 后端。

**默认执行节奏（分段确认制）**：Step 1~5 生成 Markdown 报告后**必须停下**，等用户检查确认后才可进入 Step 6（PDF + 邮件）。邮件是不可逆动作，禁止跳过 md 确认点直接发送。

## 前置条件

- **TotalLINK 项目选择**：参照 [基础 Skill](../SKILL.md) 完成项目选择和认证配置
- **API 调用**：通过 `../scripts/totallink_api.py` 调用
- 邮件 SMTP 配置：参照 [邮件发送 Skill](../shared/email-sender/SKILL.md)。首次使用向用户索取发件人邮箱与 SMTP 授权码，保存到 `~/.totallink/smtp.json`（权限 600）；**收件人每次执行时向用户确认**
- PDF 生成工具链：由 [PDF 生成 Skill](../shared/pdf-generator/SKILL.md) 承担，渲染统一走 Chrome headless（本机 WeasyPrint 缺 gobject 不可用，已废弃）
- Python 环境：需准备装有 `pdfplumber`、`requests` 的 Python，路径导出为 `TOTALLINK_PYTHON`

> 为简化下文命令，先执行：
> ```bash
> export TOTALLINK_PYTHON="${TOTALLINK_PYTHON:-<装有 pdfplumber 的 python3 绝对路径>}"
> ```

---

## 本次场景所需工具

以下工具的 dmCode/dmNum 已固定，调用时直接使用：

| 工具 | dmCode | dmNum | script_type | 用途 |
|------|--------|-------|-------------|------|
| 报销单列表 | LINKAI20 | 10 | 0 | 按日期范围查询 |
| 报销单表头信息 | LINKAI2010X | 10 | 0 | 获取单张表头 |
| 报销单内容 | LINKAI2010X | 20 | 0 | 获取费用明细 |
| 报销单附件列表 | LINKAI2010X | 30 | 0 | 获取附件 URL |

> **工具编号以服务端为准**：平台工具编号会随服务端调整而变化，本节编号已按最新一次核对结果更新。若调用出现「工具不存在」或返回空数据，先用 SEARCHLIST 以关键字（如「报销」）复核，再按返回的 `code` / `num` 调用，不要沿用历史编号。
>
> 返回数据为**中文列名**（`schema` 即中文标签），核对时按中文列名取值，不要按英文列名（如 DOCNUM/AMTTOT）取数。

---

## Workflow

### 产物归档结构（固定，全程使用）

```text
outputs/exp_audit_<yyyymm>/
├── attachments/          # 下载的原始附件（按 单号__原文件名 命名）
├── evidence/             # 审计底稿（可追溯、供跨月查重复用）
│   ├── docs_index.json       # 单据索引：表头/明细/附件摘要
│   ├── invoices_index.json   # 发票索引：单号、发票号、开票日期、价税合计、来源(pdf/jpg)
│   └── invoice_texts/        # PDF 发票文本提取结果（JPG 无文本，写 _README 说明）
├── 审计报告.md
├── 审计报告.pdf
└── （可选）duplicate-report.json / render-notes.html
```

中间数据（API 原始返回、发票提取文本）**必须落盘到 evidence/**，不要留在 /tmp——跨月查重依赖历史 invoices_index.json。

### Step 1：查询报销单列表

```bash
python3 ../scripts/totallink_api.py \
  --dm-code LINKAI20 --dm-num 10 \
  --params "" "2026-06-01" "2026-07-11" "" --script-type 0
```

`--params` 按位置传入：`"搜索内容(可空)"` `"开始日期"` `"结束日期"` `"状态(可空)"`。
默认时间范围：上月至今（用户可指定起止日期）。

**返回数据（字段为中文列名）：**

```json
{
  "isSuccess": "true",
  "data": {
    "Table": {
      "schema": ["单据编号", "报销类型", "报销日期", "部门", "报销人", "币种", "汇率", "总金额", "借款金额", "应退补款", "备注", "单据状态", "工作流状态", "创建人", "修改人", "创建时间", "修改时间"],
      "data": [
        ["EXP260600009", "招待费（BusinessEntertainment）", "2026-06-23", "TotalLINK", "RANDY.LIU", "CNY", 1.0, 300.0, 0.0, 300.0, "第二次提交仍然不符合要求", "Planned-计划的", "REJECTED", "RANDY.LIU", "RANDY.LIU", "2026-06-23T17:35:01.347", "2026-06-23T17:36:43.72"],
        ["EXP260600010", "招待费（BusinessEntertainment）", "2026-06-26", "", "Oscar", "CNY", 1.0, 606.0, 0.0, 606.0, "再次驳回", "Planned-计划的", "REJECTED", "Oscar", "Oscar", "2026-06-26T10:55:41.607", "2026-06-26T10:55:49.777"]
      ]
    }
  }
}
```

列表字段要点：

- `单据状态` 为流程步骤（如「Planned-计划的」），**是否驳回看「工作流状态」是否为 `REJECTED`**。
- `备注` 列在驳回后承载**驳回原因**，审核时须与问题清单对照。

---

### Step 2：获取每单详细信息

对每张报销单并行调用（提升效率）：

```bash
# 表头信息
python3 ../scripts/totallink_api.py \
  --dm-code LINKAI2010X --dm-num 10 --params "EXP260600009" --script-type 0

# 费用明细
python3 ../scripts/totallink_api.py \
  --dm-code LINKAI2010X --dm-num 20 --params "EXP260600009" --script-type 0

# 附件列表
python3 ../scripts/totallink_api.py \
  --dm-code LINKAI2010X --dm-num 30 --params "EXP260600009" --script-type 0
```

三个接口均**按单据编号精确过滤**。取数时注意：

- 表头（/10）的「报销类型」返回的是**类型编码**（如 `ZDF` 招待费、`QTFY` 其他费用、`CLSYF` 车辆使用费、`SNJTF` 市内交通费），中文名称在「单据描述」列。
- 表头（/10）**不返回工作流状态**，是否驳回需从列表查询（`LINKAI20/10`）的「工作流状态」列判断。
- 明细（/20）的「费用类型」同样是编码，中文名称在「类型描述」列。
- 表头（/10）与明细（/20）在**传空参数**时会各返回一条「单据编号为空」的模板行（新增单据用的脚手架，非真实单据），取数时须过滤。

---

### Step 3：下载并识别发票

下载附件（PDF 或 JPG），提取发票关键信息：

**下载附件：**

```python
import requests, time
from urllib.parse import quote

parts = url.split('/', 3)
encoded_url = parts[0] + '//' + parts[2] + '/' + quote(parts[3])

# 附件 URL 会偶发瞬时 404（含其所在目录也返回 404），必须重试后再判定
ok = False
for attempt in range(3):
    r = requests.get(encoded_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    if r.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(r.content)
        ok = True
        break
    time.sleep(1)
if not ok:
    raise RuntimeError(f"附件下载失败（已重试 3 次）: {r.status_code} {url}")
```

> **重要：不可因一次 404 就判定附件缺失。** 实测同一 URL 首次请求（连同其日期目录）返回 404，数十秒后重试即返回 200 并正常下载。判定"附件缺失"前至少重试 2 轮。
> 辅助判断：`/Files/` 与已存在的日期目录返回 403（目录存在但禁止列目录），不存在的目录返回 404。

**PDF 发票 → 读取文本（pdfplumber）：**

```bash
"$TOTALLINK_PYTHON" -c "
import pdfplumber
with pdfplumber.open('path.pdf') as pdf:
    for page in pdf.pages:
        print(page.extract_text())
"
```

**JPG 图片发票 → 使用 Read 工具（多模态）直接读取。**

提取关键字段：发票号码、开票日期、购买方名称、项目名称、金额、税额、价税合计、出行人信息。

> 网约车/运输类发票常出现「出行人、出行日期、出发地、到达地」等栏位为空白（行程明细在行程单内），且可能含**负数冲销行**（退款调整）。前者须在报告中列为「缺少行程凭证」，后者须提示确认退款部分未重复报销。

---

### Step 4：核对分析

逐单对比报销单与发票信息：

| 核对项 | 检查点 |
|-------|--------|
| 金额一致性 | 发票价税合计合计值 vs 报销单总金额（注意多张发票需先求和） |
| 发票时效 | 发票开票日期与费用日期是否吻合，是否在有效期内（一般 3~6 个月） |
| 费用归类 | 发票项目名称（如「运输服务-客运服务费」）与报销单费用类型是否匹配 |
| 购买方抬头 | 发票上的购买方是否属于可报销公司 |
| 附件合规 | 是否有附件、附件是否真实发票、是否含冲销负数行 |
| 行程佐证 | 网约车/机票类是否附行程单，出行人与报销人是否一致 |
| 明细勾稽 | 明细各行金额合计是否等于表头总金额；明细拆分与各张发票能否对应 |

**占位值与异常字段规则（2026-06 实测新增）：**

- 明细「开始/结束日期」出现 `1900-01-01` → 视为**费用日期未填**，直接列入问题清单，报告中不显示原始占位值。
- 附件中混入**非发票文件**（付款申请单 xlsx、行程单图片以外的文档等）→ 标注「非合规报销票据」列入问题清单，不尝试解析其内容，也不计入票据合计。
- 明细填报费用期间与票据实际日期（乘车日/开票日）不吻合 → 列为「费用期间填报有误」，中风险。

### Step 4.5：跨单发票查重（强制）

全部单据发票识别完成后，必须做跨单比对——历史上同一张发票被拆到多张单据重复提交过（2026-06 实测：007/008 与 011 交叉重复 ¥84.21）。

1. 识别过程中将每张发票登记到 `evidence/invoices_index.json`。**顶层为 `{"period": "2026-06", "note": "…", "invoices": […]}` 包装**，发票条目字段：`doc` / `invoice_no` / `issue_date` / `total` / `source`；非发票附件不登记。
2. 运行查重脚本：

```bash
"$TOTALLINK_PYTHON" scripts/dedup_check.py \
  outputs/exp_audit_<当月>/evidence/invoices_index.json \
  [outputs/exp_audit_<历史月>/evidence/invoices_index.json ...]
```

- 传多个月份的索引即实现**跨月查重**（渐进式：有历史底稿就带上，不为查重专门回溯取数）。
- 退出码 2 = 发现重复，输出 JSON 中每组含涉及单据、金额、是否金额冲突、是否跨期。
3. 查重结果写入报告「共性问题汇总」的**重复发票专项**小节，并计入风险评级。建议去重归属时给出明确指向（如「该票保留在 EXP260600011 中提交，007/008 重新提交时须剔除」）。

### Step 4.6：风险评级（按固化标准）

按以下对照表定级，保证每次报告口径一致：

| 风险等级 | 判定标准（命中其一即定级） |
|---------|--------------------------|
| 高 | 购买方抬头不属于可报销公司；票据合计与报销金额不符；跨单/跨期重复发票；发票开票早于费用 6 个月以上或已超一般报销时效 |
| 中 | 费用归类与票据内容不匹配；开票/乘车日期与填报费用期间逻辑不符；含负数冲销行待确认退款；附件含非发票文件；费用日期未填 |
| 低 | 仅缺行程佐证（出行人/行程栏位空白）；部门等字段未填；票据合规但驳回原因不明 |

多问题取最高级。评级表写入报告「风险评级」章节（等级 / 单据 / 核心问题 / 建议处理）。

---

### Step 5：生成审计报告（Markdown）

按以下结构生成 Markdown 审计报告：

```markdown
# 本周报销单审计分析报告

## 一、总体概览
（汇总表：单号、金额、类型、状态）

## 二、各单明细审计
### 1. 单号 — 费用类型 ¥金额
（详细信息表 + 问题列表）

## 三、共性问题汇总
（发票日期问题/金额问题/归类问题/抬头问题）

### 重复发票专项（查重发现重复时必写）
（重复发票号码 / 涉及单据 / 合计金额 / 去重归属建议）

### 提交人画像
（按报销人汇总问题类型分布；对外场合可隐去姓名只按问题类型统计）

## 四、风险评级
（风险表 + 建议处理）

## 五、审计结论
```

**单张单据审核的报告结构**（用户只指定一张单号时使用）：

```markdown
# 报销单审计分析报告

## 一、单据概览
（单据编号 / 报销类型 / 日期 / 部门 / 报销人 / 金额 / 状态 / 驳回备注）

## 二、费用明细审核
（明细表 + 与表头金额的勾稽结论）

## 三、附件与发票核对
（逐张发票：号码 / 开票日期 / 销售方 / 购买方 / 项目 / 价税合计 + 票据合计）

## 四、问题清单
（序号 / 问题 / 说明 / 风险等级）

## 五、风险评级
（风险等级 / 问题序号 / 处理建议）

## 六、整改建议
（可执行的逐项整改动作）

## 七、审计结论
```

**重要规则：**
- 日期用 `YYYY-MM-DD` 格式
- 金额用 `¥` 前缀
- 不要使用 emoji
- 使用 `---` 分隔章节
- 报告中需明确写出「票据合计 vs 报销金额」的差额（无差额写「一致」），以及发票开票日期与费用日期的间隔
- 报告末尾必须加上声明：`本报告由 TotalLINK AI 助手自动生成，仅供参考，最终审批以人工审核为准。`

**Pandoc 安全规则（参照 PDF 生成 Skill）：**
- 禁止 `[X]` `[!]` `[OK]` → 使用 `X` `!` `OK`
- 禁止 `\*文本\*` → 使用 `*文本*`
- 每个表格前后必须有空行

---

### Step 6：生成 PDF + 发送邮件

参照 [PDF 生成 Skill](../shared/pdf-generator/SKILL.md) 和 [邮件发送 Skill](../shared/email-sender/SKILL.md)。

**生成 PDF（Chrome headless）：**

> 排版与渲染统一由 [PDF 生成 Skill](../shared/pdf-generator/SKILL.md) 承担。WeasyPrint 路径已废弃（本机缺 `libgobject-2.0-0`，`import weasyprint` 直接报错），不要尝试。Chrome 不支持 @page 页码计数器，PDF 无页码（已接受此限制；需要页码时在 Chrome 打印对话框勾选「页眉和页脚」）。

```bash
cd /path/to/outputs/exp_audit_<yyyymm>
# <SKILL_DIR> = TotalLINK skill 安装目录，如 ~/.workbuddy/skills/TotalLINK

# 1. 按 PDF 生成 Skill 的排版规范生成自包含 HTML（见其工作流第 4 步，
#    排版依据 references/print-css.md 与 references/visual-design.md）

# 2. 渲染 PDF（脚本自动探测 Chrome，不硬编码浏览器路径）
"<SKILL_DIR>/shared/pdf-generator/scripts/render_pdf.sh" 审计报告.html 审计报告.pdf

# 3. 校验页数与关键内容（NFKC 归一化已内置于脚本）
"$TOTALLINK_PYTHON" "<SKILL_DIR>/shared/pdf-generator/scripts/verify_pdf.py" \
  审计报告.pdf --expect "执行摘要" "结论" --max-pages 30
```

校验提示：用 pdfplumber 检查页数与关键内容时，Chrome 嵌入字体的 ToUnicode 会把「一/风/车」等映射为康熙部首码位（U+2E80~2FDF），提取文本需先做 NFKC 归一化再比对，否则会误判缺内容；视觉渲染不受影响。

**发送邮件（仅 PDF 附件）：**

> ⚠️ **发送前必须向用户确认收件人地址**，不得使用任何硬编码地址。邮件是不可逆的外部动作，未取得明确同意前禁止调用 `send_message`。

配置读取优先级：`~/.totallink/smtp.json`（权限 600）→ 缺失则向用户索取发件人邮箱与 SMTP 授权码。

`~/.totallink/smtp.json` 格式：

```json
{
  "host": "smtp.163.com",
  "port": 465,
  "from_addr": "your邮箱@example.com",
  "password": "SMTP授权码"
}
```

```python
import json, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

SMTP_CFG = os.path.expanduser("~/.totallink/smtp.json")
if not os.path.exists(SMTP_CFG):
    raise SystemExit("未配置 SMTP，请向用户索取发件人邮箱与授权码后写入 ~/.totallink/smtp.json（chmod 600）")
cfg = json.load(open(SMTP_CFG, encoding="utf-8"))

from_addr = cfg["from_addr"]
to_addr = "<用户本次确认的收件人地址>"   # 必须经用户确认，禁止硬编码

msg = MIMEMultipart()
msg["From"] = from_addr
msg["To"] = to_addr
msg["Subject"] = "本周报销单审计分析报告"
msg.attach(MIMEText("报销单审计报告见附件，请查收。", "plain", "utf-8"))

with open("审计报告.pdf", "rb") as f:
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=("utf-8", "", "审计报告.pdf"))
    msg.attach(attachment)

with smtplib.SMTP_SSL(cfg.get("host", "smtp.163.com"), cfg.get("port", 465), timeout=30) as server:
    server.login(from_addr, cfg["password"])
    server.send_message(msg)

print(f"邮件已发送至 {to_addr}")
```

---

## 关键注意事项

1. **认证**：脚本自动从 `~/.totallink/config.json` 读取令牌，无需手动传
2. **dmCode/dmNum**：已按最新核对结果硬编码（见「本次场景所需工具」），无需工具发现步骤；编号若失效先用 SEARCHLIST 复核
3. **列名**：返回数据为中文列名，按 `schema`/`captions` 的中文标签取值，不要按英文列名取数
4. **直参**：`--params` 空位传 `""`（空字符串），不是 `null`/`undefined`
5. **并行调用**：Step 2 中多张报销单的详情可并行请求
6. **附件 URL**：含中文时需对路径部分做 URL-encode；下载须带 `User-Agent` 头
7. **附件瞬时 404**：**必须重试至少 2 轮再判定缺失**，一次 404 不代表文件不存在
8. **模板行过滤**：表头（/10）与明细（/20）传空参数会返回「单据编号为空」的模板行，须过滤
9. **JPG vs PDF**：JPG 用多模态直接读取，PDF 用 pdfplumber
10. **所有 Python 命令**：通过 venv 执行（`$TOTALLINK_PYTHON`）
11. **SMTP 凭据**：首次向用户索取发件人邮箱与授权码，保存到 `~/.totallink/smtp.json`（chmod 600）；**禁止**写入 `MEMORY.md`
12. **收件人**：每次执行前向用户确认，**禁止**硬编码、禁止免确认自动发送
13. **分段确认**：md 报告生成后必须停下等用户确认，才可生成 PDF / 发邮件
14. **跨单查重**：Step 4.5 强制执行，结果写入报告重复发票专项
15. **底稿归档**：API 中间数据与发票提取文本一律落盘 `evidence/`，禁止只留 /tmp
16. **占位值**：明细日期 1900-01-01 = 未填；非发票附件不计入票据合计、不解析内容

## Resources

### scripts/
- [dedup_check.py](scripts/dedup_check.py) — 跨单/跨月发票查重（输入 invoices_index.json，输出重复分组 JSON，退出码 2=有重复）

### references/
- [TotalLINK 基础 Skill](../SKILL.md) — 认证管理、API 格式
- [邮件发送 Skill](../shared/email-sender/SKILL.md) — SMTP 发送规范
- [PDF 生成 Skill](../shared/pdf-generator/SKILL.md) — Markdown → HTML → PDF 自动流程（Chrome headless）
