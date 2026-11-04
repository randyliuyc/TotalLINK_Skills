# 约定 class 与特定元素 id（以源码检索为准）

> 检索范围：js/linkshared.js（数百处选择器）+ contentlist.js/newrecord.js/menulist.js/menugroup.js/index.js/setting.js 等页面 js，并对照各 html。行号为编写时快照，引用前需复核。非穷举但覆盖全部已知点。

## 1. 约定 class

### 1.1 上传 / 媒体类

| class | 位置 | 行为 |
|---|---|---|
| linkUploadImage | linkshared.js:8624（tap 委托）；:1046、:1917（参数收集识别） | tap → 拍照(:8887)/相册(:8906)上传图片 |
| linkUploadFile | :8659 | tap → 上传附件文件 |
| linkMedia | :1605、:2224、:8673、:8676、:8752、:8926-8939 | 媒体列表容器：删除子项（tap 内 .mui-icon-trash）、tap .linkMediaFile 打开文件 |
| linkMediaImages / linkMediaFiles | :8994（框架动态生成） | linkMedia 内部图片区/文件区容器 |
| linkMediaImage | :8677、:9002-9008、:4273 | tap 图片预览（填充 LINKIMAGES_IMAGE） |
| linkMediaFile / _text / _p | :9012-9020、:8677 | 打开文件；文件名/副标题展示 |
| linkimage | newrecord.js:259、:580 等；linkshared.js:4273 | newrecord 图片九宫格子项（≤9 张）；tap 预览 |
| linkimgDiv | newrecord.js:256、:585 | 图片容器 |
| linkfile | newrecord.js:260、:722；fileicon.js | click 打开附件 |
| linkrec | linkshared.js:2227-2228 | 录音控件（清空时同时清 rec-src 属性） |

### 1.2 卡片 / 布局类

| class | 位置 | 行为 |
|---|---|---|
| linkcard | linkshared.js:1016-1017（禁内部 input 默认行为）、:9402、:9589 | 列表卡片项；closest(".linkcard") 配合折叠 |
| linkcard-1 / linkcard-4 | :9826、:9952 / :9640、:9657、:9678 | 动态生成卡片变体；-4 为消息卡片（#notify 内计数/时间刷新） |
| linkcard-title | :9819、:9952 | 卡片标题条 |
| linkflexbox / linkleft | :9646-9648、:9943 | 消息区容器 |
| linkflexfooter | :9968 | 卡片底部按钮区（success=/error= 属性） |
| linkcollapse-hide / linkcollapse-show | :9388-:9420 | tap 切换折叠（配合 closest(".linkcard")） |
| link-table-default / linktable | :1481-1482 | 表格滚动同步表头 |
| linkabscenter / linkhide / link-input / linkRow | index.html、login.css | 纯样式（登录页布局） |

### 1.3 表单控件类（模型 H5 最重要扩展点）

| class | 位置 | 行为 |
|---|---|---|
| linkpicker | :1050、:1857、:4099 | 输入触发 picker 弹层 |
| linkdate | :1056、:1857 | 触发日期选择 |
| linkpicklist | :1058-1061、:2593-2600 | 触发 linkPicklistFun 自定义选择（生成 linkPicklistDiv 弹层，css/picklist.css） |
| link-picklist2/3、link-backdrop2/3 | :2561-2635 | 选择弹层 li 触摸变色、遮罩关闭 |
| linkmultiple（+linkmultipleClear/Cancel/OK） | :3871-3880、:4099-4113、:4122 | 多选控件：change 联动、清除/取消/确定 |
| linkdatasearch | :4099、:4122-4152；modelpara.html:92 | 打开数据搜索选择（配 expression/separator/one/target-id 属性） |
| linkcheckbox | :2148-2203 | tap 切换勾选 |
| linkcheckbox-one / linkcheckbox-multiple | :8542-8552（change）、:1891-1906 | 单选/多选组取值；参与必填校验 |
| linkcheckdiv + linkcheck | :2173、:2384；contentlist.js:591、:996 | 列表批量勾选容器（存在则显示勾选栏） |
| linktextarea | :51、:6771-6778 | 文本域（input 自动增高） |
| linktexteditdiv | :2682-2691、:4097 | tap 标签聚焦、focus/blur 样式切换 |
| linkswitch | :1861、:4095-4096、:9303 | 开关：mui-active ↔ 值 "1"/"0" |
| link-submit-content | :1899-1912（取值）、:9241-9251（按钮 ok/cancel → linkSubmit） | **模型 H5 提交表单约定容器**：内部 input/select 取值；按钮加 ok/cancel class 触发提交/取消 |
| linkUploadImage/linkUploadFile（取值排除） | :1917 | 不参与参数收集 |
| linkdealdiv（[data] 属性） | :2358-2415 | 服务端下发数据回填 option/input |
| 软键盘焦点白名单 | :1605 | .linkMedia,.linktextarea,.linkmultiple,.linkdatasearch... 显示软键盘时聚焦 |
| 必填校验 class 集 | :1857-1858 | .linkcheckbox-*、.linkpicker、.linkdate、.linkdatasearch、.linkmultiple... |

