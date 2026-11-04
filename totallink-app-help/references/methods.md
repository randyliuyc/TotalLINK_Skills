# 项目方法库（以源码核实为准）

> 本文件是对项目 API 方法的逐条归档，**全部以 /Users/link2.0/app 源码核实为准**（行号为编写时快照，引用前需 read_file/search_content 复核），不依赖任何外部文档链接。
> 核心文件：js/linkshared.js（下表未注明文件者均在此）。标注【页面可重写】的是业务模型开发者的扩展点。

## 1. 扫描

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| scan_para【入口】 | :41 | `scan_para(id,r,type)` 扫描触发总入口 → scan_impl/autoResolve/scanAfterActionImpl |
| scan_impl | :133 | `scan_impl(id,r,type)`：`{json}` 走 deal_json；`{ajax…}` 走 scan_ajax |
| deal_json | :176 | `deal_json(r)` JSON 解析并按 id 赋值表单元素 |
| scan_ajax | :198 | `scan_ajax(id,arr,res,type)` ajax 取数 → deal_json + scanAfterActionImpl |
| scanAfterAction【页面可重写】 | :110 | `scanAfterAction(id)` 扫描后自定义处理（被 scanAfterActionImpl :90 调用） |
| reScanFlag【页面可重写】 | :82 | `reScanFlag(id)` return true 则扫描后执行保存 |
| keep_focus | :256 | `keep_focus(id)` 扫描后保持焦点（常配 setTimeout） |
| LINK_SCAN_AFTER | :4349 | 扫描后回调变量（页面赋值，:4353 使用） |
| broadcastPara | :2786 | `var broadcastPara={value,filter}` 广播参数对象（注意是对象不是字符串） |
| getBroadcast | :2790 | `getBroadcast()` 注册 Android 广播，收到值后 scan_para |
| openBroadcast | :1575 | 全局开关变量 `var openBroadcast=memGet("broadcast")`（"1" 时启用），非方法 |
| autoResolve | :3809 | `autoResolve(id,r,ele)`：元素带 [resolve] 且无 [no-scan] → scan_impl；**带 [automatch] 且 ele 有值 → autoMatching(id,ele)** |
| autoMatching | :4177 | 自动带出实现：解析元素 `automatch` 属性（JSON，格式 `{目标元素id: 数据源字段}`），对每个映射执行 `$("#目标id").val(val).text(text).attr("value",val)`，其中 val=ele[字段]，text 优先取 ele[字段+"DES"]；完成后调 autoMatch(id,ele) |
| autoMatch【页面可重写】 | :4205 | `autoMatch(id,ele)` 自动带出完成后的自定义钩子（switch(id) 按触发元素 id 写自定义逻辑），默认空实现 |
| 触发点 | :8483-8506 | 输入历史列表点击（inputListory_info :8314-8324，元素带 automatch 属性时选中历史值后自动带出） |

## 2. 执行钩子（页面可重写）

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| BEFORE_STA_ARRAY / AFTER_STA_ARRAY | :4260/:4261 | `["para","attach","new","memo","linkquick","autoSave","content","upload"]` |
| beforeFunction | :4262 | `beforeFunction(sta,id)` return true 拦截后续动作 |
| afterFunction | :4265 | `afterFunction(sta,id)` 执行后处理 |
| reloadAfter | :4269 | `reloadAfter()` 数据加载后自定义动作（:4345 调用） |
| ifBeforeAction | :4665 | `ifBeforeAction(a,r,row)` 单接口执行前校验（配 submitAction before 属性） |
| beforeAlert / stopAlert | :4566/:4570 | 拦截/终止时提示（可重写覆盖） |
| stopFunction | :4654 | `stopFunction(a,r,row)` 是否终止剩余接口（配 stop 属性） |
| customFunction | :4657 调用点 | api='function' 时调用，**定义需由业务页面提供**（配 express 属性） |
| initModelparaPage | :8534 | 参数界面返回时触发（注意：定义在 linkshared.js，modelpara.js 仅调用） |

### 2.1 执行前模型校验（服务端条件动作）

与"页面级" beforeFunction 不同，**模型级执行前校验**由服务端条件动作完成，入口是 `DMContextAction(type=1, action, RDs, func, code, num)`（POST `/api/DataModel/linkDMConditionAction`）：
- 调用点：linkquickAction3（新增，action="1"）、linkquickAction5（编辑，action="2"）、linkquickAction6（删除，action="3"）、contextCall1（附加功能校验，action="6"，code=`dmCode+dmNum+'X'`）
- 返回 `dataType=="modelActionInfo"` 时按 `a.type` 分支：1 → 执行 func + 长 toast；2 → mui.confirm 确认后才 func；3 → `a.condition` 为 True/1 才执行 func，否则 alert(a.message)；空白内容直接 func
- 即"能不能执行"由模型配置的条件动作决定，客户端只按 type 分支处理；详见 functions.md §2、linkquick.md §10

## 3. UI 扩展

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| addIcons | :6787 | `addIcons(id,text,icon,para,page)` 底部操作栏新增/替换图标（page: content/para/new/attach/memo） |
| setParaControl | :6923 | `setParaControl(ary,code,num,para,keys)` 生成顶部筛选标签，输出到 #para-filter |
| span_keys | :6906 | 标签 key 映射对象（.code/.num/.para/.text/.value/.id/.single/.active） |
| linkPicklistFun | :2498 | `linkPicklistFun(id)` 列表自定义选择初始化 |

