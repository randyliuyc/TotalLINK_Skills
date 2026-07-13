# TotalLINK Skills

WorkBuddy 技能包，对接 TotalLINK 数据分析平台，提供报销单审计等自动化能力。

## Skills

| Skill | 用途 |
|-------|------|
| `totallink-base` | 基础 Skill：认证管理、API 调用模板、工具发现 |
| `reimbursement-audit` | 报销单全流程审计：查询 → 发票识别 → 报告 → PDF → 邮件 |
| `shared/email-sender` | SMTP 邮件发送（SSL 465） |
| `shared/pdf-generator` | Markdown → Pandoc → WeasyPrint 生成 A4 PDF |

## 安装

```bash
git clone https://github.com/randyliuyc/TotalLINK_Skills.git ~/.workbuddy/skills/TotalLINK
```

重启 WorkBuddy 后自动加载。

## 前置条件

- **TotalLINK 认证**：使用 `totallink-base` 前需提供 TotalLINK 授权令牌和服务地址
- **报销单审计**（`reimbursement-audit`）：
  - Python venv 中安装 `pdfplumber`
  - Pandoc CLI + WeasyPrint（用于 PDF 生成）
  - SMTP 授权码（用于邮件发送）
- 邮箱 SMTP：支持 163 邮箱 SSL 465 端口

## 使用

在 WorkBuddy 中直接描述需求：

```
帮我审计最近一周的报销单
```

Skill 会自动执行：查询报销单 → 下载附件识别发票 → 生成审计报告 → 发送邮件。

## 结构

```
TotalLINK/
├── totallink-base/SKILL.md
├── reimbursement-audit/SKILL.md
└── shared/
    ├── email-sender/SKILL.md
    └── pdf-generator/SKILL.md
```