### 1.4 列表 / 操作类

| class | 位置 | 行为 |
|---|---|---|
| linkSliderCls | contentlist.js:1325、:1360 | 列表项左/右滑操作（slideleft/slideright） |
| linkendline | contentlist.js:822 | 分页尾元素（渲染前 remove） |
| linkcontext / linkmorefun | contentlist.js:1098-1099 | 长按菜单/更多功能图标置灰 |
| linksearch | contentlist.js:1118 | 搜索过滤 |
| link-address | contentlist.js:1196 | 列表项地址文本（长按 → 打开地图） |
| linkDialTele | contentlist.js:715-718 | 多号码拨号菜单 |
| linkappend / link-append | linkshared.js:10354 | 追加区（阻止冒泡判断） |

### 1.5 提示 / 杂项类

| class | 位置 | 行为 |
|---|---|---|
| link_toast-box / linkbuttonClose | linkshared.js:3729-3785；css/linkToast.css | 自定义 toast（tap 关闭） |
| linkjavascript | :2263、:2295；各 html `<script id="linkjavascript">` | 服务端下发 JS 的挂载点（remove 后 append；id+class 混用） |
| statusListShow | :9492 | 状态栏显隐 |
| linkEditPlus / linkEditMinus | editApp.js:336-339 | 桌面编辑模式添加/删除图标 |
| linkcollection | collection.js:71-124；setting.js:1592 | 收藏项 tap 打开、longtap 取消收藏 |
| link-fav / link-faved | menugroup.js:522；menulist.js:350 | 收藏/取消收藏 |
| linkaddIcon | menugroup.js:514 | 添加图标 |
| linkdiv / link-active / linkmainmenu | menulist.js:275、:345 | 菜单滚动定位 |
| linkalldiv / linkversion / link-language / linkpoint | index.js、setting.js | 登录页显隐/版本号/语言切换/设置红点 |
| link-loading | search.js:349 | 加载完移除 |

## 2. 特定元素 id 约定

### 2.1 全局/跨页面

| id | 位置 | 所属页面 | 行为 |
|---|---|---|---|
| linkinput | linkshared.js:44、:188、:1584、:1640；contentlist.js:11 | contentlist/modelpara/newrecord/attachmodelpara/linkmemo | **扫描输入区**：keydown 回车 → scan_para("linkinput", r) |
| linksavepwd | :1322；index.html:60 | index | 记住密码勾选框 |
| linkswitch | :2348；contentlist.html:157 | contentlist | 只看未完成开关（mui-switch） |
| linkjavascript | :2263、:2295 | 所有页面 | 挂载服务端下发 JS |
| link_a_location | :1605、:6335；newrecord.js:287 | newrecord（动态） | 定位地址展示，点击开地图 |
| linkfilter | :8052 | 动态生成 | 打开筛选 |
| linkInputClear / linkInputClose | :8514、:8521 | 动态（扫描框旁） | 清除记录/关闭 |
| autosave_btn | :91-92、:4361；newrecord.html:155 | newrecord | 扫描后自动保存开关（mui-active 判断） |
| autoadd_btn | :1762、:4364；newrecord.js:126 | newrecord | 连续添加开关（保存后继续） |
| linkREC / linkSIG | :1938-1945（页面存在 #linksignopen 则写入） | newrecord（动态） | 提交时自动携带录音/签名数据 |
| todoList | :9426-9460（动态生成） | menugroup（动态） | 待办轮播 slider |
| notify | :9563、:9839；menugroup.html:114 | menugroup | 消息通知容器 |
| mesPoint / item1 / item2 | :9839；menugroup.html:82/:86/:113 | menugroup | 消息红点 / 分段选项卡 |

