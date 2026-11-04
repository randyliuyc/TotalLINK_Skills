# 模型 H5 编写指南（动态渲染机制与编写规范）

> **核心概念：模型界面不是静态页面**。contentlist/modelpara/attachmodelpara/newrecord/linkmemo 五个界面的 HTML 都由服务端返回片段、客户端 `innerHTML`/`append` 动态注入。回答"怎么写模型 H5"时以本文件 + classes-ids.md + attributes.md 为准。行号为编写时快照。

## 1. 五个界面的动态渲染链路

### 1.1 contentlist（列表界面）

在线主链路（`contentlist.js:451-502` `loadModelDataImpl`，接口 `linkDMData`/`linkDMDataWithLastParams`，`scriptType:101`）：

| 服务端字段 | 填充目标 | 代码 |
|---|---|---|
| `r.data.Data` | `#list.innerHTML`（**列表整段 H5**） | :461-463 |
| `r.data.ParaList` | `#para-area-content` append | :465 |
| `r.data.GDs` / `r.data.DataStru` | 行数据缓存（currRDs 用） | :471-472 |
| `r.data.FunList` | `#linkfunlist.innerHTML` | :476 |
| `r.data.DataMineList` | `#linkcontextdatamine.innerHTML` | :480 |
| `r.data.ContextMenuList` | `#contextmenulist.innerHTML` | :484 |
| `r.data.URLList` | `#linkurllist.innerHTML` | :487 |
| `r.data.NewRecList` | memSet("dmNewRecList")（新增页模板） | :492,499 |
| `r.data.js` | `load_js()`（模型 JS） | :494-495 |

- 顶部参数区独立加载：`linkDMH5ParaListJS`（:233）→ `#paralist`/`#para-area-content` append **`r.data.content`（注意小写）**（:240-241）→ `load_js(r.data.js)`（:243）→ `mui('.mui-input-row input').input()`（:246）
- 翻页：`linkDMH5BatchDataListWithGDs`（:833）→ `#list.innerHTML = r.data.DataList`（:854）→ `linkInitData()`；触发 `#list #moredata` 委托（:1216-1222）
- 空列表：`isSuccess != 'true'` → toast `rLang('model.null')`（:426）；`#list` 初始为骨架屏（contentlist.html:168-230）
- 离线：模板机制见 §2.1；缓存于 sqlite `html5` 表（:1716,1813）

### 1.2 modelpara（参数界面）

- 接口 `linkDMH5ParaListJS`（modelpara.js:74）→ `modelParaImpl`（:177-197）：`#paralist.innerHTML = r.content`（:184）→ `#linkul` append_picklist（:186）→ `init_local_pl()` → `load_js(r.js)`（:189）→ `linkInitData()`（:190）→ `mui('.mui-input-row input').input()`（:192）→ 非 notFocus 时 showSoftInput("linkinput")
- 重置 `#linkreset` → `clear_input("paralist")`（:137-140）；离线从 sqlite html5 表取 `ParaList+js`（:157-175）

### 1.3 attachmodelpara（附加参数界面）

- 数据来源：memGet AttachDmCode/Num/Title + extras attachNum（attachmodelpara.js:67-76）
- 接口 `linkDMH5AttachParaListJS`（:82），参数传**当前行 RDs**（:88-98，服务端可按行生成界面）
- 渲染：`#attachparalist.innerHTML = r.data.content`（:125-127）→ append_picklist → load_js → linkInitData → mui input 重初始化（:129-135）
- 保存：`valueList().concat(cRDs)` 后 `contextCall(...)`（:110-115）

### 1.4 newrecord（新增/编辑界面）

- 新增：`editlist = memGet("dmNewRecList")`（= 列表页存的 `r.data.NewRecList`），`dataSumitScriptType=1`（:101-103）；编辑：`memGet("dmEditList")` + `dataSumitScriptType=2`（:110-112）
- 填充：`#linkeditlist.innerHTML = editlist + "<div></div>"`（:128-137，**结尾追加空 div 是历史修复**，防 linkreadonly 格式错位）→ `load_js_ajax(linkDMH5ParaListJS)` → `linkInitData()`
- 编辑模式：`editCurrRowAsync`（:139-147）实现在 linkshared.js:6347-6384——在线 `linkDMEditList`（带 RDs），离线用 `H5Edit` 模板 `replaceTextsAndTranslate(template, arr2obj(cRDs))`，同样 `+ "<div></div>"` 填充
- 之后统一 `dealsignevent()`/`dealServerEvent()`（:149-151）；保存 `recSave(..., dataSumitScriptType)`

