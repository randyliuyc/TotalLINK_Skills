# 自定义属性用法总结（js/linkshared.js 等，以源码检索为准）

> 检索范围：linkshared.js 全部 220+ 处 `.attr()`/`getAttribute`/属性选择器，并经 contentlist.js/newrecord.js/menugroup.js/collection.js 等页面 js 交叉印证。行号为编写时快照，引用前需复核。
> 检索确认**不存在**的属性：`link-loadding`、`linktag`、`scriptType`、`showtext`、`showvalue`、`rowid`、`version`、`scan-type`（相近的真实属性：`loaded`、`row-id`、`echartflag`、`data-value`）。

## A. link- 前缀系列（行为控制）

| 属性 | 位置 | 取值/格式 | 作用 |
|---|---|---|---|
| linkquick | :4429、:4513 | '1'~'16' | 快捷动作分发号 → linkquickAction1~16 |
| linkrefresh | :5087、:5372；contentlist.js:993 | 标志串 | 扫描/拍照/动作回填后是否刷新列表 |
| linkparafill | :5088 | 标志串 | 拍照/扫描结果是否回填为参数（contextTap linkparafill=1 → 附加参数页） |
| linktitle | :5089、:5140 | 文本 | 功能标题（→ memSet("AttachDmTitle")） |
| linkimage | :5090 | '1'/'2' | 相机/百度识别类型（openCam 的 type）；注意 `.linkimage` 同时是图片预览容器 **class**（:4273-4297） |
| linklocation | :4468、:4880、:4896、:4947、:4961、:5105 | '0'/'1'/'2' | 携带地理位置：0=不需要/1=文字/2=JSON；memSet("linkLocation")；**支持 closest("[linklocation]") 祖先继承**（缺省兜底 "0"） |
| link-text / link-value | :1852、:1930 | 字段名 | 控件 key/val 的绑定字段（优先于元素 id） |
| link-lang | :3412 | `xx:yy` 冒号分隔 | 多语言标记（linkLanguage() 批量翻译） |
| linkcopy | contentlist.js:1370 | 文本 | 长按复制时覆盖复制内容 |

## B. 模型标识与参数系列

| 属性 | 位置 | 取值/格式 | 作用 |
|---|---|---|---|
| code / num | :4514/:4515 等 | 串 | 模型代码/编号；code 缺省回退全局 globleDmCode |
| para | :4516 等 | JSON 或参数串 | 提交/挖掘参数；行数据元素上 para 存整行 JSON（currRDs 解析）；亦复用作 MQTT/地图地址/展示列表参数 |
| api | :4517 | 1~7 / 'function' | linkQuickAjax1~7 接口选择 |
| script | :4520、:8718 | 脚本号 | 服务端脚本类型（deleteScript 缺省 3） |
| rowdata / row-id | :4499、:9273 / :8761 | 行号数字 | 当前行号（rowdata 支持继承，isNaN 判断后赋 currRDsLineNo） |
| formula | :4519、:6110 | 公式串 | 计算公式，缺省 "1"（求和） |
| data-id | :1026 等 | id 串 | 控件/记录的持久标识（id 的影子属性；上传后刷新媒体列表的容器 id） |
| target-id | :1433、:3886、:4152 | id | 联动赋值目标控件 |
| props | :1437-1438 | 字段映射 | 自定义返回列与控件映射 |
| not-para | :1917-1918 | 存在即真 | 元素**及其祖先**不参与参数收集 |
| expression | :4152 | 表达式 | 选择列表过滤/计算 |
| action | :4503-4508 | 键名 | 查 submitAction[action] 动作数组（自定义弹框） |
| submit-id | :1046 选择器 | — | 标记提交控件 |
| paradm | :1055、:4008 | 参数串 | 联动数据挖掘参数 |
| dmCode/dmNum/dmTitle/dmParaFlag/dmChartFlag | collection.js:75-79、:2728 | 串/1 | 菜单项挖掘模型五元组 |
| echartflag | :5163；menulist-bf.js:155/297 | 1 | 直接挖掘到图表 |
| data | :2371 等 | 任意串 | 通用暂存值 |

## C. 执行控制系列（提交管线，reAllPara 收集）