### 2.2 contentlist（列表页）

| id | 位置 | 行为 |
|---|---|---|
| content | contentlist.html:146；contentlist.js:123 | 总容器 |
| paralist | contentlist.html:77 | 参数区（服务端 ParaList 填充） |
| para-area-content | contentlist.html:127 | 顶部筛选参数区 |
| reset / search / scan | contentlist.html:83/:87/:62 | tap：重置/查询/扫一扫 |
| list | contentlist.html:168 | 列表主体（空/追加 h5 数据） |
| moredata | 动态生成 | 加载更多（下一页前先 remove） |
| linkul / linkPopoverCheck | contentlist.html:147-157 | 筛选列表 ul / 筛选 popover |
| linkreload | contentlist.html:33 | 刷新 |
| menugroup | contentlist.html:38 | 打开功能分组菜单 |
| linkmore | contentlist.html:51 | 更多功能入口（href="#moreFunctions"） |
| shareFunction | contentlist.html:237 | 分享面板 popover（linktele/linksms/linkmail/linkwx 四项） |
| linktoggle / linkget / linksubmit | contentlist.html:261-267 | 离线切换/缓存模型数据/上传同步 |
| linkmorechoice（duoxuan/quanxuan/fanxuan/quxiao） | contentlist.html:288-295 | 多选/全选/反选/取消 |
| moreFunctions | contentlist.html:311 | 功能弹出层（popover） |
| linkurllist | contentlist.html:315 | URL 功能列表（li tap → linkquickAction9） |
| linkfunlist | contentlist.html:321 | 功能列表（服务端 FunList 填充） |
| contextPopover | contentlist.html:335 | 长按弹出层 |
| linkcontextdatamine | contentlist.html:338 | 关联菜单-数据挖掘列表（li tap → linkquickAction10） |
| contextmenulist | contentlist.html:340 | 长按关联菜单列表（li tap → linkquickAction8） |
| linkpreprocess / linkpostprocess / linknewrecord / linktagprint / linkedit / linkremove | **动态生成**（html 无静态） | 底部工具栏按钮（contentlist.js:926-980 委托） |

### 2.3 modelpara / attachmodelpara（参数页）

| id | 位置 | 行为 |
|---|---|---|
| paralist | modelpara.html:96 | 参数输入区 |
| linkreset / loaddata | modelpara.html:48/:52 | 重置/查询按钮 |
| barcode | modelpara.html:39；newrecord.html:132 | 头部扫一扫图标 |
| linkPicklist | modelpara.html:61 | 自定义选择 popover |
| attachparalist | attachmodelpara.html:76 | 附加参数界面 |

### 2.4 newrecord（新增/编辑页）

| id | 位置 | 行为 |
|---|---|---|
| linkeditlist（变体 linkeditlist1） | newrecord.html:162；linkmemo.html:154 | **录入表单容器**（服务端 H5ParaListJS 内容填充） |
| linkok | newrecord.html:144；newrecord.js:157 | 保存（recSave(...,"new","linkok")） |
| linkcancel / linkreset | newrecord.html:136/:140 | 取消/重置 |
| linksign 系列（linksign/linksignopen/linksignarea/linksignsave/signContent/signature） | **js 动态生成**（appendsign，newrecord.js:673-804） | 签名画布全链路；保存后数据进 linkSIG |
| linkaudio / link-file / linklocDiv | 动态 | 录音控件/附件区/定位区 |

### 2.5 menulist / menugroup / index / uploadimage

| id | 位置 | 行为 |
|---|---|---|
| linkmenugroup / list / linkmenulist / linkfav / linkinfo / linksetup | menulist.html:27-94 | 菜单页区域：分组列表、主菜单、收藏、设置 |
| girdList / historyList / segmentedControl / sheet1 / clearHis / deleteHis / linkhome | menugroup.html:28-147 | 功能宫格、历史记录、消息页、清空历史 |
| linkserver / linkuser / linkpwd / login / devicereg / forgetPsw / language / fwxy / yszc | index.html:16-100 | 登录页：服务器/用户名/密码/登录/注册/语言/协议 |
| carema_pic_foot | uploadimage.html:76 | 拍照底部按钮 |