### 1.5 linkmemo（多功能界面）

- 与 newrecord 几乎同构，但直接 `localStorage.getItem("dmNewRecList"/"dmEditList")` 取模板（:89/:97）
- 独有：jSignature 签名、录音、上传 `/ashx/upload.ashx`、LINKSIG/LINKREC 传值（:152-161）
- 容器同为 `#linkeditlist`（linkmemo.html:154）

## 2. 服务端片段处理与客户端动态模板

### 2.1 离线模板机制（服务端"模板型 H5"的标准写法）

- `re_h5_id`（linkshared.js:8182-8185）：`id="#"` 占位符按行号改写为 `id='行号'`——**列表行模板的 id 一律写 `#`，不可写死重复 id**
- `replaceTextsAndTranslate`（:8223-8240）：正则 `(#(\w+)#)|lang:{(.*?)}`——`#字段#` 从行数据池取值，`lang:{zh:中文,en:English}` 按当前语言翻译
- 离线列表组装（contentlist.js:360-378 `ape_list_data`）：每行用 `H5GridDetail`（或 `H5List`）做模板替换后拼接，`H5GridHeader` 包裹全部行（占位符 `{LINKTABLEROWS}`）

### 2.2 服务端片段注入方式

- **无 sanitize、无 script 摘除、无 style 过滤**：直接 innerHTML/append；服务端 js 片段单独走 `load_js`
- 服务端 css 动态注入：`addCSS(服务端 + "/Files/index.css")`（linkshared.js:3623-3631；attachmodelpara.js:54、linkmemo.js:66）

### 2.3 客户端拼接模板（H5 可参考的框架惯用结构）

- 加载更多/结束行（contentlist.js:312-317）：`<li id='moredata' nextbatch='..' class='mui-table-view-cell linkendline'><a>..</a></li>` / `<div id='endofdata' class='linkendline'>n/n</div>`
- 筛选弹层（linkshared.js:2389-2396）：`<div data='..' class='linkdealdiv'><p>..</p><select>..</select></div>`
- 宫格 li（menugroup.js:464-476）：`<li data-code data-num data-title data-para data-chart class='mui-table-view-cell mui-media mui-col-xs-3'><a><div><img/><div class='mui-media-body'>..</div></div></a></li>`
- 多选弹层（linkshared.js:3947-3988）：`<div class='linkmultipleDiv'><div class='mui-card linkabscenter'>..`，选项行 `<div class='mui-input-row mui-checkbox'><label>..</label><input type='checkbox' value=..></div>`
- 签名区（newrecord.js:686-700）/附件卡片（:658-667）：`#linksignarea`、`<div class='mui-card-header mui-card-media linkfile' filename=.. data-src=..>`

## 3. 编写规范（模型 H5 怎么写）

### 3.1 para 属性（行数据）

- 行元素 `para` 属性 = **JSON 字符串**（`[{Key,Type,Value},...]` 行数据数组）；`currRDs(ele)`（linkshared.js:4906-4919）`JSON.parse` 失败返回 `[]`（容错点）
- contentlist.js 另有同名 currRDs（:626-647）：离线取 `DATALIST[行号]`、在线取 `dmGDs[行号].RowData`
- 行号即元素 id（由 `re_h5_id` 改写），用于 currRDsLineNo 定位与 scroll_record_id 回位

### 3.2 控件值绑定（getValue 口径，linkshared.js:1849-1877）

- 字段名优先级：`link-text` > `link-value` > 元素 `id`
- 取值方式：`[link-text]`/div → `text()`；`[link-value]`、`.linkcheckbox-*`、`.linkpicker`、`.linkdate`、`.linkdatasearch`、`.linkmultiple` → `attr("value")`；普通 input/textarea/select → `val()`；`.linkswitch` → on/off 属性或 "1"/"0"；checkbox → true/false；再经 `reDataByType`（:6386-6413）按 dataType 转型

### 3.3 提交链路（reParaList 顺序参数）

- 收集选择器 `jq_para`（:1878-1914）：`#content .mui-input-group` 内 input/button/textarea/select、[link-value]/[link-text]、.linkcheckbox-*、.linkpicker、.linkdate、.linkswitch、.linktexteditdiv>div、.linkmultiple、.linkdatasearch，以及 `.link-submit-content` 内同款（:1899-1912）
- `reParaList`（:3849-3861）按 **DOM 顺序** push → 顺序参数 `{0}{1}{2}…`（服务端模型按位置取参）
- 跳过规则 `filterPara`（:1916-1921）：`[not-para]`、`.linkUploadImage`、`.linkUploadFile` 自身，及位于 `[not-para]`/`.linkcheckbox-*` 内的元素
- `valueList`（:1923-1953）生成 key-value 对象，自动附加 **LINKSIG（签名）/LINKREC（录音）/LOCATION（定位）** 三个特殊字段

