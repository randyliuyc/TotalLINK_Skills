# linkquick 属性完整用法（js/linkshared.js）

> 行号为编写时快照（linkshared.js 当前版本），引用前用 read_file 核实。

## 1. 事件委托与入口

```js
// ~4393 全局委托（document 级，tap）
$(document).on('tap', '[linkquick]', function(e) {
	e.stopPropagation();
	var t=this
	linkQimplMethod(t)
});
```

`linkQimplMethod(t)`（~4399）流程：
1. 防重复：`if(ifRepeatSta("",t))return limitTimeAction(id,t); resetRepeatSta(t);`（默认锁 1s）
2. 读元素 `confirm` 属性 → 有则 `mui.confirm`，确认后 `linkQimpl(t)`（e.index==0）
3. 读 `prompt` 属性 → 有则 `mui.prompt`，输入回写元素 value 后 `linkQimpl(t)`
4. 否则直接 `linkQimpl(t)`

## 2. linkQimpl 分发（~4426）

```js
function linkQimpl(ele){
	var id=return_ele_id($(ele))
	var type=$(ele).attr("linkquick")
	var flag="linkquick"+type
	if(BEFORE_STA_ARRAY.indexOf("linkquick")!=-1&&beforeFunction(flag,id))return;//执行前校验
	var nwaiting=showWaiting(rLang("wait"),id);
	switch ((type+"")){ ... }
}
```

## 3. 分发表（case → 函数 → 行为）

| linkquick 值 | 功能 | 函数（行号） | 行为要点 |
|---|---|---|---|
| '1' | 预处理 | linkquickAction1（:4858） | `DMContextAction(0,"21",currRDs(ele),()=>pre_post(ele,"linkpreprocess",nw))`；离线走 `_offline` |
| '2' | 后处理 | linkquickAction2（:4867） | `DMContextAction(0,"41",...)` → `pre_post(ele,"linkpostprocess",nw)` |
| '3' | 添加记录（可带定位） | linkquickAction3（:4876） | 先 `DMContextAction(1,"1",...)` 校验，linklocation=1/2 时先 getAdrLoc，成功后 `recNew()`；读 `linklocation` 属性（本元素或最近祖先） |
| '4' | 打印 | linkquickAction4（~4901） | `showTagprint(rePrintPara(ele))`，取勾选行 RowData |
| '5' | 编辑 | linkquickAction5（~4945） | 先 `DMContextAction(1,"2",...)` 校验（可带定位），成功后 `editImpl(ele,nw)` |
| '6' | 删除 | linkquickAction6（:4964） | `DMContextAction(1,"3",currRDs(ele),()=>recRemov(ele,nw))` |
| '7' | 打开地址 | linkquickAction7 | 打开 URL 类地址 |
| '8' | 附加功能/上下文菜单 | linkquickAction8（:5082） | 取 `btnid`（无则 `id`）作 contextid；linkimage=1/2 → openCam 拍照；linklocation=1/2 → 先定位再 `DMContextAction(0,contextid,...)`；否则直接 `DMContextAction(0,contextid,currRDs(ele),()=>contextTap(contextid,linktitle,linkrefresh,linkparafill,...))` |
| '9' | URL 功能列表 | linkquickAction9（:5136） | `urlFunctionTap(contextid,linktitle,ele,nw)` → attachURLFunction（打开 URL 附加功能） |
| '10' | 数据挖掘 | linkquickAction10（:5153） | 读 `btnid`、`paraconfirm`、`echartflag`；组装 data 入 backArr（`safeBackArrPush`，上限 20 条），调 `dataMine(...)` |
| '11' | 打开第三方 APP | linkquickAction11 | 属性 `pname`(Android)/`action`(iOS)/`extra`(JSON) → launchApp |
| '12' | 提交所有数据（模型自定义） | linkquickAction12 | loc=`linklocation` → memSet；读 `linklocation` 属性，循环参数数组按 `a.api` 1~7 调 linkQuickAjax1~7，'function' 走 customFunction（eval 元素 `js` 属性）；每轮 `formulaData(a,r,row)` 回写公式、`tipAndAlert`、`stopFunction` 中断；离线走 `_offline` |
| '13' | 低功耗蓝牙 | linkquickAction13 | 属性 `service`/`key` 设 serviceId/characteristicId |
| '14' | MQTT | linkquickAction14 | MQTT 消息触发 |
| '15' | 文字转语音 | linkquickAction15 | 属性 `text`/`token`/`spd`/`pit`/`per` → text2audio；离线 `_offline` |
| '16' | 自定义函数 | linkquickAction16 | eval 元素 `js` 属性 |

（case '8' 注释原文：`//contextmenulist`；case '9'：`//linkurllist`；case '10'：`//linkcontextdatamine`——即 8/9/10 分别对应长按菜单/URL 列表/数据挖掘列表三个容器。）

