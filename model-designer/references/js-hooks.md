# JavaScript 钩子参考（js-hooks）

> 证据来源：2026-11-04 语料盘点（`samples-corpus/KEEWAYZUPPDA` 139 个模型中 26 个非空 ≈ 19%；FB 侧 TMESPUR 4/259，全部是同一 `contextTap`）。
> **2026-11-12 APP 壳源码核实**（`TotalLINKAPP/app/js`，未混淆源码；反直觉结论主会话复核行号）：钩子签名/调用时机/返回语义逐条对齐壳源码，修正 2 处语料误读（repeatTime、linkDMFuncBackImpl）。
> 运行链路：APP 主链路把 `JAVASCRIPT` 字段原样下发给壳（占位符已展开，`SysDataModel.vb:4554`）；顶层语句在页面加载时即执行，可做初始化脚本。
> 技术栈：mui + jQuery + HTML5+（`plus.webview`）。函数用 `functionName = function(入参){}` 形式全局定义，**无需注册**——壳按函数名直接调用（**无 typeof 存在性判断**，唯一例外 `searchContent&&searchContent()` 短路写法，`linkshared.js:102`）；模型 JS 经 `load_js` 新建 inline script 注入，函数声明同名覆盖壳默认实现（壳在 `linkshared.js` 内为每个钩子都留了默认实现）。

## 钩子选型（问卷三问，命中才写 JS）

| 触发条件 | 必写钩子 | 可选配套 |
|---|---|---|
| 含扫码输入 | `scan_para` | `scan_if` / `scan_ajax` / `scanAfterAction` |
| 提交/更新/删除前有跨字段业务校验 | `beforeFunction` | — |
| 动作完成后要自动刷新/跳焦点 | `afterFunction` | `Save_Data`（扫码子页回列表） |

约 81% 的 APP 模型不需要 JS。FB 详情页只有 `contextTap` 一种钩子。

## 钩子清单（平台约定，勿自创函数名）

