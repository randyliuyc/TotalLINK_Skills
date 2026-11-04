# TotalLINK 项目整体结构

> 来源：项目源码调研（`/Users/link2.0/app`）。`unpackage/`、`static/`、`other/` 为构建产物/静态页，非分析重点。行号为编写时快照，引用前需核实。

## 1. manifest.json 要点

- **appid**：`H5B39CAF9`，应用名 **TotalLINK**，版本 2.2.8 / code 208，launch_path `index.html`
- 开发者：Shanghai Multisoft Software Co., Ltd. / linkbi.cn
- permissions：Accelerometer、Audio、**Bluetooth**、Cache、Camera、Device、Downloader、File、Gallery、**Geolocation**、Orientation、Storage、Uploader、XMLHttpRequest、**Barcode（扫码）**、Maps、Speech、Webview、NativeUI、Push、VideoPlayer、Record、**SQLite（离线库）** 等
- plus：iOS WKWebview 内核、沉浸式状态栏；distribute.plugins 含 unipush、baidu speech（appid 16100802）、geolocation(system)；Android schemes `totallink`、targetSdkVersion 29；iOS plistcmds 解除 ATS 限制
- ⚠️ `dependencies.pages` 为**陈旧配置**（旧文件名），页面清单以下面实际文件为准

## 2. 页面清单（根目录 html）

| 页面 | 用途 |
|---|---|
| index.html | **登录页/入口**：服务器地址+账号+密码+自动登录；首次启动弹服务协议/隐私；语言切换；离线模式入口（js/index.js login 事件、offline_login） |
| contentlist.html | **模型数据内容列表（核心业务页）**：渲染模型数据、行内 linkquick 快捷按钮、数据挖掘跳转 |
| menulist.html | **功能选择页**（菜单列表/目录抽屉），进入模型列表（js/menulist.js menugroupLoad） |
| menugroup.html | **首页（九宫格应用组）**：模型分组宫格、下拉刷新、双击退出；离线走 SQLite（js/menugroup.js） |
| modelpara.html | **模型参数录入页**：调 linkDMH5ParaListJS 取参数列表（js/modelpara.js） |
| attachmodelpara.html | **附加模型参数补充页**（contextTap linkparafill=1 时打开；extras: currRowData/linkrefresh/attachNum） |
| linkchart.html | **ECharts 图表页**：按 showChartType 0/1/2 三种方式加载（js/linkchart.js） |
| linktagprint.html | **标签打印页**（Android 蓝牙），长按打印入口打开 |
| linkmemo.html | **备忘/附件选择页**（LINKMEMO 模型专用，含文件/签名/录音） |
| collection.html | **收藏页**（离线读 SQLite fav 表，js/collection.js） |
| documents.html | **帮助文档页**（外链列表） |
| editApp.html | **应用编辑页**：常用模型管理/排序（_LINKSYS_ 模型 + sortable 拖动） |
| forget.html / reg.html | 找回密码页 / 设备注册页 |
| fwxy.html / yszc.html | 服务协议 / 隐私政策静态页 |
| ai.html | AI 助手页：iframe 加载 localStorage `aiHelp` 的 URL |
| linkmap.html | 地图页（百度地图 BMap 展示 globleAdress 位置） |
| linkdatasearch.html | 数据搜索/选择页 |
| linkimagesee.html | 图片查看页 |
| linkbluetooth.html | BLE 蓝牙标签打印页（onLinkBluetooth extras.tagprint） |
| newrecord.html | **添加/编辑记录页**：录音、签名、文件上传；dataSubmitScriptType 区分增改（js/newrecord.js） |
| setting.html | **个人中心/设置页**：版本检查 /api/LINK/linkUserByToken、清缓存、语言、消息（js/setting.js） |
| linkdatasearch / uploadimage / update | 搜索页 / 拍照相册上传 / 更新页 |

## 3. js/ 目录职责

| 文件 | 职责 |
|---|---|
| **js/linkshared.js（314KB+，核心公共库）** | 内存缓存 memGet/memSet；扫码 scan_para/scan_impl/deal_json；页面跳转 show* 系列；分享 shareAction；**contextCall/attachURLFunction/processCall/DMContextAction**；地理位置；linkAjax/ajaxSetting；rLang 多语言；getMain/getDmData/getDmResult；before/after 钩子+防重复点击；**linkquick 全套**；currRDs；urlFunctionTap/dataMine/showDataMine；openCam/contextTap；BLE；ifOffline；showWaiting/closeWaiting |
| js/contentlist.js（55KB） | 数据列表页逻辑：数据渲染、按钮 tap 委托（#linkpreprocess/#linkpostprocess/#linknewrecord/#linktagprint/#linkedit/#linkremove）、#contextmenulist 委托（~1233）、本地覆写 pre_post（支持勾选多行）、showW 等待框简写、backArr 返回栈消费 |
| js/index.js | 登录页逻辑：版本号、协议首次弹窗、登录（在线/离线/无网络）、设备注册、忘记密码入口 |
| js/menulist.js | 功能选择页：menugroupLoad 加载菜单组 |
| js/menugroup.js | 首页宫格：下拉刷新 reloadApp（离线走 SQLite）、双击退出、MQTT 消息触发 |
| js/modelpara.js | 参数页：linkDMH5ParaListJS 拉取参数并渲染 |
| js/attachmodelpara.js | 附加模型参数页：读 AttachDmCode/Num/Title + extras（currRowData/linkrefresh/attachNum） |
| js/newrecord.js | 添加/编辑记录：录音、签名、文件上传、dataSubmitScriptType 区分增改 |
| js/setting.js | 设置页：版本检查、清缓存、语言、消息 |
| js/linkchart.js | ECharts 图表加载（三种模式，见下） |
| 其余 | 各对应页面的页面级逻辑 |

## 4. ECharts 图表（js/linkchart.js）

- 三种加载模式（showChartType）：0=`loadChartbyPara`（POST linkDMEChartScript，传 ChartParams）；1=`loadChartbyGDs`（POST linkDMChartScript，scriptType:104 + ChartGDs）；2=`loadChartbyLastPara`
- 服务端返回 **option 脚本字符串**，`loadScriptString(r.data)` eval 执行
- 生命周期：initChart 懒初始化；destroyChart 在 beforeback 时 dispose + 移除 resize 监听；图表高度=视口高-44-沉浸栏高度；离线/地图支持 libs/map/*.js、libs/bmap.js

## 5. 行数据结构 RDs / GDs

- **RDs（行数据数组）**：一行数据 = `[{Key, Type, Value}, ...]`；工具 `currRDs(ele)` 取当前行（元素 attr("para")），`cObj(r)` 把对象/数组转成该结构
- **GDs（多行集合）**：`[{"RowData":[RDs...]}]`，多行提交用
- 位置信息也是一条 RD：`{Key:"LINKLOCATION"|"LINKLOCATIONJSON", Type:"String", Value:...}`

## 6. "附加模型"概念

- 附加模型 = 挂在父模型（dmCode+dmNum）上的脚本/动作，编号 contextid（contextMenuNo）
- **代码拼接规则 `dmCode + dmNum + 'X'`**：作为附加模型族标识（如 TEST01+18+X → `TEST0118X`）
- 执行链：contextTap（linkparafill=1 → 先补充参数 attachmodelpara）→ contextCall →（可选定位）→ contextCall1 → DMContextAction 条件校验 → POST linkDMContextFunBack → 跳转/刷新