## 4. linkquickAction8 详细行为（附加功能/长按菜单核心）

```js
function linkquickAction8(ele,nw){                       // :5082
	if(ifOffline())return linkquickAction8_offline(ele,nw);
	var id=$(ele).attr("id")
	var contextid = ele.getAttribute("btnid")||id;       // 优先 btnid
	var linkrefresh = ele.getAttribute("linkrefresh");
	var linkparafill = ele.getAttribute("linkparafill");
	var linktitle = ele.getAttribute("linktitle");
	var bd = ele.getAttribute("linkimage");
	if (contextid == "linkmap") { turnOnAdr(ele); mui.openWindow({...linkmap...}); return; }
	memSet("linkLocation", linklocation);                // linklocation: 0不需要/1文字/2JSON
	if (bd == "1" || bd == "2") { openCam(contextid, linktitle, linkrefresh, linkparafill, bd, ele); return; }
	if (linklocation == "1" || linklocation=="2") {
		getAdrLoc(function(t) {
			DMContextAction(0, contextid, currRDs(ele).concat(t), function(t) {
				contextTap(contextid, linktitle, linkrefresh, linkparafill, currRDs(ele).concat(t), id, nw);
			})
		})
	} else {
		DMContextAction(0, contextid, currRDs(ele), function() {
			contextTap(contextid, linktitle, linkrefresh, linkparafill, currRDs(ele), id, nw);
		})
	}
}
```

`contextTap`（:5519）：先 `mui('#contextPopover').popover('hide')`；
- `linkparafill == "1"`：生成 `AttachDmCode = globleDmCode + globleDmNum + 'X'`，memSet AttachDmCode/AttachDmNum(=contextid)/AttachDmTitle，closeWaiting 后 `showAttachModelPara(...)`（打开附加模型参数补充页 attachmodelpara.html）
- 否则：`linkpopopvercheck(currRDsLineNo)` 通过才 `contextCall(LinkID, globleServer, globleDmCode, globleDmNum, contextid, cRDs, linkrefresh, id, nw)`，否则 toast contentlist.filter1

`contextCall`（:752）→（可选地理定位）→ `contextCall1`（:1219）：
- 先发**附加模型校验**：`DMContextAction(1, "6", RDs, func, DmCode+DmNum+'X', contextid)`（url=linkDMConditionAction，校验通过才继续）
- 校验通过后真正执行：POST `linkDMContextFunBack`（parajson: `{loginID, par:{dm:{dmCode, dmNum}, contextMenuNo: contextid, RDs}}`），toast message，`linkDMFuncBackImpl(r.data)`

## 5. linkquick 元素可用自定义属性（reAllPara 收集，~4496）

从元素及最近 `[id]` 祖先收集：`id、linkquick、code、num、para、api、rowdata、formula、script、before、beforeTip、stop、stopTip、express、tip、alert、prefix、suffix` 等。即 linkquick 元素可通过自定义属性扩展行为：confirm/prompt 确认框、before/stop 执行前后条件、formula/tip/alert 结果处理、api 选择接口等。

## 6. 配套 AJAX：linkQuickAjax1~7（~4777-4838）

| api | 端点 | 用途 |
|---|---|---|
| 1 | `/api/DataModel/linkDMDatasetResult` | 获取基本模型数据 |
| 2 | `/api/DataModel/linkDMGridRowSubmit` | 单行数据提交（par: {dm, scriptType, RDs}） |
| 3 | `/api/DataModel/linkDMContextFunBack` | 附加模型执行后回跳/单行处理 |
| 4 | `/api/DataModel/linkDMGridDataSubmit` | 多行数据提交 |
| 5 | `/api/LINK/linkFormula` | GET，公式计算 |
| 6 | `/api/DataModel/linkDMFormData` | 载入模板/跳转刷新 |
| 7 | `/api/DataModel/linkDMDataSubmit` | 全量数据提交（data:{formData:RDs}） |

## 7. 使用位置说明

- HTML 中没有静态 `linkquick="x"` 属性——linkquick 元素来自**服务端返回并动态渲染的模板**（FunList/ContextMenuList/URLList/DataMineList），因此必须用全局委托。
- 长按菜单项委托：contentlist.js `mui('#contextmenulist').on('tap','li',...)`（~1233）直接调 `linkquickAction8(this, showW(this))`（该组 li 只有 btnid，无 id 无 linkquick）。
- js 内直接绑定固定 ID 按钮调用 linkquickActionN 的位置：contentlist.js 928-991（`#linkpreprocess`/`#linkpostprocess`/`#linknewrecord`/`#linktagprint`/`#linkedit`/`#linkremove`，模式统一：`ifRepeatSta → resetRepeatSta → beforeFunction → linkquickActionN(this, showW(this)) → afterFunction`）。注意 955-963 的 `#linktagprint` 里 afterFunction 被重复调用了两次（历史遗留）。

