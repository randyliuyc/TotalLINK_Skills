#!/usr/bin/env python3
"""模型 XML 静态诊断（零网络）。

用法:
    python3 validate_model.py <model.xml> [code num] [--columns COL1,COL2]

诊断在导入之前完成：找出「导入会被拒」「模型必然跑不通」的硬错误，
以及「大概率不对」的警告。规则依据 references/ 与 21 个真实样例。

严重级别:
    error    导入会被拒 / 反序列化必然失败 / 必填项缺失
    warning  运行时大概率不对（旧分隔符、参数未定义、CubeSetting 未覆盖列等）
    info     写法提示，不影响执行

退出码: 0 无 error / 1 存在 error / 2 用法或 IO 错误

--columns 传 `tlk model run` 返回的 columns（逗号分隔），用于对齐
「CubeSetting 是否覆盖实际返回列」；不传则跳过该检查。
"""

import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT_TAG = "SysDataModelXML"

INT_FIELDS = {"ModelNum", "Ret1", "Ret2", "Ret3", "Ret4", "Ret5", "H5MaxLines"}
BOOL_FIELDS = {"UseParameter", "ShowInMenu", "SysModelFlag"}
LIST_FIELDS = {"CubeSetting": "DMCubeSetting", "DMUsage": "DMUsage"}

# 参与占位符/标记扫描的字段（顺序同 SysDataModelXML 属性序）
SCRIPT_FIELDS = (
    "SQLScript", "SQLUpdateScript", "SQLNew", "SQLRemove", "SQLClear",
    "CallFunction", "JavaScript", "ModelSetting",
)

# 行级替换（#列名#）有意义的字段：这些脚本执行时总有一行数据
ROW_SCRIPT_FIELDS = ("SQLUpdateScript", "SQLNew", "SQLRemove", "SQLClear",
                     "CallFunction", "ModelSetting")

# 经 string.Format 处理、字面花括号需转义的字段。
# CallFunction / ModelSetting 的花括号是 JSON 结构本身，转义反而破坏语义。
BRACE_FIELDS = ("SQLScript", "SQLUpdateScript", "SQLNew", "SQLRemove",
                "SQLClear", "JavaScript")

PARA_TYPES = {"STR", "DROPDOWN", "DROPRELOAD", "MOREFUNC"}

CUBE_ATTRS = ("DMCODE", "DMNUM", "COLNAME", "CAPTION", "COLTYPE",
              "COLFORMAT", "COLAGGREGATE", "DISPORDER", "FORMULA")
CUBE_INT = {"DMNUM", "DISPORDER"}
USAGE_ATTRS = ("DMCODE", "DMNUM", "SCRIPT", "DMUSAGE")
USAGE_INT = {"DMNUM", "SCRIPT"}

# 行级占位符白名单：前缀命中即视为运行时占位符，不是「本模型的列名」
TOKEN_PREFIXES = ("LINKSCRIPTGET", "LINKSCRIPTRUN", "LINKRES", "LINKID_",
                  "SYSUSER", "LC.", "LINKDROP", "LINKLIST", "LINKTEXT", "LOAD")
TOKEN_EXACT = {"LINKROWID", "LOGIN_USER", "TAG"}

# --LINKxxx 标记：实证标记 + 应所在字段（None = 多字段通用）
FLAG_FIELD = {
    "--LINKSAVEONENTERKEY": "SQLUpdateScript",
    "--LINKEDITMODE": "SQLUpdateScript",
    "--LINKREQUIRED": "SQLUpdateScript",
    "--LINKADDNEWROWS": "SQLNew",
    "--LINKNOGROUP": "SQLScript",
    "--LINKDATAMINELAYOUT": "SQLScript",
    "--LINKLOADDATAIMMEDIATE": "SQLScript",
    "--LINKDATAMINEOVERVIEW": "SQLScript",
    "--LINKREFRESH": "SQLClear",
    "--LINKSCRIPTGET": None,
    "--LINKSCRIPTRUN": None,
}
# 源码有解析、样例未实证：格式必须先去读源码确认
FLAG_UNEVIDENCED = {
    "--LINKAUTHORIZE", "--LINKDATAAUTOSAVE", "--LINKADDNEWROWTOP",
    "--LINKGANTTVIEW", "--LINKCALENDARVIEW", "--LINKLOGICALDAY",
    "--LINKPIVOTGRID", "--LINKNOEXPORT", "--LINKWAITTASKDONE",
    "--LINKCALLFUNCTION", "--LINKSHOWPROCESS", "--LINKSHOWEXCEPTION",
    "--LINKUPDATESCRIPT", "--LINKDATATRANSPOSITION", "--LINKDETAILLIST",
    "--LINKBACKFUNC", "--LINKWINDOWMODE", "--LINKMYROWDATA",
}

