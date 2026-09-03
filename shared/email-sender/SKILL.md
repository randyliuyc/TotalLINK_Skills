---
name: totallink-email-sender
slug: totallink-email
description:
  TotalLINK 邮件发送公共 Skill，提供通过 SMTP 发送邮件的通用能力。
  被报销审核等场景化 Skill 引用，可复用于任何需要发送邮件的场景。
metadata:
  workbuddy:
    env:
      SMTP_HOST: "smtp.163.com"
      SMTP_PORT: "465"
      SMTP_FROM: ""
      SMTP_PASSWORD: ""
      SMTP_TO_DEFAULT: ""
    note: "SMTP 授权码首次使用时向用户索取，保存到 ~/.totallink/smtp.json（chmod 600）复用"
---

> **安全约定（上游自带，更新时勿回退）**
> 1. 凭据一律存 `~/.totallink/smtp.json`（权限 600），**禁止**写入 `~/.workbuddy/MEMORY.md`、`SOUL.md`、`USER.md` 等会被注入模型上下文的文件
> 2. 发送前必须向用户确认收件人地址，禁止用 `SMTP_TO_DEFAULT` 跳过确认

# 邮件发送 Skill

## 概述

通过 SMTP 发送邮件，支持纯文本正文和附件。优先使用网易邮箱（smtp.163.com SSL 465）。

> ⚠️ 发送邮件是不可逆的外部动作。执行 `send_message` 前必须向用户确认**收件人地址**。

## 配置

首次使用时向用户索取发件人邮箱与 SMTP 授权码，保存到 `~/.totallink/smtp.json`（权限 600）供后续复用：

```bash
mkdir -p ~/.totallink && umask 077 && cat > ~/.totallink/smtp.json << 'EOF'
{
  "host": "smtp.163.com",
  "port": 465,
  "from_addr": "your邮箱@example.com",
  "password": "SMTP授权码"
}
EOF
chmod 600 ~/.totallink/smtp.json
```

```
SMTP服务器：smtp.163.com
SSL端口：465
发件人邮箱：用户提供
授权码：用户提供（非邮箱密码，需在邮箱设置中开启 SMTP 服务获取）
```

## 发送脚本

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import sys

def send_email(subject, body, to_addr, attachments=None, smtp_host="smtp.163.com",
               smtp_port=465, from_addr=None, password=None):
    """
    发送邮件，支持附件。

    Args:
        subject: 邮件主题
        body: 纯文本正文
        to_addr: 收件人邮箱（单个字符串）
        attachments: [(文件路径, 文件名), ...]
    """
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if attachments:
        for filepath, filename in attachments:
            with open(filepath, "rb") as f:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition", "attachment",
                    filename=("utf-8", "", filename)
                )
                msg.attach(attachment)

    with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=30) as server:
        server.login(from_addr, password)
        server.send_message(msg)

    print(f"邮件已发送至 {to_addr}")


if __name__ == "__main__":
    # 命令行调用示例
    # python send_email.py <subject> <to_addr> <body> [attachment_path]
    send_email(
        subject=sys.argv[1],
        body=sys.argv[2],
        to_addr=sys.argv[3],
        attachments=[(sys.argv[4], sys.argv[4].split("/")[-1])] if len(sys.argv) > 4 else None
    )
```

## 调用方式

场景化 Skill 可直接内联发送逻辑，无需保存脚本文件。示例：

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# 从 ~/.totallink/smtp.json（chmod 600）读取；缺失则向用户索取
import json, os
cfg = json.load(open(os.path.expanduser("~/.totallink/smtp.json"), encoding="utf-8"))
from_addr = cfg["from_addr"]
password = cfg["password"]
to_addr = "<用户本次确认的收件人地址>"   # 禁止硬编码，发送前必须确认

msg = MIMEMultipart()
msg["From"] = from_addr
msg["To"] = to_addr
msg["Subject"] = "邮件主题"
msg.attach(MIMEText("邮件正文", "plain", "utf-8"))

# 附件（如 PDF）
with open("report.pdf", "rb") as f:
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=("utf-8", "", "report.pdf"))
    msg.attach(attachment)

with smtplib.SMTP_SSL("smtp.163.com", 465, timeout=30) as server:
    server.login(from_addr, password)
    server.send_message(msg)
```

## 注意事项

- 使用 SSL 465 端口，非 TLS 587
- 授权码非邮箱登录密码，需在邮箱设置中开启 SMTP 服务后获取
- 附件文件名含中文时需 encode 为 utf-8
- 超时时间设为 30 秒