| 钩子 | 触发时机 | 签名/入参 | 返回约定 | 证据（APP 壳源码 `TotalLINKAPP/app/js/`） |
|---|---|---|---|---|
| `scan_para` | 扫码返回（摄像头回调 `scaned`/Android 扫码枪广播 `SCANRESULT`/键盘 Enter+TAB 三入口汇合） | 壳默认实现三参 `(id, r, type)`；模型常写 `(id, r)`（兼容，`type` 仅扫码枪 search 场景传） | 无；自行填充控件值（`"#"+r+"#"`）。**壳默认实现**（`linkshared.js:41-73`）：`id=="linkinput"` 且 `autoFlag=='1'` 时自动加双 `#` 包裹后调 `scan_impl`；`linktextarea` 按 `delimiter` 属性拼接追加 | 定义 `linkshared.js:41`；调用点 :1613/:1660/:1665/:2809/:2811 |
| `scan_if` | 扫码内容分发前（`scan_impl` 内） | `(r)`：扫码原文（模型常写 `()`，兼容） | 返回数字=扫码模式（1=JSON `deal_json` 直填 / 2=`#…#`或`$…$`结构化走 `scan_ajax` / 其他=直接写 input） | 定义 `linkshared.js:119`；唯一调用点 :134 `switch(scan_if(r))` |
| `scan_ajax` | 扫码内容为 `#…#`/`$…$` 结构化 | `(id, arr, res, type)`：`arr[0]`=URL、`[1]`=loginID、`[2]`=dmCode、`[3]`=dmNum、`[4]`=参数（壳 POST `linkDMDatasetResult` 后把响应传给本钩子） | 自行取数填充；返回后壳走 `deal_json`+`scanAfterActionImpl` | 定义 `linkshared.js:198`；唯一调用点 :161（scan_impl case 2） |
| `scanAfterAction` | 扫码处理完成后（`scanAfterActionImpl` 内，`LINK_ASYNC` 恢复 true 后） | `(id)` 或 `(id, r)`（版本不一） | 无；常做数据检查提示/自动查询 `showModelData(reParaList())`/焦点跳转 `keep_focus(...)` | 壳默认空实现 `linkshared.js:110`；调用点 :103。注意 `scanAfterActionImpl`（:90）是壳内部函数不可重写 |
| `beforeFunction` | 模型函数执行前；**sta 白名单** `BEFORE_STA_ARRAY=["para","attach","new","memo","linkquick","autoSave","content","upload"]`（`linkshared.js:4297`），sta 不在名单钩子不被调用 | `(sta, id)`：`sta`∈白名单；`id`=动作标识（content 场景=按钮 id 如 `linkpreprocess`/`linkedit`/`linkremove`，linkquick 场景=linkquick 值） | **返回真值即中断**（壳默认恒 `return false`；调用模式 `if(BEFORE_STA_ARRAY.indexOf(sta)!=-1 && beforeFunction(sta,id)) return;`） | 默认实现 `linkshared.js:4299-4301`；调用点 contentlist.js:930/939/948/…、modelpara.js:104、linkshared.js:95/4468/8672 |
| `afterFunction` | 模型函数执行后；同一 sta 白名单（`AFTER_STA_ARRAY`，:4298） | `(sta, id)`：同 beforeFunction | 无。**时机注意**：contentlist 各 tap 是动作**发起后同步**调用（动作结果未返回）；「完成后」触发的只有 recSave 回调（成功/失败**都**触发，`linkshared.js:1763/1766`）、linkquickAction 异步回调（:4530 等）、linkmemo finally（失败也触发）——刷新逻辑放这里要确认所在链路是哪种 | 默认实现 `linkshared.js:4302`；contentlist.js:932/941/…（发起后同步） |
| `Save_Data` | **beforeback（页面返回/关闭前）与右滑返回手势**：contentlist/modelpara/attachmodelpara/linkmemo/newrecord/menulist 各页 `onBeforeBack` 调 `Save_Data(mui.currentWebview,"webpage")`；右滑 `linkshared.js:2154` | 壳默认实现 `(data, ele)` 把 webview 关键状态（modelParams/currRowData/functype）去重后存 localStorage `"webpage"` | 无；模型 JS 重写后做自定义返回动作（典型 `mui.fire(plus.webview.getWebviewById(...))` 通知列表页刷新）——重写会顶掉壳的状态保存 | 壳默认实现 `linkshared.js:2081-2092`；调用点 contentlist.js:46、modelpara.js:35 等 |
| `reScanFlag` | 扫码后、`#autosave_btn` 未激活时判断是否强制走「扫描后保存」 | `(id)`：扫码目标控件 id | 返回**真值**=绕过按钮激活状态强制执行扫描后自动保存（beforeFunction("autoSave") 校验 → `recSave`） | 默认 `return false` `linkshared.js:82-84`；唯一调用点 :92（注释原文「返回true则执行扫描后保存等操作」:79） |
| `linkDMFuncBackImpl` | **附加功能执行返回后**（`contextCall1` 的 `linkDMContextFunBack` 回调，`linkshared.js:1266`）与**前/后置处理返回后**（`ProcessCall` 回调，:931）——**与 linkdatasearch 开窗无关**（开窗回填走 `linkdatasearch_local` 事件 + `autoMatching`） | `(data)`：响应 `r.data`，壳按 `dmCode/dmNum/dmDesc/rowID/Para` 跳转或刷新当前列表（:941-989）；模型重写做扣量/清空/关窗/通知刷新 | 无 | 定义 `linkshared.js:941`（注释「处理后跳转的方法」）；tagprint 链也有（linktagprint.js:261） |
| `repeatTime` | **防重复点击的冷却秒数**（语料误读为轮询定时器，已修正）：`resetRepeatSta` 用 `setTimeout(..., repeatTime秒*1000)` 解锁 | `(id)`：动作元素 id | 返回秒数（默认 1）；元素 `repeatTime` 属性优先于本钩子（`repeatTimeByElement`，:4357-4360） | 默认 `return 1` `linkshared.js:4362-4364`；唯一消费点 `resetRepeatSta` :4349-4356 |
| `contextTap`（FB） | 详情页列表行点击 | `(contextid, linktitle, linkrefresh, linkparafill, cRDs)` | 无；localStorage 暂存 + `showAttachModelPara(...)` 弹补充参数 | TMESPUR01/02/03/06 #10；壳侧同名函数 `linkshared.js:5560` 为内部实现不可重写 |
| `searchContent` | 扫码 `type=="search"`（扫码枪 search 场景） | `()` | 无；**全壳唯一的存在性短路判断**（`searchContent&&searchContent()`），仅 contentlist 页定义（contentlist.js:264） | `linkshared.js:102` |
| `autoResolve` | 扫码 `scan_para` finally、输入联动等多处（7 个调用点） | `(id, r)` | 无；壳默认实现（:3846）可被模型重写 | `linkshared.js:68/1123/1443/2570/2660/3904/3962` |
| `limitTimeAction` | 防重复点击命中时（`ifRepeatSta` 为真） | `(id, ele)` | 无（壳默认返回 ""）；自定义限流提示 | 默认实现 `linkshared.js:4366-4368` |
| `onLinktagprint` | 标签打印按钮**长按**（tap 走 linkquickAction4） | `()` | 无 | 调用点 `contentlist.js:967` |