# ModelSetting 运行时真实读取的键（大小写敏感，拼错即静默失效）
SETTING_KEYS = {
    "DataScript", "BaseScript", "CreateScript", "UpdateScript", "DeleteScript",
    "TreateScript", "EditCols", "EditValueList", "ColumnWidth",
    "DoubleClickDataMine", "GridDataSave", "leveldatasetting", "hidecols",
    "paraDisabled", "BeforeSaveAction", "AfterSaveAction", "Timeout",
    "LinkConn", "DataMineCondition", "WindowSize", "dataClear", "dataReplace",
    "dataFill", "filterRows", "columns", "fill", "find", "replace",
    "dmCode", "dmNum", "condition",
}
# 设计器转换器遗留键：没有运行时读取方，写了也不生效
SETTING_DEAD_KEYS = {
    "BatchEdit", "SaveOnEnterKey", "LinkEditMode", "AutoClose",
    "CopyPreviousLine", "LoadDataImmediate", "InputBox", "DeepAnalysisType",
    "LocationType", "RequiredCols", "DataMineOverview",
}

PARAM_INDEX_RE = re.compile(r"\{(\d{1,2})\}")
BRACE_TOKEN_RE = re.compile(r"\{\{|\}\}|\{\d{1,2}\}")
ROW_TOKEN_RE = re.compile(r"#([A-Za-z_][A-Za-z0-9_.]*)#")
FLAG_RE = re.compile(r"--LINK[A-Z]+")


def root_fields():
    names = ["ModelCode", "ModelNum", "ModelDesc", "KeyWords", "DataMineCode",
             "FunctionCode", "ChartType", "SQLScript", "SQLUpdateScript"]
    names += [f"Ret{i}" for i in range(1, 6)]
    names += ["UseParameter", "ConnString", "ModuleCode"]
    for i in range(1, 11):
        n = f"{i:02d}"
        names += [f"ParaLabel{n}", f"ParaType{n}",
                  f"ParaSearchCode{n}", f"ParaDefVal{n}"]
    names += ["SQLNew", "SQLRemove", "SQLClear", "H5List", "H5Detail", "H5Edit",
              "H5Chart", "H5MaxLines", "AllDataTreatTitle", "H5NewRec",
              "H5Para", "H5AttPara", "CallFunction", "JavaScript",
              "H5GridHeader", "H5GridDetail", "ImageFile", "ListPrint",
              "MD5HASH", "ModelSetting", "ShowInMenu", "SysModelFlag",
              "CubeSetting", "DMUsage"]
    return names


ROOT_FIELDS = set(root_fields())


class Diagnostics:
    def __init__(self):
        self.items = []

    def add(self, severity, code, path, message):
        self.items.append({
            "severity": severity,
            "code": code,
            "path": path,
            "message": message,
        })

    def error(self, code, path, message):
        self.add("error", code, path, message)

    def warning(self, code, path, message):
        self.add("warning", code, path, message)

    def info(self, code, path, message):
        self.add("info", code, path, message)

    def summary(self):
        summary = {"error": 0, "warning": 0, "info": 0}
        for item in self.items:
            summary[item["severity"]] += 1
        return summary


def text_of(root, tag):
    el = root.find(tag)
    if el is None or el.text is None:
        return ""
    return el.text.strip()


def field_text(el, tag):
    child = el.find(tag)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


# ---------------------------------------------------------------- 结构