## 8. 防重复点击（~4301-4330）

```js
var LINK_REPEAT_STA={}                       // 全局锁表
function ifRepeatSta(id,ele)  // key = id 参数 || ele的id || 最近[id]祖先的id
function resetRepeatSta(ele,oid){ LINK_REPEAT_STA[id]=true;
  setTimeout(...=false, (repeatTimeByElement(id)||1)*1000) } // 默认1秒
function repeatTimeByElement(id) // 优先元素属性 repeatTime（秒），否则 repeatTime(id)=1
function limitTimeAction(id,ele) // 被锁时的提示钩子（默认空实现，可重写）
```

使用范式（contentlist.js 928-931 等）：`if(ifRepeatSta("linkpreprocess"))return limitTimeAction("linkpreprocess"); resetRepeatSta(this,"linkpreprocess")`。

## 9. 调试案例一：一次点击触发两次"完全相同"的请求（真 bug，双委托命中）

**现象**：点击顶部功能按钮（如预处理），真机日志出现两条内容完全相同的 `DMContextAction` parajson。

**机制**：本项目同时存在两套 document 级 tap 委托：
1. contentlist.js 928-991：按 id 绑定的特化委托（`#linkpreprocess` → linkquickAction1 固定 code "21" 等）；
2. linkshared.js ~4393：按 `[linkquick]` 属性绑定的全局委托 → linkQimpl → case '1' → 同一个 linkquickAction1。

若服务端下发的按钮 DOM **同时带 `id="linkpreprocess"` 和 `linkquick="1"`**，一次 tap 会被两条委托各命中一次（`e.stopPropagation()` 挡不住同一 document 上的其它委托 handler），两次都进入 linkquickAction1 → 两条相同日志。

**防重为何没拦住**：两条链的 key 取法不同——特化委托 key 固定 `"linkpreprocess"`；通用委托 key 取 `this` 的 id 或 `closest("[id]")` 祖先 id。只要被点元素/其最近带 id 祖先的 id 不是该字符串（如 id 在内层 a、linkquick 在外层 li），两条链各用各的 key，互不拦截。

**插桩判读方法**（真机 console）：
- 打印服务端 FunList HTML（contentlist.js `funclist.innerHTML = r.data.FunList;` 之后 `console.log(funclist.innerHTML)`）看按钮是否 id+linkquick 双属性；
- 两条委托入口各打标记日志（`委托A(id委托)` / `委托B(linkquick委托)` + outerHTML）；
- linkquickAction1 入口打印 `new Error().stack` 第二行区分来源。

**修复方向**（二选一）：
1. 删掉 contentlist.js 特化委托，统一走 `[linkquick]` 通用委托（需逐条核对 linkrefresh/beforeFunction 细节）；
2. 保守做法：让通用委托与特化委托**共用同一防重 key**（把显式 id 传入 `ifRepeatSta(id,t)`/`resetRepeatSta(t,id)`）。

## 10. 调试案例二：长按菜单"两次请求"——不是 bug，是设计

点击 `#contextmenulist` 里的附加功能项（如 `<li btnid="501" linkrefresh="0" linkparafill="0" ...>`，这组 li 只有 btnid、无 id 无 linkquick，只能命中 contextmenulist 委托 → linkquickAction8），**设计上就是两段式**：

```
tap 委托(1次) → linkquickAction8
  ├─ 第1次 DMContextAction(0, contextid="501", ...)   → POST linkDMContextActionInfo（功能信息/判断）
  └─ 回调 contextTap →（linkparafill=0）contextCall → contextCall1
       └─ 第2次 DMContextAction(1, "6", ..., DmCode+DmNum+'X', contextid)
            → POST linkDMConditionAction（附加模型校验，dmCode 如 TEST0118X，dmNum=501）
            → 校验通过后 POST linkDMContextFunBack 真正执行
```

**判读技巧**：`DMContextAction` 的日志里，type=0 的请求带 `contextMenuNo` 字段，type=1 的请求带 `action` 字段；`dmCode` 形如 `主code+主num+'X'`（如 TEST0118X）的是附加模型校验。两条日志内容不同 = 业务链路正常；两条日志完全相同 = 疑似 §9 的重复触发。

**附带问题**：第 2 段请求若返回 `操作异常400 Bad Request`，通常是服务端对 `linkDMConditionAction`（dmCode=TEST0118X/dmNum=501/action=6）没有配置校验条件或附加模型 code 拼接规则与服务端不一致，需查服务端模型配置，不是客户端重复调用。
