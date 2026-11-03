# 模型的三个消费环境

同一份模型定义（SYSSEARCH / 模型 XML）被三个环境消费。本 Skill 当前只覆盖**模型运行器**场景。

| 环境 | 入口 | 消费的字段 | 本版状态 |
|------|------|-----------|---------|
| **模型运行器（fDataAnalysis）** | WinForms：`fDataModelList` → 双击/btnTest → `fDataAnalysis` | SQLScript 四件套、参数四件套、CallFunction、JavaScript、ModelSetting、ChartType、CubeSetting、全部 `--LINKxxx` 标记 | ✅ 本版覆盖 |
| **TotalLINK APP（H5 界面）** | 移动端按 H5 属性渲染 | `H5List`、`H5Detail`、`H5Edit`、`H5Chart`、`H5MaxLines`、`H5NewRec`、`H5Para`、`H5AttPara`、`H5GridHeader`、`H5GridDetail` | ⛔ 不覆盖。字段留空/保持原值（硬规则 5） |
| **BS 设计器** | 浏览器端，调用 LINKIIS 端点 | 与运行器共享模型定义（端点侧解析） | ⛔ 不覆盖 |

## 给生成阶段的约束

1. 只为运行器场景生成/修改脚本字段；H5 字段防呆（见 SKILL.md 硬规则 5）。
2. 用户需求如果明确说「APP 上用」「网页上用」，提醒用户：该场景本 Skill 不保证，需人工在对应环境验证；`H5*` 字段内容需要另行设计。
3. 未来扩展本 Skill 时：在此文档补齐各环境字段消费细节，并在 SKILL.md 增加对应工作流章节，不重构语法参考（fields/link-flags/callfunction-actions/placeholders 是环境无关的）。
