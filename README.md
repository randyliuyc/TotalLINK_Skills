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
| shared/pdf-generator | Markdown → PDF | 通用 |

## 目录结构

```
TotalLINK_Skills/
├── SKILL.md                 # totallink-base（多平台通用）
├── README.md
├── scripts/                 # Python 脚本
│   ├── totallink_api.py     #   统一 API 调用
│   ├── parse_tools.py       #   工具列表解析
│   └── preprocess.py        #   大数据自动摘要
├── reimbursement-audit/     # 报销审计 Skill
│   └── SKILL.md
└── shared/                  # 通用 Skill
    ├── email-sender/SKILL.md
    └── pdf-generator/SKILL.md
```

## 前置条件

- Python 3.9+
- TotalLINK 账户及授权令牌（`tlk_` 开头）
- 报销单审计额外依赖：`pdfplumber`、`pandoc`、`weasyprint`

## 使用

```bash
# 查询项目列表
python3 scripts/totallink_api.py --list-projects

# 搜索可用工具
python3 scripts/totallink_api.py --dm-code SEARCHLIST --dm-num 100 \
  --params "" --script-type 0 | python3 scripts/parse_tools.py

# 查询积分
python3 scripts/totallink_api.py --dm-code SYSINFOMATION --dm-num 220 \
  --script-type 0
```
