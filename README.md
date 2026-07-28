# TotalLINK Skills

对接 [TotalLINK](https://totalink.io) 数据分析平台的 AI Skill 集合，提供认证管理、API 调用、数据分析等通用能力，及报销单审计等场景化自动化。

## 快速开始

### 任意 AI Agent（推荐）

1. 克隆仓库
2. 告知 Agent 加载根目录的 `SKILL.md`
3. 提供 TotalLINK 令牌和服务地址

### WorkBuddy

```bash
git clone https://gitee.com/randyliuyc/TotalLINK_Skill.git ~/.workbuddy/skills/TotalLINK
```

重启 WorkBuddy 后自动加载 `workbuddy/SKILL.md`。

## 技能列表

| Skill | 位置 | 用途 | 适用范围 |
|-------|------|------|---------|
| totallink-base | `SKILL.md` | 认证、工具发现、API 调用、数据预处理 | 通用 |
| reimbursement-audit | `workbuddy/reimbursement-audit/` | 报销单全流程审计：查询 → 发票识别 → 报告 → PDF → 邮件 | TotalLINK Development |
| email-sender | `workbuddy/shared/email-sender/` | SMTP 邮件发送（SSL 465） | 通用 |
| pdf-generator | `workbuddy/shared/pdf-generator/` | Markdown → Pandoc → WeasyPrint 生成 A4 PDF | 通用 |

## 目录结构

```
TotalLINK_Skills/
├── SKILL.md                      # 通用版基础 Skill（跨平台入口）
├── README.md
├── scripts/                      # Python 脚本（跨平台核心）
│   ├── totallink_api.py          #   统一 API 调用
│   ├── parse_tools.py            #   工具列表解析
│   └── preprocess.py             #   大数据自动摘要
└── workbuddy/                    # WorkBuddy 平台专用 Skill
    ├── SKILL.md                  #   基础 Skill（含 AskUserQuestion 交互）
    ├── reimbursement-audit/
    │   └── SKILL.md
    └── shared/
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
