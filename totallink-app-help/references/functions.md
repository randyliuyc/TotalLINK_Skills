# 核心公共函数清单（js/linkshared.js）

> 行号为编写时快照，引用前需核实。全局变量与 localStorage/memGet key 惯例亦见本文。

## 1. 缓存与状态

| 函数 | 签名/用途 |
|---|---|
| memGet/memSet/memRemove/memClearAll | localStorage + `_memoryCache` 内存缓存双层读写；memClearAll 会向所有 webview 广播清缓存 |
| get_L(key)/set_L(key,val) | JSON.parse(memGet)/memSet(JSON) 封装 |
| ifRepeatSta(id,ele)/resetRepeatSta(ele,oid)/repeatTimeByElement/limitTimeAction | 防重复点击锁表 LINK_REPEAT_STA（详见 linkquick.md §8） |
| ifOffline() | memGet("offline")=="1" 即离线模式 |
| showWaiting(str,id)/closeWaiting(ele) | plus.nativeUI.showWaiting 封装；showW(t) 是页面级简写（contentlist.js） |

## 2. 附加模型/上下文动作（核心链路）

| 函数 | 签名/用途 |
|---|---|
| **DMContextAction** | `DMContextAction(type, id, RDs, func, code, num)`：type=0 → POST `linkDMContextActionInfo`（par.contextMenuNo=id）；type=1 → POST `linkDMConditionAction`（par.action=id）。parajson=`{loginID, par:{dm:{dmCode: code\|\|globleDmCode, dmNum: num\|\|globleDmNum}, contextMenuNo/action, RDs}}`。返回 dataType=="modelActionInfo" 时按 a.type：1→执行 func+长 toast；2→confirm 后执行；3→condition 为真才执行否则 alert；空→直接 func()。注意 type=1 校验常传 code=`dmCode+dmNum+'X'`、num=contextid（附加模型标识） |
| **contextCall** | 上下文菜单总入口：缓存 c* 全局变量（clinkID/cGlobleServer/cDmCode/cDmNum/cContextID/cRDs/cLinkRefresh）；linkLocation=1/2 时先 plus.geolocation（baidu, geocode:true）→ contextCallWithGeoInf，否则直接 contextCall1 |
| **contextCall1** | 先 `DMContextAction(1,"6",RDs,...,DmCode+DmNum+'X',contextid)` 附加模型校验；通过后 POST `linkDMContextFunBack`（parajson: `{loginID, par:{dm, contextMenuNo: contextid, RDs}}`）→ toast message → linkDMFuncBackImpl(r.data) |
| **linkDMFuncBackImpl** | 执行后跳转：返回模型==当前或为空 → showModelData(null,rowID)；否则 fire `contentlist_local` 事件给 contentlist webview 保存返回信息，memSet globleDmCode/Num/Title，设置 webview.modelParams/rowID 后 showModelData |
| **attachURLFunction** | URL 型附加功能：POST `linkDMAttachURLFunction` → openURL(r.data)；先 memSet globleDmCode/Num 防错乱 |
| **contextTap** | linkparafill=1 → 打开附加模型参数页（showAttachModelPara，AttachDmCode=DmCode+DmNum+'X'）；否则 linkpopopvercheck 通过后 contextCall |
| **pre_post / ProcessCall** | 预/后处理：processType=="linkpreprocess"→POST `linkDMPreProcessByGridDataBack`；"linkpostprocess"→`linkDMPostProcessByGridDataBack`；parajson=`{loginID, par:{dm:{dmCode,dmNum,Para:reParaList()}, GDs}}`；成功 toast message → linkDMFuncBackImpl |
| currRDs(ele) | 取当前行数据：`JSON.parse($(ele).attr("para"))`，失败返回 [] |

## 3. 网络请求

| 函数 | 签名/用途 |
|---|---|
| linkAjax(para, url, opt) | Promise 封装 ajax_promise_plus，catch 时 alert + closeWaiting + rethrow |
| ajaxSetting(id,def) | 有 def 返回 def（如 `{type:"GET"}`、`{timeout:120000}`），否则 "" |
| getMain / getDmData / getDmResult | 分别对应 linkDMContextFunBack（单行）/ linkDMGridDataSubmit（多行+scriptType+GDs）/ linkDMDatasetResult |
| loadScriptString(str) | eval 执行服务端返回的 option 脚本字符串 |

## 4. 页面跳转与事件

| 函数/机制 | 用途 |
|---|---|
| mui.openWindow + extras | 多数跳转用 openWindow + extras 传态；extras 常见 currRowData/linkrefresh/attachNum 等 |
| mui.fire(target,'contentlist_local'/'menulist_local'/...) | webview 事件：beforeback/返回时通知上级刷新 |
| backArr（返回栈） | `var backArr=[]; BACK_ARR_MAX=20; safeBackArrPush(item)` 溢出 shift；元素结构 `{type:"dataMine"|"back"|..., id, uuid, dmChartFlag, paraconfirm, code, num, title, para, cRDs}`；contentlist.js beforeback 消费 |
| menutap / showMenuGroup | 菜单跳转家族：memSet globleDmCode/Num/Title/ChartFlag → 按 dmParaFlag/dmChartFlag 分流 showPara/showChartbyPara/showModelData |

## 5. 多语言

- rLang(key)：按 memGet('link_language')\|\|'zh' 选语言包，`.` 分路径取值，缺失返回 key 本身
- linkLanguage()：扫描 `[link-lang]` 元素，属性值 `位置:键`（text/html/val/其它=attr）批量翻译
- 语言包懒加载：ajax_json(url) 同步 getJSON 读 libs/lang/xx.json 缓存到全局对象

## 6. 其它常用

| 函数 | 用途 |
|---|---|
| getAdrLoc / getLocationStr | 定位（baidu, geocode, timeout 5000）→ cb(getLocationStr(p))，失败 cb("")；生成 `{Key:"LINKLOCATION",Type:"String",Value:地址文本}` 或 LINKLOCATIONJSON |
| openCam | actionSheet"拍照/相册"选择后进入拍照/选图流程（linkimage 入口） |
| dataMine / showDataMine | 数据挖掘：POST linkDMDataMine，par=`{dmWithParams:{dmCode,dmNum,Para}, dataMineNum, RDs}` |
| scan_para / scan_impl / deal_json | 扫码入口：内容为 `{...}` 直接赋值；`#xxx#` 走 linkDMDatasetResult 查询 |
| currRDsLineNo / recheckid | 当前行号 / 多行勾选取值 |
| linkpopopvercheck(RDsLineNo) | 长按菜单执行前的过滤校验 |
| reParaList() | 收集界面参数（模型 Para 列表） |
| rePrintPara(ele) | 打印参数（取勾选行 RowData） |