def check_structure(root, d):
    seen = {}
    for child in root:
        tag = child.tag
        seen[tag] = seen.get(tag, 0) + 1
        if tag not in ROOT_FIELDS:
            d.error("UNKNOWN_ELEMENT", tag,
                    f"<{tag}> 不是 SysDataModelXML 的字段，导入后会被静默丢弃")
            continue
        if tag in LIST_FIELDS:
            expect = LIST_FIELDS[tag]
            names = set()
            for sub in child:
                if sub.tag != expect:
                    d.error("UNKNOWN_ELEMENT", f"{tag}/{sub.tag}",
                            f"<{tag}> 的子元素必须是 <{expect}>，实际 <{sub.tag}>")
                names.add(sub.tag)
            if expect not in names and len(child) > 0:
                d.error("UNKNOWN_ELEMENT", tag,
                        f"<{tag}> 内部结构异常，无法反序列化为 List(Of {expect})")
            continue
        if tag in INT_FIELDS:
            try:
                int((child.text or "0").strip() or "0")
            except ValueError:
                d.error("BAD_INT", tag,
                        f"<{tag}> 必须是整数，实际 {(child.text or '').strip()!r}")
        elif tag in BOOL_FIELDS:
            value = (child.text or "").strip().lower()
            if value not in ("true", "false"):
                d.error("BAD_BOOL", tag,
                        f"<{tag}> 必须是 true/false，实际 {(child.text or '').strip()!r}")

    for tag, count in seen.items():
        if count > 1 and tag not in LIST_FIELDS:
            d.error("DUPLICATE_ELEMENT", tag,
                    f"<{tag}> 出现 {count} 次，反序列化会报重复元素")

    for required in ("ModelCode", "ModelNum"):
        if text_of(root, required) == "":
            d.error("MISSING_FIELD", required, f"<{required}> 不能为空")


def check_identity(root, d, expect_code, expect_num):
    code = text_of(root, "ModelCode")
    raw_num = text_of(root, "ModelNum")
    num = None
    try:
        num = int(raw_num) if raw_num != "" else None
    except ValueError:
        num = None

    if code and not re.fullmatch(r"[A-Z][A-Z0-9._]*", code):
        d.warning("MODELCODE_NAMING", "ModelCode",
                  f"模型代码 {code!r} 不是「系统缩写+模块缩写」的大写形式")

    if expect_code is not None and code and code != expect_code:
        d.error("EXPECT_MISMATCH", "ModelCode",
                f"XML 内 ModelCode={code!r} 与期望 {expect_code!r} 不一致")
    if expect_num is not None and num is not None and num != expect_num:
        d.error("EXPECT_MISMATCH", "ModelNum",
                f"XML 内 ModelNum={num} 与期望 {expect_num} 不一致")

    if text_of(root, "SysModelFlag").lower() == "true":
        d.error("SYSMODELFLAG", "SysModelFlag",
                "SysModelFlag=true 是系统级模型，导入会被服务端拒绝；必须 false")

    image = text_of(root, "ImageFile")
    if image == "":
        d.warning("IMAGEFILE_EMPTY", "ImageFile",
                  "ImageFile 恒非空，写 #LINKRES#<0~99>")
    elif not re.fullmatch(r"#LINKRES#\d+", image):
        d.warning("IMAGEFILE_FORMAT", "ImageFile",
                  f"ImageFile 格式应为 #LINKRES#数字，实际 {image!r}")

    if text_of(root, "MD5HASH") == "":
        d.info("MD5HASH_EMPTY", "MD5HASH",
               "MD5HASH 留空即可：导入时由服务端重算，不是文档哈希")

    for i in range(1, 6):
        tag = f"Ret{i}"
        if text_of(root, tag) not in ("", "0"):
            d.warning("RET_NONZERO", tag,
                      f"<{tag}> 样例恒为 0，语义无证据，保持 0")

    h5 = [t for t in ("H5List", "H5Detail", "H5Edit", "H5Chart", "H5NewRec",
                      "H5Para", "H5AttPara", "H5GridHeader", "H5GridDetail")
          if text_of(root, t) != ""]
    if h5:
        d.warning("H5_NONEMPTY", ",".join(h5),
                  "H5 字段属 TotalLINK APP 场景，本 Skill 不覆盖；留空或保持原值")

    return code, num


# ---------------------------------------------------------------- 参数

def param_slots(root):
    """返回 [{index, label, type, search, defval}]，index 从 1 开始。"""
    slots = []
    for i in range(1, 11):
        n = f"{i:02d}"
        slots.append({
            "index": i,
            "label": text_of(root, f"ParaLabel{n}"),
            "type": text_of(root, f"ParaType{n}"),
            "search": text_of(root, f"ParaSearchCode{n}"),
            "defval": text_of(root, f"ParaDefVal{n}"),
        })
    return slots


