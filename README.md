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
| reimbursement-audit | 报销单全流程审计 | TotalLINK Development |
| shared/email-sender | SMTP 邮件发送（SSL 465） | 通用 |
| shared/pdf-generator | Markdown → 精美 HTML → A4 PDF（自动，Chrome headless 渲染） | 通用 |

## 目录结构

```
totallink-base/
├── SKILL.md                 # totallink-base（多平台通用）
├── README.md
├── scripts/                 # Python 脚本
│   ├── tlk.py               #   CLI 单入口（env / auth / call / tools）
│   ├── tlk_core.py          #   配置、请求、错误映射
│   ├── parse_tools.py       #   工具列表解析
│   └── preprocess.py        #   大数据自动摘要
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
