---
name: totallink-app-help
description: TotalLINK App（HBuilder 5+ Runtime / HTML5+ / mui / jQuery）项目知识库。当用户询问本项目相关问题时使用：项目结构与页面、linkquick 属性全套用法（linkquick="1"~"14" 及各分支行为）、核心公共函数（DMContextAction/contextCall/linkAjax/防重复点击等）、服务端接口约定、页面间通信与状态管理、多语言、离线模式、以及本项目常见的"一次点击触发两次请求"等调试经验。遇到本项目代码问题（js/linkshared.js、js/contentlist.js、各 html 页面）应先读本 skill 的 references 再作答。
---

# TotalLINK App 项目知识库

本 skill 是 TotalLINK App（HBuilder 5+ Runtime，mui + jQuery + ECharts，服务端为 formbuilder 低代码平台）的项目知识库。回答本项目问题前，先按主题读取对应 reference，不要凭空猜测项目细节。

## 参考资料（按需读取）

| 文件 | 内容 | 何时读 |
|---|---|---|
| `references/architecture.md` | 项目整体结构：manifest 配置、全部页面清单及用途、js 文件职责表 | 问项目结构、某个页面/文件是干嘛的 |
| `references/linkquick.md` | **linkquick 属性完整用法**：事件委托机制、type 1~16 分发表、可用自定义属性、配套 AJAX 接口、防重复点击、以及本项目"双委托重复触发"调试案例 | 问 linkquick、按钮快捷功能、重复点击/重复请求问题 |
| `references/functions.md` | 核心公共函数清单（js/linkshared.js）：签名、用途、关键参数 | 问某函数怎么用、页面跳转/等待框/多语言/定位等 |
| `references/api.md` | 服务端接口约定：globleServer/LinkID、接口清单、parajson 参数结构、离线模式 | 问接口、请求参数、后端对接 |
| `references/methods.md` | **方法库（以源码核实为准）**：扫描/钩子/UI/防重复/音频/接口/表单/上传/文件/SQLite 等逐条归档（含行号、真实签名、"未找到"更正清单） | 问某方法是否存在、怎么用、模型页面可重写哪些扩展点 |
| `references/attributes.md` | **自定义属性用法总结（以源码检索为准）**：link- 前缀系列、模型标识参数、执行控制、行数据、硬件/语音/菜单、属性继承与布尔惯例规律 | 问某 HTML 自定义属性（如 linkquick/linklocation/para/btnid 等）怎么用、元素上能配哪些属性 |
| `references/classes-ids.md` | **约定 class 与特定元素 id（以源码检索为准）**：交互控件 class（linkpicker/linkdate/linkmultiple/linkcheckbox 等）、卡片/媒体/列表/提示 class、各页面固定骨架 id（linkinput/list/paralist/linkeditlist/contextmenulist 等）、模型 H5 可用扩展点清单 | 问某 class/id 是干嘛的、写模型 H5 时该用什么控件 class/id |
| `references/platform.md` | **平台专题（以源码核实为准）**：CSS 定制分布（mui.min.css 内 .link* 行段图、沉浸式状态栏 js 方案）、MQTT 消息链路（配置/订阅/收发/重连）、离线 SQLite（表结构/typeMappings/CRUD）、推送消息（createPushMsg/clickPushMethod/notify 统一分发） | 问样式定制在哪、MQTT 怎么配置收发、离线数据存哪张表、推送/待办消息怎么处理 |
| `references/h5-guide.md` | **模型 H5 编写指南（动态渲染机制）**：五个界面（contentlist/modelpara/attachmodelpara/newrecord/linkmemo）由服务端返回片段动态 append 的完整链路与接口字段、离线模板机制（#字段#/lang:{} / id="#" 占位）、控件值绑定与提交链路、模型 JS 通道（load_js/reloadAfter）、多语言、注意事项 | **用户问"模型 H5 怎么写/AI 帮我写个 H5 界面"时必读**，配合 classes-ids.md（控件 class）和 attributes.md（属性）使用 |

## 回答本项目问题的规则

1. **行号以当前源码为准**：本项目处于持续修改中，skill 中的行号是编写时的快照，引用代码前用 read_file / search_content 核实。
2. **区分两条委托链**：本项目同时存在"按 id 绑定的特化委托"（contentlist.js 928-991）和"按 linkquick 属性的全局委托"（linkshared.js ~4393）。排查"一次点击触发两次相同请求"时优先怀疑双委托命中同一 DOM（详见 linkquick.md §9）。
3. **区分长按菜单的两段式调用**：点击 `#contextmenulist` 里的附加功能项（如 btnid=501）设计上就会发两次请求（linkDMContextActionInfo → linkDMConditionAction action=6 校验），这不是 bug，不要误判为重复触发。
4. **manifest.json 的 dependencies.pages 是陈旧配置**，与实际目录不符，不要以它为页面清单依据。
5. 用户给出真机日志（HBuilder 控制台、`file:///storage/emulated/0/...` 路径）时，按 linkquick.md §9 的插桩/判读方法分析，先分清"业务链路的多步请求"和"真正的重复触发"。

## 快速索引

- 入口/登录：index.html + js/index.js（globleServer/globleUser 登录态）
- 核心业务页：contentlist.html + js/contentlist.js（模型数据列表）
- 全局公共库：js/linkshared.js（314KB+，几乎所有公共函数在此）
- 服务端地址：全局 `globleServer`（memGet），请求令牌 `LinkID`
- 离线模式：`ifOffline()` = memGet("offline")=="1"，走 SQLite
- 多语言：`rLang("key.sub")`，语言包 libs/lang/*.json（12 种）

## 与 model-designer 的分工

> 本 skill 是 APP 壳工程的知识库（壳开发、排障、平台机制）。`model-designer` skill 生成模型 H5 模板（H5List/H5Para/H5Edit 等）时，控件 class 用 `classes-ids.md`、自定义属性用 `attributes.md`、动态渲染与提交取值链路用 `h5-guide.md`（§3）、模型 JS 钩子用 `model-designer/references/js-hooks.md`。
