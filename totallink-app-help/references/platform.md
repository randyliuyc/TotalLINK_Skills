# 平台专题：CSS 定制 / MQTT / SQLite / 推送（以源码核实为准）

> 全部结论经源码逐条核实（排除 unpackage/），行号为编写时快照，引用前需复核。

## 1. CSS 定制样式分布

### 1.1 css/ 目录清单（27 个）

| 文件 | 大小 | 用途 |
|---|---|---|
| mui.min.css（定制版） | 103.75 KB | mui 框架 + **定制合并的 .link* 规则约 144 处** |
| contentlist.css | 10.35 KB | 列表页（含 .link* 定制） |
| menugroup.css / menulist.css / menulist-bf.css | 8.76 / 5.56 / 5.42 KB | 首页/菜单页 |
| link.css | 8.86 KB | 通用定制（**不含 .link 前缀类**，.link*{ 检索 0 匹配） |
| audio.css / login.css / common.css | 7.53 / 5.42 / 5.53 KB | 音频/登录/通用 |
| font-awesome.min.css / icons-extra.css | 31.51 / 2.75 KB | 第三方图标 |
| mui.picker.all.css / mui.picker.min.css / mui.poppicker.css | 6.43 / 4.73 / 1.28 KB | mui 选择器 |
| linkmemo.css / moreapp.css / editapp.css / setting.css | 4.13 / 3 / 2.86 / 5.45 KB | 备忘/全部应用/编辑/设置 |
| attachmodelpara.css / modelpara.css / linkToast.css / picklist.css | 2.04 / 2.12 / 3.01 / 1.76 KB | 参数页/toast/拾取列表 |
| search.css / upload.css / ai.css(空) | 1.81 / 1.38 / 0 KB | 搜索/上传/占位 |

### 1.2 mui.min.css 内 .link* 规则分布

| 行段 | 内容 |
|---|---|
| 14 | .linkselflist |
| 35–70 | .linktexteditdiv 系列（label/empty::before/.tolinkactive） |
| 73–137 | .link-required-boder(73)；颜色系 .link-red/orange/yellow/olive/green/blue/gray/black/white/pink/brown/grey/cyan(76–112)；渐变系 .link-gradualRed/Purple/Mauve/Orange/Green/Blue/Pink/Purplek(115–137) |
| 153 | .linkIcon-loading |
| 160–253 | .linkmultiple/.linkdatasearch/.linkmultipleDiv/Tools/OK/Cancel/Clear 系列 |
| 307–315 | .linkbluetooth、.linkble .linkabscenter |
| 327 | .link-backdrop4（弹框遮罩） |
| 381–412 | .linktextarea、.link-input-list、.linkreadonly |
| 545–558 | .linkhide/.linkcheckbox-multiple,.linkcheckbox-one、.link-submit-content 内 checkbox/radio(555–558) |
| 568–653 | .linkMedia/.linkMediaImages/.linkMediaImage/.linkMediaFile 系列 |
| 661 | .linkflexbox |
| 668–832 | **.linkcard(668)/.linkcard-1(684)/.linkcard-title(710)/.linkcard-2(746)/.linkcard-3(764)/.linkcard-4(785)** |
| 836–844 | .linkcenter(836)/.linkleft(840)/.linkright(844) |
| 855–923 | .link-submit(855)/.link-submit-content(870,879,916-923)/.link-submit-footer(890-913) |
| 1141 | #todoList .linkcard（应用内消息弹框） |
| 1281–1363 | .link_toast 系列（default/success/warning/danger/info/toast_hide/box/message-close） |

**易混淆点**：`.link-picklist2/3`、`.link-backdrop2/3` **不在** mui.min.css——在 `css/picklist.css`（:38/:26/:12-23）；`link-pick-btn` 在 `css/contentlist.css:507,514`；`.link-backdrop` 在 `css/menulist.css:251`；`linkcollapse` 在 css/ 目录 **0 匹配**（js 中 class `linkcollapse-hide` linkshared.js:9420 的样式可能在动态生成或内联处）。

### 1.3 各页面 css 的 .link* 代表 class

- **contentlist.css**：.linkul:63、.linkdealdiv:74、.linkpopobtn:115、.linkchart:248、.link-table/.link-table-default:346/357、.linkPicklistDiv:471、input/button.link-pick-btn:507/514
- **menulist.css**：.link-btn-active:12、.link-theme11:38（左侧主菜单栏）、.link-theme12:85（底部导航栏）、.linktitle:116、.linkcounts:128、.linkselflist:145、.linkCollection:170、.link-backdrop:251、.link-fav:276
- **login.css**：#login.linkdisable:17、.linkhide/.linkshow:66/70、.link-icon:74、.link-label:88、.link-input:110、.linkalldiv:146、.link-theme1:161、.linkabscenter:195、.link-language:209
- **picklist.css**：.linkDialTele.linkabscenter:2、.link-backdrop2,.link-backdrop3:12、.link-picklist3:26、.link-picklist2:38
- **linkToast.css**：.link_toast:62、.link_toast-message-close:74、.linkbutton:114

### 1.4 沉浸式状态栏（纯 JS 方案）

全部在 `js/immersed.js`（1.69 KB），css 中 **0 匹配** safe-area/constant()/env(safe-area-inset)：
- plusready 里取 `plus.navigator.getStatusbarHeight()`（:3-12），UA 正则 `Immersed\/(\d+.?\d*)` 取高度存 `localStorage("immersedHeight")`（:15-23）；
- 依次处理 `#header`/`#linkhead`（paddingTop=immersed、height=44+immersed、背景 #355C7D）、`#content`/`#dcontent`/`#map`（marginTop）、`#contentlist2_2`（paddingTop=44+immersed）（:29-48）。

## 2. MQTT 消息链路

### 2.1 配置对象与填充（linkshared.js）

- 全局 `link_mqtt_ele`（:6071-6080）：`{port:9047, user:memGet("globleUser").toUpperCase(), alive:60, useSSL:false, url:reMqttUrl(), http:globleServer, username:"", password:"", session:false}`；port=WebSocket 端口、alive=KeepAlive 秒、url=`reMqttUrl()`(:6144-6152，从 globleServer 去 scheme 取 host)、session=cleanSession
- 服务端参数填充 `mqttPara(table)`（:6153-6175）：mqttUserName→username、mqttPassword→password、`cleanSession=='True'`→session、keepAlivePeriod→alive、https 用 webSocketPorts 且 useSSL 默认 true/http 用 webSocketPort、qosLevel→qos、`retain=='True'`→retained、**`mqttEnable=='True'`→enable（总开关）**
- 元素属性填充 `reMqttEle(currEle)`（:6105-6141）：读元素 `para/publish/port/url/user/topic/alive/subtopic/pubtopic/id`，缺省回退 memGet("mqtt_port"/"mqtt_url"/"mqtt_alive")；有 para 时 `publish=changeSeftPara(para)`

### 2.2 runMqttService() 流程（:6274-6280 起）

1. `getScript("js/mqtt/MQTT.js")` 动态加载 Paho → `init_mqtt()`（:6182-6204）：`new Paho.Client(url, port, "APP_"+user)` → `_doConnect()`
2. `onConnectionLost`(errorCode!==0) → `handleReconnect()`（:6206-6223）：最多 20 次（maxRetries:6178），指数退避 `min(30000, 1000*2^n)`，超限 `destroyMQTT()`(:6258-6273)
3. `_doConnect()`（:6225-6257）：`_mqttConnecting` 防重复连接；connect 参数含 cleanSession/useSSL/**keepAliveInterval（即心跳）**/timeout:5/userName/password
4. `onConnect()`（:6308-6313）：订阅默认主题 `["LINKTOPIC", "LINKTOPIC/"+user]`；`subTopic()`（:6287-6306）支持数组多主题，qos 取 `link_mqtt_ele.qos||2`

### 2.3 收消息链路

- `onMessageArrived` → `mui.fire(topWebview, "notify", {data: payloadString})`（:6195-6200）→ :1407 `addListener('notify')` → `loadRecentHistory(data)`(:9701)
- 快捷链路：`linkquickAction14(ele,nw)`(:6083) → `listenMQTT()`(:6087-6094) → fire menugroup `menugroup_local {MQTT:true,ele}` → **menugroup.js:386-387 `linkQuickMQTT(event.detail.ele)`**（linkshared.js:6096-6104：有 subtopic → subTopic()，有 publish → sendMess()）；调用入口 linkshared.js:4482

### 2.4 发布

`sendMess(obj)`（:6319-6329）：`new Paho.Message(obj.publish)`，`destinationName=obj.pubtopic`，qos=2，`link_mqtt_client.send()`，成功后 toast。**无独立 publish 函数，统一走 sendMess**。

### 2.5 依赖与启动

- 库：`js/mqtt/MQTT.js`（84.94 KB，Paho.MQTT）；**所有 html 静态引入均被注释**（linkmemo.html:215、modelpara.html:26、contentlist.html:30、attachmodelpara.html:26、newrecord.html:260），运行时由 runMqttService 的 getScript 动态加载
- 启动点：menugroup.js:340-346——登录后 `getDmResult("SYSPARAMS",320)` 拉参数 → mqttPara() → **link_mqtt_ele.enable 为真才 runMqttService()**（menugroup.js:301 直接调用已注释）

## 3. 离线 SQLite

### 3.1 库与连接（linkshared.js）

- 库名 `db_name="totallink"`，路径 `db_path="_doc/totallink.db"`（:7243-7244）
- `openDB()`（:7260-7304）：Promise + `DB_OPEN_LOCK` 互斥（:7256）+ 10 秒超时；已打开（`ifDB` :7247-7254）直接 resolve
- `closeDB()`（:7307-7342）：5 秒超时，未打开/失败也 resolve（不阻塞）

### 3.2 类型映射与建表

`typeMappings`（:7802-7814）完整内容：Boolean/Byte→`INTEGER NOT NULL DEFAULT 0`；Char→`TEXT NOT NULL DEFAULT ''`；DateTime→`DATETIME NOT NULL DEFAULT ''`；Decimal/Double/Single→`REAL NOT NULL DEFAULT 0`；Int16/Int32/Int64→`INTEGER NOT NULL DEFAULT 0`；String→`TEXT NOT NULL DEFAULT ''`

- `createTableFromData(arr, obj, tableName)`（:7817-7850）：按 obj 的 key+类型映射生成列，统一加 `_totalLINK_id_ INTEGER PRIMARY KEY AUTOINCREMENT`（:7826），再逐行 insertData
- `createTableWithData(arr, obj, tableName)`（:7853-7877）：先 drop 再建，拼批量 INSERT，arr 空则只建表

### 3.3 实际使用的表（建表均在 setting.js `reloadOffline()`）

| 表 | 字段 | 读 | 写/删 |
|---|---|---|---|
| **user** | _totalLINK_id_, UserName, psw, url, Email, Tel, token（setting.js:1258） | index.js:178（offline_login） | setting.js:1265 |
| **image** | _totalLINK_id_, name, CodeDesc(MEDIUMEXT,存 base64)（setting.js:1273） | menugroup.js:63-65（ape_img） | setting.js:1285 |
| **icon** | _totalLINK_id_, IMAGE, MENUNO, DMNUM, DMDESC, DMPARA, ECHARTFLAG, DMDESC_1, DMDESC_2, TYPE（setting.js:1317） | menugroup.js:68-71（ape_grid） | setting.js:1333 |
| **item** | 同 icon（setting.js:1313） | menugroup.js:75-77、reHisItem:116-122（MENUNO/DMNUM/IMAGE） | setting.js:1335/1358/1382 |
| **fav** | 同 icon（setting.js:1321） | menugroup.js:80-83、collection.js:33-37 | 写 menugroup.js:200-201；删 menugroup.js:171-172、collection.js:101/136 |
| **html5** | _totalLINK_id_, MENUNO, DMNUM, DMDESC, H5List, js, ParaList, GDs, FunList, DataMineList, ContextMenuList, URLList, NewRecList, H5Edit, H5GridHeader, H5GridDetail（setting.js:1309） | 离线编辑 memGet("H5Edit")（linkshared.js:6367） | setting.js:1408（getH5）、1632 |
| 动态业务表 | 表名 `replaceCodeNum(MENUNO,DMNUM)`，列由服务端 DataStru 决定 | contentlist.js:1829 | setting.js:1640、contentlist.js:1829 |

### 3.4 CRUD 函数（linkshared.js）

- `selectData(tableName, columns, where, selfsql)` :7433-7450——拼 SELECT，传 selfsql 时整条替换
- `insertData(tableName, data)` :7413-7431——对象拼单条 INSERT，值经 `escapeString`（:7890，单引号转义）
- `insertOrUpdateData(tableName, data)` :7564-7606——接受对象或数组，**逐条**：带 `_totalLINK_id_` 则 UPDATE，否则 INSERT
- `insertOrUpdateDataWhere(tableName, data, where)` :7534-7562——按 where 查有无再决定 insert/update
- `insertMultipleData(tableName, dataArray)` :7663-7677——循环 insertData 后 Promise.all
- `deleteData(tableName, where)` :7471-7484；`deleteRecords(tableName, ids)` :7486-7502（按 _totalLINK_id_ IN）
- 另有 updateData:7452、transactionDB:7345、createTable:7398、deleteTable:7651、deleteAllTables:7608

### 3.5 离线登录与存储分工

- `offline_login(nwaiting)`（index.js:159-195）：校验 server/user/pwd → 查 **user 表**（WHERE UserName+url+psw）→ 命中取 `r[0].token` 调 `goonItem(server,user,pwd,{data:token})` 完成登录；未命中提示离线未缓存
- **分工**：SQLite 存结构化/大块数据（轮播图 image、菜单 icon、历史 item、收藏 fav、html5 模板、业务数据表），离线分支依次 selectData image→icon→item→fav（menugroup.js:58-92）；localStorage 存键值：登录态 LinkID/globleServer/globleUser（menugroup.js:332-334）、最近历史 `get_L(user+server+'recentHis')`（menugroup.js:337、setting.js:1345）、H5Edit 模板片段（linkshared.js:6367）、neverTodo 等

## 4. 推送消息

### 4.1 核心函数（linkshared.js）

- `rePushObject(data)`（:6460-6469）：payload 字符串/对象容错解析
- `createPushMsg(content, payload, title, cover)`（:6471-6475）：`ele.local=true` 标记本地消息 → `plus.push.createMessage(content||"totalLINK", JSON.stringify(ele), {cover, title||"totalLINK"})`
- `clickPushMethod(msg)`（:6477-6589）：解析 payload → dmCode/dmNum/dmTitle 写 memSet+全局（:6486-6491）→ 按 `type` 分支：
  - `open` → openFile(:6493)
  - `para` → showPara(:6496)
  - `content` → fire contentlist 的 contentlist_local + showModelData（:6502-6515）
  - `new` → 请求 linkDMData/linkDMDataWithLastParams 后 recNew()（:6517-6558）
  - `edit` → SYSTEMLINKMEMO/`_LKMM` 走 showLinkmemo，否则 showRecEdit（:6560-6572）
  - `attach` → showAttachModelPara(:6574)
  - `echart` → showChartbyPara(:6582)

### 4.2 监听注册（js/menugroup.js:309-328，plusReady 内）

- `"receive"`（:309-323）：APNS/在线消息 → createPushMsg 转本地通知；**payload.local=true 的本地消息不处理**（:317）
- `"click"`（:325-328）：直接 `clickPushMethod(msg)`

### 4.3 与个推/UniPush 对接

- **cid 上报**：登录时 `plus.push.getClientInfo().clientid`（index.js:235）作为 `getuiCID` 参数 POST `/api/LINK/linkUserLogin`（index.js:242-251）
- **别名绑定**：源码中**未检索到** alias 相关调用；其余 cid 相关多为注释代码（index.js:149-155、linkshared.js:1347、setting.js:133/1674）

### 4.4 应用内消息与推送的关系

统一入口 `"notify"` 事件（:1407 addListener）→ `loadRecentHistory(obj)`(:9701-9735) 按 `obj.type` 分发：

| type | 处理 | 行号 |
|---|---|---|
| LINKPUSH | clickPushMethod（已打开）或 linkPushMethod（:9577，转系统通知栏） | :9701-9708 |
| LINKMESSAGE | linkAlertMethod（:9581，页内弹框） | :9709-9716 |
| LINKQUICK | linkQuickMethod（:9608，生成伪元素触发快捷函数） | :9717-9723 |

- **三个来源都 fire "notify"**：MQTT 消息（:6200）、待办轮询 `setLoadNotify()`（:9553-9556，每 180 秒 `LINKWORKFLOW,20` 拉待审批，:9558-9575）、推送
- 弹框 UI：`apeMessageBox`（:9765-9811，#todo + #todoList slider）、`apeMessage`（:9813-9836，linkcard/linkcard-title/linkcard-1 结构）、滑页/关闭 :9426-9476
- 最近消息卡片：`apeRecentCard`（:9645-9671，#notify 内 linkcard-4，LINKPUSH/LINKQUICK 配不同图标）、`findCardAndClear` :9677；经 listenCard→fire menugroup_local {card:true}（:9695-9699）→ 首页 menugroup.js:388-389 渲染