> 壳内部函数（非钩子，重写无效）：`scanAfterActionImpl`、`scan_impl`、`linkquickAction1~16`（壳分发实现，但其动作 id 会作为 beforeFunction/afterFunction 的 `sta="linkquick"` 实参）、`contextTap`、`resetRepeatSta`。`openZoom`、`linkDMFuncBack`（无 Impl 后缀）在壳源码**不存在**。

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
| 附加功能执行返回回调（linkDMFuncBackImpl 扣量/清空/关窗/通知刷新；经 contextmenulist 附加功能链触发，非 datasearch） | `samples-corpus/TAMPERAPP/TMESPDA13010X#502-公斤领用.xml`（L274-318） |
| 扫码后数据检查 + 自动查询 | `KEEWAYZUP30#5`（corpus，L435-452） |
| 纯 UI 增强（双指缩放，无钩子） | `KEEWAYZUP2010X#703-图片展示.xml`（L92-110） |
| FB 行点击补充参数 | `TMESPUR01#10-采购申请详情.xml`（L339-348） |

## 注意

- 顶层语句即页面初始化脚本（如 `$("#linkok").hide()`），不只是函数定义区。
- 服务端 js 片段的**唯一可靠执行通道是客户端 `load_js`**（`linkshared.js:2292-2306`：先 `$(".linkjavascript").remove()` 再新建 inline script append，插入即执行）；`load_js_ajax`/`append_js`（:2308-2335，newrecord/linkmemo 用）只是把文本 append 到**页面里已静态解析的空 `<script id="linkjavascript">` 节点**——不触发执行，只有其 func 回调（linkInitData）会跑，模型 JS 初始化在这些页面应走 `reloadAfter()` 钩子。`reloadAfter()` 壳默认空实现（:4306），`linkInitData` 末尾统一调用（:4382）。提交参数按 DOM 顺序由 `reParaList`/`jq_para` 收集成 `{0}{1}…`——客户端机制详见 `totallink-app-help/references/h5-guide.md`（§3.3/§3.4）。
- `JavaScript` 字段属 `BRACE_FIELDS`：脚本内字面花括号需 `{{ }}` 转义（经 string.Format 处理）。
- 任务书按钩子选型结果列 JS 清单；验收时人工断言含扫码/校验/刷新行为。