def check_params(root, slots, d):
    last = 0
    for slot in slots:
        i = slot["index"]
        if slot["label"]:
            last = i
        if slot["type"] and slot["type"] not in PARA_TYPES:
            d.error("PARATYPE_ILLEGAL", f"ParaType{i:02d}",
                    f"ParaType 只能是 {'/'.join(sorted(PARA_TYPES))}，实际 {slot['type']!r}")
        if slot["type"] in ("DROPDOWN", "DROPRELOAD") and not slot["search"]:
            d.warning("PARA_DROPDOWN_SOURCE", f"ParaType{i:02d}",
                      f"{slot['type']} 需要 ParaSearchCode{i:02d} 指定下拉来源模型代码")
        if slot["search"] and not slot["label"]:
            d.warning("PARA_ORPHAN", f"ParaSearchCode{i:02d}",
                      f"ParaSearchCode{i:02d} 有值但 ParaLabel{i:02d} 为空，参数位不会显示")
        if not slot["label"] and (slot["type"] or slot["search"] or slot["defval"]):
            d.warning("PARA_ORPHAN", f"ParaLabel{i:02d}",
                      f"参数 {i} 只填了类型/来源/默认值，标签为空")

    for slot in slots[:last]:
        if not slot["label"]:
            d.warning("PARA_GAP", f"ParaLabel{slot['index']:02d}",
                      f"参数 {slot['index']} 标签为空但后续参数有值，位置参数会错位")
    return last


def check_placeholders(root, slots, last, is_main, d):
    """
    {N} / #列名# / 字面花括号。

    附加模型（ModelNum 不在 1~10）由主模型或其他模型调用，参数与行数据可能
    来自调用方，未定义的 {N} / #列名# 只提示不判错；主模型则判错。
    """
    defined = {s["index"] - 1: s for s in slots if s["label"]}
    used = set()

    for field in SCRIPT_FIELDS:
        text = text_of(root, field)
        if not text:
            continue

        for match in PARAM_INDEX_RE.finditer(text):
            idx = int(match.group(1))
            used.add(idx)
            if idx >= 10:
                d.error("PARAM_INDEX_UNDEFINED", field,
                        f"{{{idx}}} 超出参数上限（最大 {{9}}）")
            elif idx not in defined:
                message = (f"{{{idx}}} 没有对应参数（ParaLabel{idx + 1:02d} 为空），"
                           "运行时会原样留在脚本里")
                if is_main:
                    d.error("PARAM_INDEX_UNDEFINED", field, message)
                else:
                    d.warning("PARAM_INDEX_EXTERNAL", field,
                              message + "；附加模型可能由调用方传参，确认调用链")

        leftover = BRACE_TOKEN_RE.sub("", text)
        if field in BRACE_FIELDS and ("{" in leftover or "}" in leftover):
            d.warning("BRACE_UNESCAPED", field,
                      "脚本含未转义的字面花括号；经 string.Format 时会抛异常并回退逐参替换，"
                      "需要字面花括号时写 {{ }}")

        if field in ROW_SCRIPT_FIELDS:
            continue
        if field == "SQLScript" and is_main:
            check_row_tokens(text, field, d)

    for slot in slots:
        if slot["label"] and (slot["index"] - 1) not in used:
            d.warning("PARAM_UNUSED", f"ParaLabel{slot['index']:02d}",
                      f"参数 {slot['index']} 已定义但所有脚本都没引用 "
                      f"{{{slot['index'] - 1}}}")


def is_runtime_token(name):
    if name in TOKEN_EXACT:
        return True
    return name.upper().startswith(TOKEN_PREFIXES) or name.startswith(TOKEN_PREFIXES)


def check_row_tokens(text, field, d):
    for match in ROW_TOKEN_RE.finditer(text):
        name = match.group(1)
        if is_runtime_token(name):
            continue
        d.warning("ROW_TOKEN_IN_QUERY", field,
                  f"主模型 SQLScript 没有当前行，#{name}# 不会被替换"
                  "（行级占位符只能用在编辑/新增/删除/动作脚本）")
        return


