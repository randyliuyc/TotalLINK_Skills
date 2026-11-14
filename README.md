# TotalLINK Skills

对接 [TotalLINK](http://total-link.cn) 数据分析及功能开发平台的 AI Skill 集合。

**一个文件，多平台通用**：根 `SKILL.md` 同时适配 WorkBuddy（AskUserQuestion 弹窗）和其他 AI Agent（文字交互）。脚本层纯 Python，跨平台可运行。

## 安装

```bash
git clone https://gitee.com/randyliuyc/TotalLINK_Skill.git <目标目录>
```

| 平台 | 安装路径 | 加载文件 |
|------|---------|---------|
| WorkBuddy | `~/.workbuddy/skills/TotalLINK/` | 根 `SKILL.md` |
| 其他 Agent | 任意目录 | 根 `SKILL.md` |

> **整仓安装**：仓库根目录即 base skill（`totallink-base`），场景 skill 放在同级子目录。目录名 `TotalLINK` 是安装目录名，不要求与 skill `name` 一致；各子目录名与各自的 `name` 一致。
> 跨 skill 的引用按 skill 名描述（如「见 `model-designer` skill 的 `references/endpoints.md`」），可执行脚本路径按仓库布局给出（如 `<SKILL_DIR>/pdf-generator/scripts/render_pdf.sh`）。

## 技能列表

| Skill | 目录 | 用途 | 适用范围 |
|-------|------|------|---------|
| totallink-base | 根目录 | 认证、工具发现、API 调用、数据预处理 | 通用 |
| ai-init | `ai-init/` | AI 环境初始化：新环境导入 LINKAIINIT 模型组并执行 SYSINFOMATION230X/501（建 LINKAIAVT/LINKAIBAL 表 + 汇总行基线） | 通用 |
| model-designer | `model-designer/` | 数据模型设计：需求问卷与任务书门禁 → 生成 XML → 静态诊断 → 导入 → 设计态运行 → 两层验收（`tlk model` 命令组，含 `dict` 表字典） | 通用（角色须 SystemAdmin/SystemExpert） |
| model-interview | `model-interview/` | 需求访谈纪律（grilling）：一次一题、附推荐、事实自查决策归用户、共识前不动手 | 通用 |
| formbuilder-json-generator | `formbuilder-json-generator/` | Formbuilder 表单 JSON 生成（MODJSON 骨架：布局/控件/按钮/表达式规则）——model-designer 的 FB `formtemplate` 骨架设计知识来源 | 通用 |
| totallink-app-help | `totallink-app-help/` | TotalLINK App 壳项目知识库（linkquick / 公共函数 / 接口 / 模型 H5 编写指南 / 属性与 class 约定）——model-designer 生成 APP H5 模板时的客户端约定权威 | TotalLINK App 项目 |
| totallink-api | `totallink-api/` | 第三方系统 HTTP 对接契约：`linkUserLogin` / `linkDMDatasetResult` 等 8 个端点的权威文档（登录、查询、提交、上传；权威基准 LINKIIS）——开发对接代码时给 Agent 读的参照 | 第三方集成开发 |
| reimbursement-audit | `reimbursement-audit/` | 报销单全流程审计 | TotalLINK Development |
| email-sender | `email-sender/` | SMTP 邮件发送（SSL 465） | 通用 |
| pdf-generator | `pdf-generator/` | Markdown → 精美 HTML → A4 PDF（自动，Chrome headless 渲染） | 通用 |

## 技能关系

所有 skill 建立在 **totallink-base** 之上（环境配置、令牌、统一调用入口 `scripts/tlk.py`），按用途分四层：

```text
                        ┌────────────────────────────────────────────┐
                        │  totallink-base（根目录）：env / auth / call / tools │
                        └──────────────────┬─────────────────────────┘
        ┌──────────────┬───────────────┬──┴──────────┬──────────────┐
     环境准备        模型开发         场景应用       外部集成        通用工具
        │              │               │             │              │
     ai-init     model-designer  reimbursement-  totallink-api  email-sender
                 model-interview audit           （不走 tlk.py） pdf-generator
                 formbuilder-json-generator
                 totallink-app-help
```

- **环境准备**：`ai-init` 只在新环境第一次使用时跑一次（导入初始化模型组、建额度表）。
- **模型开发族**：`model-designer` 是主入口，其余三个是它按需引用的支撑——`model-interview` 提供访谈纪律、`formbuilder-json-generator` 提供 FB 表单骨架知识、`totallink-app-help` 提供 APP 壳客户端约定。
- **外部集成**：`totallink-api` 是**另一套独立通道**——用户名密码登录拿 `loginID` token 直调服务端 HTTP 端点，不使用 `tlk.py` 和 `tlk_` 令牌。给第三方系统写对接代码时才用。
- **通用工具**：`email-sender` / `pdf-generator` 与 TotalLINK 平台无耦合；`reimbursement-audit` 的 PDF 渲染依赖 `pdf-generator/scripts/`。

### 我该用哪个 skill？

| 我想…… | 用 |
|--------|-----|
| 第一次在新环境用 AI / 额度激活 | `ai-init`（先配好 totallink-base 令牌） |
| 把业务需求设计成数据模型、生成/导入模型 XML | `model-designer` |
| 设计 FB 网页表单的骨架 JSON | `model-designer` + `formbuilder-json-generator` |
| 给 TotalLINK App 写 H5 模板 / 前端脚本 | `model-designer` + `totallink-app-help` |
| 让第三方系统（ERP 等）调 TotalLINK 的数据能力 | `totallink-api` |
| 审计报销单 | `reimbursement-audit` |
| 发邮件 / 生成 PDF | `email-sender` / `pdf-generator` |

## 目录结构

```
TotalLINK/                        # 仓库根 = totallink-base（安装目录名）
├── SKILL.md                      # totallink-base
├── README.md
├── scripts/                      # base 自带的 Python 脚本
│   ├── tlk.py                    #   CLI 单入口（env / auth / call / tools + 插件发现）
│   ├── tlk_core.py               #   配置、请求、错误映射、设计态端点
│   ├── parse_tools.py            #   工具列表解析
│   └── preprocess.py             #   大数据自动摘要
├── ai-init/                      # AI 环境初始化 Skill
│   ├── SKILL.md
│   └── models/                   #   LINKAIINIT 模型组 6 个 XML（含 SYSINFOMATION230X#501 初始化动作）
├── model-designer/               # 数据模型设计 Skill
│   ├── SKILL.md
│   ├── tlk_group.py              #   注册 model 命令组（dict / export / import / run / validate）
│   ├── scripts/
│   │   └── validate_model.py     #   纯 XML 静态诊断（含 --env 模型族检查）
│   └── references/
│       ├── 13 个契约文档          #   fields / endpoints / discovery / link-flags / placeholders / …
│       ├── samples/              #   43 个精选真实模型 XML（运行器 / APP / FB）
│       └── samples-corpus/       #   673 个全量语料（六个项目，只读参照）
├── model-interview/              # 需求访谈纪律 Skill（grilling）
│   └── SKILL.md
├── formbuilder-json-generator/   # Formbuilder 表单 JSON 生成 Skill
│   ├── SKILL.md
│   └── references/               #   控件类型 / 布局与按钮 / 表达式规则 / 高级配置
├── totallink-app-help/           # TotalLINK App 壳项目知识库 Skill
│   ├── SKILL.md
│   └── references/               #   架构 / linkquick / 函数 / API / H5 指南 / 属性 / class / 平台专题
├── totallink-api/                # 第三方系统 HTTP 对接契约 Skill
│   ├── SKILL.md
│   └── references/               #   endpoints.md（8 端点契约）/ auth-and-errors.md（认证与错误）
├── reimbursement-audit/          # 报销审计 Skill
│   ├── SKILL.md
│   └── scripts/dedup_check.py    #   跨单/跨月发票查重
├── email-sender/                 # 通用：SMTP 邮件发送
│   └── SKILL.md
├── pdf-generator/                # 通用：Markdown → HTML → PDF
│   ├── SKILL.md
│   ├── references/               #   打印 CSS / 视觉方向 / 交付前检查
│   └── scripts/                  #   重复检测 / Chrome 渲染 / PDF 校验
└── docs/
    ├── adr/                      #   架构决策记录（0001 totallink-api 权威基准）
    └── handoff-formbuilder-app.md #  源码核对会话的交接记录（维护者内部文档）
```

## 前置条件

- Python 3.9+
- TotalLINK 账户及授权令牌（`tlk_` 开头）
- 报销单审计额外依赖：`pdfplumber`（PDF 校验）、Chrome / Chromium / Edge（PDF 渲染，脚本自动探测）

## 使用

以下命令属于 totallink-base（`totallink-api` 是纯文档 skill，无需配置、无命令，按其 `SKILL.md` 引导阅读 `references/` 即可）：

```bash
# 查询项目列表
python3 scripts/tlk.py env list

# 环境自检（项目 / URL / 用户 / 额度）
python3 scripts/tlk.py auth verify

# 搜索可用工具
python3 scripts/tlk.py tools search 报销

# 调用工具
python3 scripts/tlk.py call TMESCOM01 9 --script-type 0 --params-json '[""]'
```

> 令牌默认以 `--token "tlk_..."` 传入；不想让令牌进 shell 历史或进程列表时，可用 `--token-stdin`（从标准输入读）或 `TOTALLINK_TOKEN` 环境变量。
> 配置落盘在 `~/.totallink/config.json`，权限固定 `600`。