| 属性 | 位置 | 取值/格式 | 作用 |
|---|---|---|---|
| confirm | :4406 | 提示文本 | 提交前确认框（mui.confirm） |
| prompt | :4407 | 提示文本 | 提交前输入提示 |
| before / beforeTip | :4521/:4522 | 表达式/文本 | 提交前置校验表达式与失败提示（return true 阻止） |
| stop / stopTip | :4523/:4524 | 表达式/文本 | 终止后续接口的条件与提示 |
| express | :4525、:4534 | 表达式 | 自定义执行表达式（api='function' 时） |
| tip / alert | :4526/:4527 | 文本 | 执行完单步 toast / 弹框提示 |
| prefix / suffix | :4528/:4529 | 文本 | 提示前缀/后缀 |
| js | :4546 | JS 代码串 | linkquickAction16 eval 执行 |
| repeatTime | :4321 | 秒数 | 元素级防重复间隔 |
| paraconfirm | :5161、:5178 | "True" | 挖掘前先弹参数录入 |
| repeatFile / repeatTip | :8833/:8835 | 键/文本 | 文件重复校验与提示 |
| deleteCode/deleteNum/deletePara/deleteScript | :8715-8718 | 同 code/num/para/script | 删除动作参数覆盖 |
| reload | :1060、:3935、:10400 | 存在即真 | 每次重新生成数据 |
| not-reset | :1608/:1615 | 存在即真 | 重置时跳过 |
| clearable | :8999 | 存在即真 | 输入框可一键清空 |
| autoPath / prefixPath | :9136/:9135 | 存在即真/前缀 | 文件路径自动补全（prefixPath 优先，autoPath 后执行） |
| append / save | :10407/:10408 | 存在即真 | link-append 面板追加区/保留区 |
| separator | :3885 | 分隔符 | 多选值分隔符（缺省 ","） |
| group | :4147 | 组名 | 选择列表分组 |
| index | :3866、:8705 | 数字 | 选项/图片序号 |
| loaded | :10401/:10427 | '1' | 面板懒加载标记 |

## D. 扫描/解析/自动带出

| 属性 | 位置 | 作用 |
|---|---|---|
| resolve | :3810 | 存在即真：输入启用自动解析（keyup/扫码 → autoResolve） |
| no-scan | :3813 | 存在即真：禁止触发解析 |
| no-keyup | :3828 | 存在即真：取消 keyup 监听解析 |
| automatch | :3811、:4178-4179 | JSON `{目标id:字段}`：自动带出（详见 methods.md §1） |
| data-value | :2621-2623 | 选项点选后作为值触发 autoResolve |
| default-value / default-text | :1627/:8548 | 重置时恢复默认 |
| autosave_btn / autoadd_btn | :4353-4365 | 注意：这是 **localStorage 开关**（'1'/'0'），不是 HTML 属性 |

## E. 数据行/行数据

| 属性 | 位置 | 作用 |
|---|---|---|
| para（JSON） | :5208 等 | 行级数据随 code/num 提交 |
| btnid | :5086、:5139、:5158 | 功能真实编号（`getAttribute("btnid")||id`），上下文菜单/URL/挖掘功能 |
| id（closest 继承） | :4498 等 | 行内控件无 id 时向最近 [id] 祖先取 |
| value | 多处读+写 | 控件选中值的持久化载体（val() 之外第二份） |
| text-value | :3963 | `key:val` 选择列表字段名标识 |
| show-id | :8314 | 展示列表目标元素 id |
| fileName / subTitle | :9010/:9011 | 上传控件显示文件名/副标题 |
| rec-src / sign-src | :2228；linkmemo/newrecord.js | 录音地址 / 签名 dataURL |
| uuid | :9255 等 | 临时记录唯一标识（时间戳） |

## F. 硬件/语音/多语言/菜单

| 属性 | 位置 | 作用 |
|---|---|---|
| token/text/spd/pit/per | :4535-4539 | TTS 语音参数（linkquick=15） |
| service | :5603 | 蓝牙服务标识 |
| pname / extra | :5277/:5279 | 第三方 APP 包名 / JSON 附加参数（linkquick=11） |
| write / notify | :5888/:5889 | 蓝牙写/通知特征标记 |
| url/user/topic/publish/port/pubtopic/cleanSession/retain/mqttEnable | :6108-6172 | MQTT 配置（cleanSession/retain/mqttEnable 用 'True' 判断） |
| address | :5079 | 地图默认地址（\|\|attr("para")） |
| on / off / other | :1860-1867 | 开关控件两态值与附加值 |
| lang / theme / key | index.js、setting.js | 语言码 / 主题 / 设置存储键 |
| totallink | menugroup.js:120 等 | 菜单 _totalLINK_id_（收藏/删除定位） |
| menutitle / menugroup / menuItem / menuItemSeq | menulist.js:276/:353 | 服务端菜单标题/分组/父级序号 |
| dmCode / dmNum | drag_ud.js:120-121 | 拖拽排序项的模型标识 |
| p1 / p2 / img | collection.js:80-82 | 菜单副标题两行与图片 |
| cid / sid | ios/print.js:353-354 | 蓝牙打印机设备/服务 id |
| one | :4152（class 用法） | 单选标记 |
| time / date | :3768、:9688 | 元素时间标记 |
| single | contentlist.js:1393 | 单条数据操作标记 |
| h | :9413-9414 | 折叠动画高度缓存（内部） |
| dataType | :1860 | 开关控件类型标识（配 on/off/other） |