# ---------------------------------------------------------------- 分隔符与标记

def check_separators(root, d):
    call = text_of(root, "CallFunction")
    if call:
        if "~<!>~" in call:
            if "~" in call.replace("~<!>~", ""):
                d.warning("SEPARATOR_MIXED", "CallFunction",
                          "同时出现 ~<!>~ 与单字符 ~，分段结果不可预期")
        elif "~" in call:
            d.warning("OLD_SEPARATOR", "CallFunction",
                      "使用旧单字符 ~ 分隔符；产出必须用 ~<!>~（读旧容忍）")

    script = text_of(root, "SQLScript")
    if re.search(r"LINKDATAMINE(?!~<!>~)~", script):
        d.warning("OLD_SEPARATOR", "SQLScript",
                  "LINKDATAMINE 用旧单字符 ~；产出必须写 LINKDATAMINE~<!>~<行号>")


def check_flags(root, d):
    for field in SCRIPT_FIELDS:
        text = text_of(root, field)
        if not text or "--LINK" not in text:
            continue
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("--"):
                continue
            for flag in FLAG_RE.findall(stripped):
                if flag in FLAG_UNEVIDENCED:
                    d.info("FLAG_UNEVIDENCED", field,
                           f"{flag} 源码有解析但样例无证据，参数格式须读源码确认")
                    continue
                if flag not in FLAG_FIELD:
                    d.warning("FLAG_UNKNOWN", field,
                              f"{flag} 不在已知标记表内，可能是拼写错误")
                    continue
                expected = FLAG_FIELD[flag]
                if expected and field != expected:
                    d.warning("FLAG_WRONG_FIELD", field,
                              f"{flag} 应写在 {expected}，写在 {field} 不会被解析")

                if flag == "--LINKREQUIRED":
                    value = stripped.split(flag, 1)[1].strip()
                    if not value.startswith(":") or not value[1:].strip():
                        d.warning("FLAG_FORMAT", field,
                                  "--LINKREQUIRED 格式为 --LINKREQUIRED:列1,列2")
                elif flag == "--LINKDATAMINELAYOUT":
                    value = stripped.split(flag, 1)[1].strip()
                    parts = value.lstrip(":").split(",")
                    if not value.startswith(":") or len(parts) != 2 \
                            or not all(p.strip().isdigit() for p in parts):
                        d.warning("FLAG_FORMAT", field,
                                  "--LINKDATAMINELAYOUT 格式为 --LINKDATAMINELAYOUT:比例1,比例2")

        for flag in ("--LINKSCRIPTGET", "--LINKSCRIPTRUN"):
            if flag not in text:
                continue
            for line in text.splitlines():
                if flag not in line:
                    continue
                value = line.split(flag, 1)[1]
                if not re.match(r"@[^:\s]+:", value):
                    d.warning("FLAG_FORMAT", field,
                              f"{flag} 格式为 {flag}@连接代码:脚本，末尾单独一行 # 结束")
            tail = text.rsplit(flag, 1)[1]
            if not re.search(r"(?m)^#\s*$", tail):
                d.warning("FLAG_FORMAT", field,
                          f"{flag} 内嵌脚本缺少结束行（单独一行的 #）")


# ---------------------------------------------------------------- CubeSetting

