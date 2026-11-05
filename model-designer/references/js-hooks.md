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
| `reScanFlag` | 保存后判断是否允许继续扫码 | `()` | 返回真值=允许重复扫码（如 functype 含 `"new"` 时） | TMESPDA130#10 L730± |
| `linkDMFuncBackImpl` | 开窗（linkdatasearch）选行返回后 | `(数据, 控件)` 上下文 | 无；典型链：扣减剩余需领量 → 清空输入 → `showModelData(null)` 关窗 → `mui.fire` 通知列表刷新 | TMESPDA130#502 L274-318 |
| `repeatTime` | 定时器（`linkpreprocess` 触发间隔） | `()` | 无；控制 #301 型按钮控制模型的轮询间隔（如 10 秒） | TMESPDA130#10 L726-729 |
| `contextTap`（FB） | 详情页列表行点击 | `(contextid, linktitle, linkrefresh, linkparafill, cRDs)` | 无；localStorage 暂存 + `showAttachModelPara(...)` 弹补充参数 | TMESPUR01/02/03/06 #10 |

**扫码解析链（TAMPERAPP 标杆，2026-11-05）**：主模型 JS 与无界面服务模型配合——

1. 主模型配 15xx 段服务模型：#1521 校验单据（返回 `DOCNUM`+`提示`列，值 `'OK'` 或错误文案）；#1522 拆二维码（`;` 分隔）返回 `DATACK/QTY/PK`
2. 跨模型传参：后一模型脚本用 `DECLARE @DOCNUM = '#DOCNUM#'` 接收**前一模型结果集列**（经 `#列#` 注入）
3. 主模型 JS：`scan_para` 把扫码值写 `"#"+r+"#"` → `scanAfterAction` 检查 `$("#提示").val()=="OK"`，通过则 `reParaList()+showModelData()` 刷新参数页，否则 alert
4. `beforeFunction` 保存前校验 `$("#DATACK").val()=="OK"`，不过则 alert + `return true` 阻断

自由函数（`openZoom`、`linkquickAction1`、`openFileMethod`、匿名 touch 监听等）不是钩子——它们由模型内 HTML 属性（`onkeyup`/`onclick`）、`CallFunction` 的 `formula:"{openFileMethod(result)}"` 或平台 API（`addIcons`）引用。

## 常用平台 API（脚本内可直接调）

`scan_impl`（执行扫码）、`reParaList`（收集当前参数）、`showModelData(dmPara)` / `reloadModelData()`（查询/刷新）、`keep_focus(控件名)`、`DMContextAction(...)` / `currRDs(ele)`（行上下文动作）、`pre_post`、`showAttachModelPara(...)`、`openFile(...)`、`addIcons(...)`、`mui.fire`。

## 克隆样板（samples/ 内）

| 需求 | 克隆来源 |
|---|---|
| 全套钩子总览（scan_para + scanAfterAction + beforeFunction + afterFunction） | `KEEWAYZUP10#10-订单收货.xml`（L414-450） |
| 扫码解析链标杆（1521→1522 服务模型 + scan_after 校验 + beforeFunction DATACK 阻断） | `samples-corpus/TAMPERAPP/TMESPDA130#10-领料出库.xml`（L667-765）+ `TMESPDA13010X#1521/#1522` |
| 开窗返回回调（linkDMFuncBackImpl 扣量/清空/关窗/通知刷新） | `samples-corpus/TAMPERAPP/TMESPDA13010X#502-公斤领用.xml`（L274-318） |
| 扫码后数据检查 + 自动查询 | `KEEWAYZUP30#5`（corpus，L435-452） |
| 纯 UI 增强（双指缩放，无钩子） | `KEEWAYZUP2010X#703-图片展示.xml`（L92-110） |
| FB 行点击补充参数 | `TMESPUR01#10-采购申请详情.xml`（L339-348） |

## 注意

- 顶层语句即页面初始化脚本（如 `$("#linkok").hide()`），不只是函数定义区。
- 服务端 js 片段的可靠注入通道是客户端 `load_js`（先移除旧 `.linkjavascript` 再 append）；`reloadAfter()` 是模型自定义初始化钩子；提交参数按 DOM 顺序由 `reParaList`/`jq_para` 收集成 `{0}{1}…`——这些客户端机制详见 `totallink-app-help/references/h5-guide.md`（§3.3/§3.4）。
- `JavaScript` 字段属 `BRACE_FIELDS`：脚本内字面花括号需 `{{ }}` 转义（经 string.Format 处理）。
- 任务书按钩子选型结果列 JS 清单；验收时人工断言含扫码/校验/刷新行为。