### 3.4 服务端下发 JS（模型 JS 通道）

- **`load_js(src)`（:2255-2269，可靠通道）**：先 `$(".linkjavascript").remove()` 再 append 新 `<script class="linkjavascript">`，插入即执行；contentlist/modelpara/attachmodelpara 用
- `load_js_ajax`（:2271-2290，newrecord/linkmemo 用）：把 r.data.js append 进预留的 `<script id="linkjavascript">` 空占位——**按标准 DOM 行为对已解析 script 追加文本不会重新执行**，模型 JS 初始化应走 `load_js` 通道或依赖 `reloadAfter()` 钩子
- 填充后统一初始化 `linkInitData`（:4333-4348）：键盘监听、图片预览、mui input/switch/numbox/slider 重初始化、initTextarea/initMediaContainer/initCollapseMethod、**`reloadAfter()`（模型自定义钩子，写模型 JS 时在此做初始化）**

### 3.5 多语言

- 静态元素：`link-lang="位置:键"`（如 `text:model.reset`、`placeholder:model.input`），linkLanguage()（:3409-3436）按 text/html/val/value/其它属性 四种位置写入
- 服务端 H5 片段内：直接写 `lang:{zh:中文,en:English}` 或 `#字段#`（渲染时替换，见 §2.1）

### 3.6 样式

- 颜色/渐变 class：`link-red` 系（mui.min.css:76-112）、`link-gradualRed` 系（:115-137）
- 布局用 mui 体系：mui-table-view-cell、mui-input-row、mui-input-group、mui-media mui-col-xs-3、mui-card 等
- 业务 class：linkendline、linkdealdiv、linkmultipleDiv、linkcheck、linkUploadImage/File、linkreadonly 等（详见 classes-ids.md）

## 4. 注意事项（写 H5 前必读）

1. **动态元素事件靠 document 委托**：模型 H5 里的元素交互应使用框架已有委托（linkquick/[resolve]/控件 class），自定义行为在模型 JS 里用 `$(document).on("tap","选择器",…)`，**不要对动态元素直接 bind**
2. **id 唯一性**：列表行模板 id 用 `#` 占位由客户端改写；不要写死重复 id
3. **mui 控件初始化时机**：innerHTML 之后必须重初始化（`mui('.mui-input-row input').input()` 或 linkInitData）——框架已在各渲染函数末尾统一处理，模型 JS 无需重复
4. **重置行为**：clear_input（:1603-1623）清空 textarea/input/button/select（排除 [type=hidden]、[not-reset]），回填 [default-value]/[default-text]——不想被清空的元素加 `not-reset` 属性
5. **提交取值范围**：只有 jq_para 选择器命中的元素会进入 `{0}{1}…` 参数；需要作为参数的控件放 `.mui-input-group` 或 `.link-submit-content` 内，并配置正确的字段名属性

## 5. 样式表引入顺序与接口字段速查

| 页面 | head 引入顺序 |
|---|---|
| contentlist | mui.min.css → icons-extra.css → mui.picker.all.css → contentlist.css → picklist.css → link.css |
| modelpara | mui.min.css → icons-extra → mui.picker.all → modelpara.css → picklist.css → link.css |
| attachmodelpara | mui.min.css → icons-extra → mui.picker.all → attachmodelpara.css → picklist.css → link.css |
| newrecord / linkmemo | mui.min.css → icons-extra → linkmemo.css → mui.picker.all → audio.css → link.css |

规律：**mui.min.css 永远第一，页面私有 css 居中，link.css 最后（覆盖优先）**；运行期动态追加服务端 `Files/index.css`。

接口字段速查：
- 列表：`r.data.Data`（整段 H5）/ `ParaList`/`FunList`/`DataMineList`/`ContextMenuList`/`URLList`/`NewRecList`/`GDs`/`DataStru`/`js`
- 参数/编辑：`linkDMH5ParaListJS` → `r.data.content` + `r.data.js`
- 附加参数：`linkDMH5AttachParaListJS` → `r.data.content` + `r.data.js`
- 编辑列表：`linkDMEditList`（在线）或 `H5Edit` 模板（离线）
- 批次：`linkDMH5BatchDataListWithGDs` → `r.data.DataList` + `r.data.GDs`