def check_cube(root, d, columns):
    el = root.find("CubeSetting")
    model_code = text_of(root, "ModelCode")
    model_num = text_of(root, "ModelNum")

    lang_of = {}
    formula_cols = []
    if el is not None:
        for cube in el:
            if cube.tag != "DMCubeSetting":
                continue
            for tag in cube:
                if tag.tag not in CUBE_ATTRS:
                    d.error("UNKNOWN_ELEMENT", f"CubeSetting/{tag.tag}",
                            f"<DMCubeSetting> 无 {tag.tag} 字段，导入后会被丢弃")
                elif tag.tag in CUBE_INT:
                    try:
                        int((tag.text or "0").strip() or "0")
                    except ValueError:
                        d.error("BAD_INT", f"CubeSetting/{tag.tag}",
                                f"{tag.tag} 必须是整数，实际 {(tag.text or '').strip()!r}")

            col = field_text(cube, "COLNAME")
            coltype = field_text(cube, "COLTYPE")
            formula = field_text(cube, "FORMULA")
            dm_code = field_text(cube, "DMCODE")
            dm_num = field_text(cube, "DMNUM")

            if not col:
                d.error("CUBE_COLNAME", "CubeSetting",
                        "DMCubeSetting 缺 COLNAME，该条设置无效")
                continue
            if not coltype.startswith("LANGUAGE-"):
                d.warning("CUBE_COLTYPE", f"CubeSetting/{col}",
                          f"COLTYPE 应为 LANGUAGE-<语言代码>，实际 {coltype!r}")
            else:
                lang_of.setdefault(col, set()).add(coltype)
            if formula:
                formula_cols.append(col)
            if (dm_code and dm_code != model_code) or (dm_num and dm_num != model_num):
                d.warning("CUBE_DMKEY", f"CubeSetting/{col}",
                          f"DMCODE/DMNUM={dm_code}#{dm_num} 与模型 "
                          f"{model_code}#{model_num} 不一致，导入时按实例编号覆盖")

    if formula_cols:
        d.warning("CUBE_FORMULA", "CubeSetting",
                  f"{len(formula_cols)} 列填了 FORMULA（历史遗留），生成时一律留空："
                  + ",".join(formula_cols[:10]))

    all_langs = set()
    for langs in lang_of.values():
        all_langs |= langs
    if len(all_langs) > 1:
        for col, langs in lang_of.items():
            missing = all_langs - langs
            if missing:
                d.info("CUBE_LANG_GAP", f"CubeSetting/{col}",
                       f"{col} 缺少 {'/'.join(sorted(missing))}，该语言下标题回落列名"
                       "（存量模型常见；新模型按每列×每语言补齐）")

    if not columns:
        d.info("CUBE_UNCHECKED", "CubeSetting",
               "未提供 --columns，跳过「覆盖实际返回列」检查（可用 tlk model run 的 columns）")
        return

    cube_cols = set(lang_of)
    skip = lambda c: c.upper() == "LINKROWID" or c.upper().startswith("LINKRESERVE_")
    for col in columns:
        if col and not skip(col) and col not in cube_cols:
            d.warning("CUBE_UNCOVERED", f"CubeSetting/{col}",
                      f"返回列 {col} 没有 CubeSetting，标题回落为列名")
    for col in cube_cols:
        if not skip(col) and col not in columns:
            d.warning("CUBE_STALE", f"CubeSetting/{col}",
                      f"CubeSetting 里的 {col} 不在本次返回列中（列名已改？）")


# ---------------------------------------------------------------- DMUsage

def check_usage(root, d):
    el = root.find("DMUsage")
    if el is None:
        return
    model_code = text_of(root, "ModelCode")
    model_num = text_of(root, "ModelNum")
    for usage in el:
        if usage.tag != "DMUsage":
            continue
        for tag in usage:
            if tag.tag not in USAGE_ATTRS:
                d.error("UNKNOWN_ELEMENT", f"DMUsage/{tag.tag}",
                        f"<DMUsage> 无 {tag.tag} 字段，导入后会被丢弃")
            elif tag.tag in USAGE_INT:
                try:
                    int((tag.text or "0").strip() or "0")
                except ValueError:
                    d.error("BAD_INT", f"DMUsage/{tag.tag}",
                            f"{tag.tag} 必须是整数，实际 {(tag.text or '').strip()!r}")
        script = field_text(usage, "SCRIPT")
        if script and script not in ("0", "3", "4"):
            d.warning("USAGE_SCRIPT", "DMUsage",
                      f"SCRIPT={script} 不在样例取值 0/3/4 内，确认脚本类型编号")
        if not field_text(usage, "DMUSAGE"):
            d.info("USAGE_EMPTY", "DMUsage", "DMUSAGE 为空，该条使用说明不生效")
        dm_code = field_text(usage, "DMCODE")
        dm_num = field_text(usage, "DMNUM")
        if (dm_code and dm_code != model_code) or (dm_num and dm_num != model_num):
            d.warning("USAGE_DMKEY", "DMUsage",
                      f"DMCODE/DMNUM={dm_code}#{dm_num} 与模型 "
                      f"{model_code}#{model_num} 不一致")


# ---------------------------------------------------------------- ModelSetting