## 3. 归纳

### 3.1 class 命名规律

- **`link` 无连字符前缀 = 交互控件/数据绑定约定**（linkpicker/linkdate/linkpicklist/linkmultiple/linkdatasearch/linkcheckbox-*/linktextarea/linkswitch/linktexteditdiv/linkUploadImage/linkUploadFile/linkMedia*/linkcard*）：js 通过 tap/change/input 事件委托触发框架行为，并参与取值/校验（linkshared.js:1857-1918、:3871-4152、:8542-8552）。**写模型 H5 时用这些 class 即可被框架识别。**
- **`link-` 连字符前缀 = 结构/容器/主题约定**（link-submit-content、link-backdrop2/3、link-picklist2/3、link-append、link-language、link-table-*、link_toast-*）：多为容器、遮罩、toast、i18n 标记。
- **纯样式/页面私有 class**（linkabscenter/linkhide/link-null/linkpoint/linkversion/linkalldiv 等）：仅对应页面使用。
- **mui 原生 class**（mui-active/mui-hidden/mui-switch 等）：js 大量用 `hasClass("mui-active")` 判断开关状态（:92、:1762、:2348、:4095）；样式集中在 css/mui.min.css（已定制合并 155 处 .link* 规则），其余分布在 contentlist.css(40)/menulist.css(32)/login.css(18)/picklist.css(15) 等。

### 3.2 id 的页面区域规律

- **每页固定骨架**：header（mui-bar-nav）、content（mui-content）、modelTitle、linkjavascript（服务端 JS 挂载）、linkinput（扫描输入区，5 个页面都有）。
- **contentlist 专属**：paralist/para-area-content/list/moredata/linkul/shareFunction/moreFunctions/contextPopover/linkurllist/linkfunlist/contextmenulist/linkcontextdatamine。
- **newrecord**：linkeditlist/linkok/linkcancel/linkreset/autoadd_btn/autosave_btn；签名/录音/附件 id（linksign*、signContent、linkaudio、link-file、link_a_location）**由 js 动态生成，html 中不存在**。
- **列表操作按钮**（linkpreprocess/linkpostprocess/linknewrecord/linktagprint/linkedit/linkremove）**不在静态 html 中**，由 contentlist.js 依模型配置动态生成底部工具栏。

### 3.3 模型 H5 / 服务端模板可用扩展点清单

写模型 h5（经 linkDMH5ParaListJS、r.data.Data 等注入 paralist/linkeditlist/para-area-content/list）时框架实际识别的扩展点：

- **控件 class**：linkinput、linktextarea、linktexteditdiv、linkpicker、linkdate、linkpicklist、linkmultiple(+Clear/Cancel/OK)、linkdatasearch（配 expression/separator/one/target-id/group 属性）、linkcheckbox-one、linkcheckbox-multiple、linkcheckdiv+linkcheck、linkswitch、linkUploadImage、linkUploadFile、linkMedia（内部 linkMediaImages/Files/Image/File）、linkimage/linkimgDiv/linkfile/linkrec、linkdealdiv[data]
- **结构/容器 class**：link-submit-content（提交区，按钮加 ok/cancel class 触发提交/取消）、linkcard、linkcard-1/2/3/4、linkcard-title、linkflexbox、linkflexfooter、linkcollapse-hide/show、linkSliderCls、linkendline、link-address
- **id 扩展点**：linkinput、list、paralist、attachparalist、linkeditlist、moredata、linkul、linkfunlist、linkurllist、contextmenulist、linkcontextdatamine、moreFunctions、contextPopover、link_a_location、link-file、linksignopen（存在即自动携带 LINKSIG/LINKREC，:1938-1945）、linkok/linkcancel/linkreset 及六个动态工具栏按钮
- **注意**：`linkhref`/`linkaddress`/`linkmain` 在 js 中**未检索到行为绑定**（仅 link-address、linkmainmenu 有据），勿凭印象使用
