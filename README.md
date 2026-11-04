# TotalLINK Skills

对接 [TotalLINK](https://totalink.io) 数据分析平台的 AI Skill 集合。

**一个文件，多平台通用**：根 `SKILL.md` 同时适配 WorkBuddy（AskUserQuestion 弹窗）和其他 AI Agent（文字交互）。脚本层纯 Python，跨平台可运行。

## 安装

```bash
git clone https://gitee.com/randyliuyc/TotalLINK_Skill.git <目标目录>
```

| 平台 | 安装路径 | 加载文件 |
|------|---------|---------|
| WorkBuddy | `~/.workbuddy/skills/TotalLINK/` | 根 `SKILL.md` |
| 其他 Agent | 任意目录 | 根 `SKILL.md` |

## 技能列表

| Skill | 用途 | 适用范围 |
|-------|------|---------|
| totallink-base | 认证、工具发现、API 调用、数据预处理 | 通用 |
| model-designer | 数据模型设计：需求问卷与任务书门禁 → 生成 XML → 静态诊断 → 导入 → 设计态运行 → 两层验收（`tlk model` 命令组，含 `dict` 表字典） | 通用（角色须 SystemAdmin/SystemExpert） |
| model-interview | 需求访谈纪律（grilling）：一次一题、附推荐、事实自查决策归用户、共识前不动手 | 通用 |
| formbuilder-json-generator | Formbuilder 表单 JSON 生成（MODJSON 骨架：布局/控件/按钮/表达式规则）——model-designer 的 FB `formtemplate` 骨架设计知识来源 | 通用 |
| totallink-app-help | TotalLINK App 壳项目知识库（linkquick / 公共函数 / 接口 / 模型 H5 编写指南 / 属性与 class 约定）——model-designer 生成 APP H5 模板时的客户端约定权威 | TotalLINK App 项目 |
| reimbursement-audit | 报销单全流程审计 | TotalLINK Development |
| shared/email-sender | SMTP 邮件发送（SSL 465） | 通用 |
| shared/pdf-generator | Markdown → 精美 HTML → A4 PDF（自动，Chrome headless 渲染） | 通用 |

## 目录结构

```
totallink-base/
├── SKILL.md                 # totallink-base（多平台通用）
├── README.md
├── scripts/                 # Python 脚本
│   ├── tlk.py               #   CLI 单入口（env / auth / call / tools + 插件发现）
│   ├── tlk_core.py          #   配置、请求、错误映射、设计态端点
│   ├── parse_tools.py       #   工具列表解析
│   └── preprocess.py        #   大数据自动摘要
├── model-designer/          # 数据模型设计 Skill
│   ├── SKILL.md
│   ├── tlk_group.py         #   注册 model 命令组（dict / export / import / run / validate）
│   ├── references/          #   字段表 / 端点契约 / 问卷与任务书 / 占位符 / 脚本标记 / 模型设置 / JS 钩子
│   │   ├── samples/         #   43 个精选真实模型 XML（运行器 / APP / FB）
│   │   └── samples-corpus/  #   640 个全量语料（四个项目，只读参照）
│   └── scripts/
│       └── validate_model.py #  纯 XML 静态诊断（含 --env 模型族检查）
├── model-interview/         # 需求访谈纪律 Skill（grilling）
│   └── SKILL.md
├── formbuilder-json-generator/ # Formbuilder 表单 JSON 生成 Skill
│   ├── SKILL.md
│   └── references/          #   控件类型 / 布局与按钮 / 表达式规则 / 高级配置
├── totallink-app-help/      # TotalLINK App 壳项目知识库 Skill
│   ├── SKILL.md
│   └── references/          #   架构 / linkquick / 函数 / API / H5 指南 / 属性 / class / 平台专题
├── reimbursement-audit/     # 报销审计 Skill
│   └── SKILL.md
└── shared/                  # 通用 Skill
    ├── email-sender/SKILL.md
    └── pdf-generator/       # Markdown → HTML → PDF
        ├── SKILL.md
        ├── references/      # 打印 CSS / 视觉方向 / 交付前检查
        └── scripts/         # 重复检测 / Chrome 渲染 / PDF 校验
```

## 前置条件

- Python 3.9+
- TotalLINK 账户及授权令牌（`tlk_` 开头）
- 报销单审计额外依赖：`pdfplumber`（PDF 校验）、Chrome / Chromium / Edge（PDF 渲染，脚本自动探测）

## 使用

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