def walk_keys(obj, path, visit):
    if isinstance(obj, dict):
        for key, value in obj.items():
            visit(key, path)
            walk_keys(value, f"{path}.{key}", visit)
    elif isinstance(obj, list):
        for item in obj:
            walk_keys(item, path, visit)


def check_modelsetting(root, d):
    text = text_of(root, "ModelSetting")
    if not text:
        return
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        if "{" in text and (PARAM_INDEX_RE.search(text) or ROW_TOKEN_RE.search(text)):
            d.warning("MODELSETTING_JSON_DYNAMIC", "ModelSetting",
                      f"占位符替换后才能解析（当前 {e.msg}），确认替换后是合法 JSON")
        else:
            d.error("MODELSETTING_JSON", "ModelSetting",
                    f"JSON 解析失败（{e.msg}），运行时静默当作空配置")
        return

    lower_map = {k.lower(): k for k in SETTING_KEYS}

    def visit(key, path):
        if key in SETTING_DEAD_KEYS:
            d.warning("MODELSETTING_DEAD_KEY", f"ModelSetting{path}",
                      f"{key} 没有运行时读取方，行为由 --LINKxxx 脚本标记控制")
            return
        if key in SETTING_KEYS:
            return
        official = lower_map.get(key.lower())
        if official:
            d.warning("MODELSETTING_CASE", f"ModelSetting{path}",
                      f"键名大小写错误：{key!r} 应为 {official!r}，写错即静默失效")
        elif not key.isupper():
            d.warning("MODELSETTING_UNKNOWN_KEY", f"ModelSetting{path}",
                      f"{key!r} 不在运行时读取的键表内，确认拼写")

    walk_keys(data, "", visit)


# ---------------------------------------------------------------- 入口

def validate_tree(root, expect_code=None, expect_num=None, columns=None):
    d = Diagnostics()

    if root.tag != ROOT_TAG:
        d.error("ROOT_TAG", root.tag,
                f"根元素必须是 <{ROOT_TAG}>，实际 <{root.tag}>")
        return d, "", None

    check_structure(root, d)
    code, num = check_identity(root, d, expect_code, expect_num)
    is_main = num is not None and 1 <= num <= 10
    slots = param_slots(root)
    last = check_params(root, slots, d)
    check_placeholders(root, slots, last, is_main, d)
    check_separators(root, d)
    check_flags(root, d)
    check_cube(root, d, columns)
    check_usage(root, d)
    check_modelsetting(root, d)
    return d, code, num


def validate_file(path, expect_code=None, expect_num=None, columns=None):
    try:
        with open(path, encoding="utf-8-sig") as f:
            raw = f.read()
    except OSError as e:
        return {"error": "IO", "message": f"读取失败：{e}", "file": path}

    try:
        root = ET.fromstring(raw)
    except ET.ParseError as e:
        diag = Diagnostics()
        diag.error("XML_PARSE", "", f"XML 解析失败：{e}")
        return _result(path, "", None, diag)

    diag, code, num = validate_tree(root, expect_code, expect_num, columns)
    return _result(path, code, num, diag)


def _result(path, code, num, diag):
    summary = diag.summary()
    result = {
        "file": path,
        "model": {"code": code, "num": num},
        "summary": summary,
        "diagnostics": diag.items,
    }
    if summary["error"]:
        result = {
            "error": "VALIDATE",
            "message": f"发现 {summary['error']} 个 error 级诊断，先修再导入",
            **result,
        }
    return result


def _parse_columns(raw):
    if not raw:
        return None
    return [c.strip() for c in raw.split(",") if c.strip()]


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = [a for a in argv if a.startswith("--")]
    columns = None
    for opt in opts:
        if opt.startswith("--columns="):
            columns = _parse_columns(opt.split("=", 1)[1])
        elif opt == "--columns":
            print("用法: --columns=COL1,COL2", file=sys.stderr)
            return 2
        else:
            print(f"未知选项 {opt}", file=sys.stderr)
            return 2

    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    expect_code = args[1] if len(args) > 1 else None
    expect_num = None
    if len(args) > 2:
        try:
            expect_num = int(args[2])
        except ValueError:
            print(f"编号必须是整数，实际 {args[2]!r}", file=sys.stderr)
            return 2

    result = validate_file(args[0], expect_code, expect_num, columns)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