## 4. 防重复点击

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| repeatTime | :4325 | `repeatTime(id)` 返回重复间隔（秒），页面可重写按 id 区分 |
| repeatTimeByElement | :4320 | 优先读元素 `repeatTime` **属性**，缺省回退 repeatTime(id) |
| ifRepeatSta / resetRepeatSta / limitTimeAction | :4304/:4312/:4329 | 锁表 LINK_REPEAT_STA，默认 1s（详见 linkquick.md §8） |

注意：**不存在** `link_repeat_time` 变量；个性化间隔靠元素属性 `repeatTime` 或重写 `repeatTime(id)`。

## 5. 音频 / TTS

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| playAudio | js/audio.js:106 | `playAudio(path)` 播放音频（本地 _www/libs/audio 或网络地址） |
| text2audio | :7076 | `text2audio(token,id,t,opt)` 百度 TTS（linkquick=15 用） |

## 6. 数据与接口

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| linkAjax | :3185 | `linkAjax(para,url,opt)` Promise 化 ajax |
| linkAjax_JQ | :3176 | jQuery 版 ajax |
| linkQuickAjax1 | :4777 | api=1 `/api/DataModel/linkDMDatasetResult` 获取模型数据 |
| linkQuickAjax2 | :4781 | api=2 `/api/DataModel/linkDMGridRowSubmit` 单行提交 |
| linkQuickAjax3 | :4799 | api=3 `/api/DataModel/linkDMContextFunBack` 附加功能/单行处理 |
| linkQuickAjax4 | :4803 | api=4 `/api/DataModel/linkDMGridDataSubmit` 多行提交 |
| linkQuickAjax5 | :4806 | api=5 `/api/LINK/linkFormula` 公式计算 |
| linkQuickAjax6 | :4810 | api=6 `/api/DataModel/linkDMFormData` 模板跳转/刷新 |
| linkQuickAjax7 | :4825 | api=7 `/api/DataModel/linkDMDataSubmit` 全量提交 |
| refreshData | :8529 | `refreshData(para)` 手动刷新内容界面（para 数组对应模型 {0}{1}{2}） |
| getDmResult | :3492 | `getDmResult(code,num,para,Rds)` |
| getMain | :3454 | `getMain(code,num,id,RDs,para)` 单行（linkDMContextFunBack） |
| getDmData | :3473 | `getDmData(code,num,type,GDs,para,RDs)` 多行 |

注意：**不存在**名为 `linkFormula` 的函数，公式只通过 linkQuickAjax5 的接口调用。

## 7. 表单取值与校验

| 名称 | 位置 | 签名与行为 |
|---|---|---|
| valueList | :1923 | `valueList(type)` 有 type 返回标准对象，否则 Key-Value 数组 |
| reParaList | :3849 | `reParaList(id)` 收集界面参数为有序数组（模型 {0}{1}…） |
| getValue | :1849 | `getValue(t,id)` 按元素类型自动取值（val/text/attr） |
| validationList | :1840 | `validationList()` required 必填校验，通过返回 true |
| filterPara | :1916 | `filterPara(ele)` 返回 true 则该元素不参与提交，页面可重写 |
| clear_input | :1603 | `clear_input(ele)` 清空界面输入（实现 clear_input_impl :1624） |
| [props] 属性 | :1437-1454 | 逗号分隔控制选中后赋值目标（text/value/val/自定义属性） |
| [target-id] 属性 | :1433 | 指定赋值/带出的目标元素 id |

## 8. 核实结论：清单中不存在 / 需更正的条目

**未找到（引用时会报 undefined，勿使用）**：
- `link_repeat_time` —— 无此变量；防重复间隔靠元素属性 `repeatTime`（repeatTimeByElement :4320 读取）
- `linkFormula` —— 无同名函数；公式计算只通过 linkQuickAjax5 的 `/api/LINK/linkFormula` 接口
- `linkcollapse-hide` / `linkcollapse-show` —— css 与 js 中均无（css/mui.min.css 亦无）
- `getServerInfo` —— 不存在
- `showNotifyDialog` —— 不存在；实际为 `loadNotifyDialog(arr)`（:9747）
- `alert` 重写 —— js 内无 window.alert 重写；弹框走 mui popup（:9523/:9534）

**是变量/对象/DOM 而非方法（不要当函数调用）**：
- `broadcastPara`（:2786 对象 {value,filter}）、`openBroadcast`（:1575 全局开关变量）、`submitH5`/`submitInit`/`submitAction`（:9279-9281 配置对象）、`gobalpickData`/`linkObj`/`inputListory_info`/`link_mqtt_ele`/`static_lang`/`span_keys`/`LINK_ASYNC`/`LINK_CONDITION`/`NO_CLOSE_WAITING`/`typeMappings`
- `linkUploadImage`/`linkUploadFile`（newrecord.js :809/:841）是按钮 DOM id；`linkMedia` 是容器 class（.linkMedia 系列）——上传/媒体逻辑走 initMediaContainer（:8925）体系
- 样式类定义在 css/mui.min.css：linkcard(:668)/linkcard-1(:684)/linkcard-2(:746)/linkcard-3(:764，另有 linkcard-4 :785)/linkleft(:840)/linkcenter(:836)/linkright(:844)/linkflexbox(:661)/linkflexfooter(:848)/.link-submit(:855)

**其它差异**：
- `broadcastPara` 的属性是 `filter`（过滤器 action 名）与 `value`（监听字段名），均字符串
- `showChartbyPara` 仅见调用（modelpara.js:110），定义未在 js/ 静态文件中找到（可能由 load_js 动态加载的服务端脚本提供）
- `customFunction`（:4657 调用）由业务页面提供定义，配元素 `js`/`express` 属性
- `link-append` 折叠面板组件在 linkshared.js 尾部（:10337/:10354/:10359），容器内 `[append]` 为懒加载区（:10407）