## G. 规律归纳

1. **命名规律**
   - `link-*`（linkquick/linkrefresh/linkparafill/linktitle/linkimage/linklocation/link-text/link-value/link-lang/linkcopy）：平台自定义**行为控制**前缀；
   - `dmCode/dmNum/dmTitle/dmParaFlag/dmChartFlag/echartflag`：数据挖掘模型五元组（服务端返回字段 MENUNO/DMNUM/DMDESC/DMPARA/ECHARTFLAG 的小写化）；
   - `deleteCode/deleteNum/deletePara/deleteScript`：删除动作对提交参数的覆盖；
   - `no-*/not-*`（no-scan、no-keyup、not-para、not-reset）：否定式存在性开关；
   - 无前缀小写动词（confirm/before/stop/express/alert/tip/prefix/suffix/js）：提交管线（reAllPara）执行控制；
   - `data-*`：DOM 暂存与动态渲染行数据。

2. **属性继承（本元素没有则向最近祖先取）**：统一模式 `$(ele).attr(X) || $(ele).closest("[X]").attr(X)`：
   - `[id]`：:1026、:4307、:4313、:4498、:5292、:6890；
   - `[linklocation]`：:4468、:4880、:4896、:4947、:4961（缺省兜底 "0"）；
   - `[rowdata]`：:4499（`e.is("[rowdata]")?(e.attr("rowdata")||closest([id]).attr("id")):false`）；
   - 祖先判断：:1918 `ele.parents().is("[not-para],.linkcheckbox-multiple,.linkcheckbox-one")`。

3. **通用读取集合 reAllPara（:4496-4531）**：批量收集 `id(4512)、linkquick(4513)、code(4514)、num(4515)、para(4516)、api(4517)、rowdata(4518，含继承)、formula(4519)、script(4520)、before(4521)、beforeTip(4522)、stop(4523)、stopTip(4524)、express(4525)、tip(4526)、alert(4527)、prefix(4528)、suffix(4529)`；入口先 `closest("[id]").attr("id")`（:4498）与 `action`→`submitAction[action]`（:4503-4508）。

4. **大小写/布尔惯例**
   - 存在性布尔（无值即 true），全部用 `is("[x]")` 判断：`reload/notify/clearable/autoPath/append/save/no-scan/no-keyup/not-para/not-reset/resolve/automatch`；
   - Pascal 惯例：`paraconfirm=="True"`（:5178、:5261）、`cleanSession/retain/mqttEnable=='True'`（:6161-6172）、条件表达式 `"True"||"1"||1`（:5350）；
   - 字符串枚举：`linklocation`/`linkimage` 用 `'0'/'1'/'2'`（:5120、:5110）；`autoadd_btn/autosave_btn` 用 `'1'/'0'`（:4360-4363，注意是 **localStorage 开关**而非 HTML 属性）；`dmParaFlag==1||"true"`（:2728）；
   - 服务端返回布尔统一小写 `'true'/'false'`（:2939、:3166 等）。

5. **服务端动态渲染容器与属性**：FunList/ContextMenuList/URLList/DataMineList 不是函数名，对应入口是 linkquickAction8/9/10（:5083、:5137、:5154，注释即 contextmenulist/linkurllist/linkcontextdatamine）。动态 li 的属性由各页面 js 拼接：
   - menugroup.js:470、:486 与 search.js:321：li 上写 `data-code/data-num/data-title/data-para/data-chart/data-p1/data-p2/data-img`；
   - menulist-bf.js:155（写 `echartflag`）与 :297（读）；:250-251 读 `menutitle/menugroup`；
   - collection.js:60 拼接 `dmTitle/dmParaFlag/dmChartFlag`；
   - menulist.js:353-354 读父级 `menuItem/menuItemSeq`；
   - 读取侧用 `data-code='..'][data-num='..'` 选择器回写（menugroup.js:120、editApp.js:295）。
