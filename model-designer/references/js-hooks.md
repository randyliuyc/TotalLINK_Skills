# JavaScript 钩子参考（js-hooks）

> 证据来源：2026-11-04 语料盘点（`samples-corpus/KEEWAYZUPPDA` 139 个模型中 26 个非空 ≈ 19%；FB 侧 TMESPUR 4/259，全部是同一 `contextTap`）。
> 运行链路：APP 主链路把 `JAVASCRIPT` 字段原样下发给壳（占位符已展开，`SysDataModel.vb:4554`）；顶层语句在页面加载时即执行，可做初始化脚本。
> 技术栈：mui + jQuery + HTML5+（`plus.webview`）。函数用 `functionName = function(入参){}` 形式全局定义，**无需注册**——引擎按函数名在固定时机调用。

## 钩子选型（问卷三问，命中才写 JS）

| 触发条件 | 必写钩子 | 可选配套 |
|---|---|---|
| 含扫码输入 | `scan_para` | `scan_if` / `scan_ajax` / `scanAfterAction` |
| 提交/更新/删除前有跨字段业务校验 | `beforeFunction` | — |
| 动作完成后要自动刷新/跳焦点 | `afterFunction` | `Save_Data`（扫码子页回列表） |

约 81% 的 APP 模型不需要 JS。FB 详情页只有 `contextTap` 一种钩子。

## 钩子清单（平台约定，勿自创函数名）

| 钩子 | 触发时机 | 签名/入参 | 返回约定 | 证据 |
|---|---|---|---|---|
| `scan_para` | 扫码返回 | `(id, r)`：`id`=目标控件 id 或 `"linkinput"`（模型参数框），`r`=扫码原文 | 无；自行填充控件值（`"#"+r+"#"`） | KEEWAYZUP10#10 L414 |
| `scan_if` | 扫码开始前 | `()` | 返回数字=扫码模式（如 `return 2;`） | KEEWAYZUP2010X#502 L274 |
| `scan_ajax` | 扫码内容为结构化数组 | `(id, arr, res)`：`arr[0]`=URL、`[1]`=loginID、`[2]`=dmCode、`[3]`=dmNum、`[4]`=参数 | 自行 `mui.ajax` 取数后填充 | KEEWAYZUP605X#1521 L99 |
| `scanAfterAction` | 扫码处理完成后 | `(id)` 或 `(id, r)`（版本不一） | 无；常做数据检查提示/自动查询 `showModelData(reParaList())`/焦点跳转 `keep_focus(...)` | KEEWAYZUP10#10、KEEWAYZUP30#5 L445、KEEWAYZUP54#10 L397 |
| `beforeFunction` | 模型函数（提交/更新/删除）执行前 | `(sta[, id])` | **返回 `true` 即中断执行**（校验不过弹 alert 后 `return true`） | KEEWAYZUP10#10 L431 |
| `afterFunction` | 模型函数执行后 | `(id)`：触发按钮 id（如 `linkquick12`=删除） | 无；`reloadModelData()` 刷新 | KEEWAYZUP10#10 L447、KEEWAYZUP56#10 L327 |
| `Save_Data` | 扫码编辑子页返回时 | `()` | 无；`mui.fire(plus.webview.getWebviewById(...))` 通知列表页刷新 | KEEWAYZUP2010X#502 L284 |
| `contextTap`（FB） | 详情页列表行点击 | `(contextid, linktitle, linkrefresh, linkparafill, cRDs)` | 无；localStorage 暂存 + `showAttachModelPara(...)` 弹补充参数 | TMESPUR01/02/03/06 #10 |

自由函数（`openZoom`、`linkquickAction1`、`openFileMethod`、匿名 touch 监听等）不是钩子——它们由模型内 HTML 属性（`onkeyup`/`onclick`）、`CallFunction` 的 `formula:"{openFileMethod(result)}"` 或平台 API（`addIcons`）引用。

## 常用平台 API（脚本内可直接调）

`scan_impl`（执行扫码）、`reParaList`（收集当前参数）、`showModelData(dmPara)` / `reloadModelData()`（查询/刷新）、`keep_focus(控件名)`、`DMContextAction(...)` / `currRDs(ele)`（行上下文动作）、`pre_post`、`showAttachModelPara(...)`、`openFile(...)`、`addIcons(...)`、`mui.fire`。

## 克隆样板（samples/ 内）

| 需求 | 克隆来源 |
|---|---|
| 全套钩子总览（scan_para + scanAfterAction + beforeFunction + afterFunction） | `KEEWAYZUP10#10-订单收货.xml`（L414-450） |
| 扫码后数据检查 + 自动查询 | `KEEWAYZUP30#5`（corpus，L435-452） |
| 纯 UI 增强（双指缩放，无钩子） | `KEEWAYZUP2010X#703-图片展示.xml`（L92-110） |
| FB 行点击补充参数 | `TMESPUR01#10-采购申请详情.xml`（L339-348） |

## 注意

- 顶层语句即页面初始化脚本（如 `$("#linkok").hide()`），不只是函数定义区。
- 服务端 js 片段的可靠注入通道是客户端 `load_js`（先移除旧 `.linkjavascript` 再 append）；`reloadAfter()` 是模型自定义初始化钩子；提交参数按 DOM 顺序由 `reParaList`/`jq_para` 收集成 `{0}{1}…`——这些客户端机制详见 `totallink-app-help/references/h5-guide.md`（§3.3/§3.4）。
- `JavaScript` 字段属 `BRACE_FIELDS`：脚本内字面花括号需 `{{ }}` 转义（经 string.Format 处理）。
- 任务书按钩子选型结果列 JS 清单；验收时人工断言含扫码/校验/刷新行为。
