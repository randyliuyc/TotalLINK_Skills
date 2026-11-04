#!/usr/bin/env python3
"""model 命令组（TotalLINK 数据模型设计）。

由 `scripts/tlk.py` 按插件契约发现并注册，成为 `tlk model <子命令>`：

  dict     表字典查询（配置驱动：编号/连接/参数模板存 ~/.totallink/config.json，
           缺省 SYSTEMCODE/30；模型不存在或列结构未知时降级提示，不猜）
  export   导出模型 XML 到文件（linkDMExport）
  import   导入模型 XML 落库（linkDMImport，服务端重算 MD5HASH）
  run      设计态运行（linkDMRun，不计配额、不校验 AccessFlag）
  validate 纯 XML 静态诊断（不走网络）

插件契约：GROUP / register(subparsers) / 可选 HELP，见 `scripts/tlk.py` 顶部 docstring。
"""

import json
import os
import sys

GROUP = "model"
HELP = "数据模型设计：字典 / 导出 / 导入 / 运行 / 静态校验"

# 表字典缺省配置：模型编号与参数模板都可在项目配置 dict 键下覆盖
DICT_DEFAULTS = {
    "dmCode": "SYSTEMCODE",
    "dmNum": 30,
    "conn": "LINKDB",
    "db": "LINKDB",
    "args": ["{conn}", "{db}", "{table}"],
}
# 归一化列词汇表：schema 命中 COLNAME 才做归一化，否则原样输出并标注「列映射未知」
_DICT_KNOWN_COLS = ("COLNAME", "COLDESC", "COLTYPE", "COLLEN", "SCALE",
                    "PK", "IDENT", "ALLOWNULL", "SEQ")

_HERE = os.path.dirname(os.path.abspath(__file__))
# 本组自带 scripts/（validate_model.py）；tlk_core 由入口注入的 scripts/ 提供
sys.path.insert(0, os.path.join(_HERE, "scripts"))

import tlk_core  # noqa: E402
import validate_model  # noqa: E402


def _emit(obj):
    """打印结果；含 error 字段即失败（与 base 的输出版本一致）。"""
    print(json.dumps(obj, ensure_ascii=False, indent=2))
    sys.exit(1 if isinstance(obj, dict) and "error" in obj else 0)


def _parse_params_json(raw):
    try:
        return tlk_core.parse_params_json(raw)
    except ValueError as e:
        _emit({"error": "PARAM", "message": f"--params-json {e}"})


def _merge_data(head, resp):
    """把响应 data（字典）平铺进输出；data 不是字典时原样放在 data 字段。"""
    data = resp.get("data")
    out = dict(head)
    if isinstance(data, dict):
        out.update(data)
    else:
        out["data"] = data
    out["_project"] = resp.get("_project")
    return out


# ---------------------------------------------------------------- dict

def _dict_cfg(project_key, proj_cfg):
    """读项目配置里的 dict 节，叠加缺省值。"""
    cfg = (proj_cfg or {}).get("dict") or {}
    out = dict(DICT_DEFAULTS)
    out.update({k: v for k, v in cfg.items() if v is not None})
    return out


def _save_dict_cfg(project_key, values):
    """把 dict 配置写进 ~/.totallink/config.json 对应项目节。"""
    all_cfg = tlk_core.load_all_config()
    if not all_cfg or project_key not in all_cfg.get("projects", {}):
        return {"error": "CONFIG",
                "message": f"项目 '{project_key}' 不存在，先运行 env add"}
    all_cfg["projects"][project_key]["dict"] = values
    tlk_core.save_config(all_cfg)
    return None


def _dict_normalize(table):
    """
    尽力而为归一化：schema 命中已知词汇表（含 COLNAME）→ 输出紧凑列清单；
    否则原样输出 schema/captions/样例行并标注列映射未知（由调用方向用户确认）。
    """
    schema = table.get("schema") or []
    rows = table.get("data") or []
    recs = [dict(zip(schema, r)) for r in rows]

    if "COLNAME" not in schema:
        return None, recs

    cols = []
    for r in recs:
        def _v(k):
            v = r.get(k)
            return "" if v is None else str(v).strip()
        typ = _v("COLTYPE")
        if typ and _v("COLLEN"):
            typ = f"{typ}({_v('COLLEN')}"
            if _v("SCALE") not in ("", "0"):
                typ += f",{_v('SCALE')}"
            typ += ")"
        cols.append({
            "name": _v("COLNAME"),
            "type": typ,
            "desc": _v("COLDESC"),
            "pk": _v("PK") not in ("", "0"),
            "null": _v("ALLOWNULL") == "1",
            "ident": _v("IDENT") not in ("", "0"),
            "seq": int(_v("SEQ") or 0),
        })
    return cols, recs


def cmd_dict(args):
    project_key, proj_cfg = tlk_core.get_project_config(args.project)
    if not proj_cfg:
        _emit({"error": "CONFIG",
               "message": "没有可用项目配置，先运行 env add / env use"})

    cfg = _dict_cfg(project_key, proj_cfg)
    # CLI 临时覆盖
    if args.code:
        cfg["dmCode"] = args.code
    if args.num is not None:
        cfg["dmNum"] = args.num
    if args.conn:
        cfg["conn"] = args.conn
    if args.db:
        cfg["db"] = args.db
    if args.args:
        try:
            tpl = json.loads(args.args)
        except json.JSONDecodeError as e:
            _emit({"error": "PARAM", "message": f"--args 不是合法 JSON：{e}"})
        if not (isinstance(tpl, list) and tpl and all(isinstance(x, str) for x in tpl)):
            _emit({"error": "PARAM",
                   "message": "--args 必须是字符串数组模板，如 '[\"{conn}\",\"{db}\",\"{table}\"]'"})
        cfg["args"] = tpl

    if args.save:
        err = _save_dict_cfg(project_key or (args.project or ""), {
            "dmCode": cfg["dmCode"], "dmNum": cfg["dmNum"],
            "conn": cfg.get("conn", ""), "db": cfg.get("db", ""),
            "args": cfg["args"],
        })
        if err:
            _emit(err)

    # 按参数模板生成 Para（占位符缺失时取空串，保证位置对齐）
    params = [t.format(table=args.table, conn=cfg.get("conn", ""),
                       db=cfg.get("db", "")) for t in cfg["args"]]

    resp = tlk_core.call(cfg["dmCode"], cfg["dmNum"], params=params,
                         script_type=0, project=args.project,
                         timeout=args.timeout)
    if "error" in resp:
        resp["hint"] = ("表字典模型不可用。处理路径：① python3 scripts/tlk.py tools search "
                        "\"表结构\" 查找字典能力；② 由用户提供 dmCode/dmNum 后用 "
                        "--code/--num 临时指定，或加 --save 写入项目配置；③ 请用户开放该功能。")
        _emit(resp)

    data = resp.get("data") or {}
    table = data.get("Table") if isinstance(data, dict) else None
    if not isinstance(table, dict) or not table.get("schema"):
        _emit({"error": "BIZ",
               "message": "返回中没有 Table.schema，无法识别为表字典结果",
               "raw_data_type": type(data).__name__})

    cols, recs = _dict_normalize(table)
    out = {
        "status": "ok",
        "table": args.table,
        "dict_model": f"{cfg['dmCode']}/{cfg['dmNum']}",
        "_project": resp.get("_project"),
    }
    if cols is not None:
        out["columns"] = cols            # 归一化清单：问卷/任务书直接用
        out["columnNames"] = [c["name"] for c in cols]
        out["normalized"] = True
        if not cols:
            out["note"] = ("列清单为空：该表可能不在当前字典模型覆盖的连接/库上"
                           "（环境常多库并存，如 MES 表与 X3 表分属不同连接），"
                           "或表名拼写不同。先确认表所在连接（问用户/查存量模型引用），"
                           "再用 --conn/--db 重试；仍为空则改问用户列结构，不要猜。")
    else:
        out["normalized"] = False
        out["note"] = ("列映射未知（schema 与已知词汇表不匹配），以下为原始结构，"
                       "请向用户确认各列含义后再使用，不要猜。")
        out["schema"] = table.get("schema")
        out["captions"] = table.get("captions")
        out["sampleRows"] = recs[: max(0, args.sample)]
    if resp.get("_warning"):
        out["_warning"] = resp["_warning"]
    if args.save:
        out["saved"] = {"project": project_key, "dict": {
            k: cfg[k] for k in ("dmCode", "dmNum", "conn", "db", "args")}}
    _emit(out)


# ---------------------------------------------------------------- export

def cmd_export(args):
    resp = tlk_core.dm_export(args.code, args.num,
                              project=args.project, timeout=args.timeout)
    if "error" in resp:
        _emit(resp)

    xml = resp.get("data")
    if not isinstance(xml, str) or not xml.strip():
        _emit({"error": "BIZ", "message": "导出返回的 data 为空",
               "_project": resp.get("_project")})

    try:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(xml)
    except OSError as e:
        _emit({"error": "IO", "message": f"写入失败：{e}", "file": args.output})

    _emit({
        "status": "ok",
        "code": args.code,
        "num": args.num,
        "file": os.path.abspath(args.output),
        "bytes": len(xml.encode("utf-8")),
        "_project": resp.get("_project"),
    })


# ---------------------------------------------------------------- import

def cmd_import(args):
    try:
        with open(args.file, encoding="utf-8-sig") as f:
            xml = f.read()
    except OSError as e:
        _emit({"error": "IO", "message": f"读取失败：{e}", "file": args.file})

    if not xml.strip():
        _emit({"error": "IO", "message": "文件为空", "file": args.file})
    if "<SysDataModelXML" not in xml:
        _emit({"error": "PARAM",
               "message": "不是模型 XML（根元素应为 <SysDataModelXML>）",
               "file": args.file})

    resp = tlk_core.dm_import(xml, code=args.code, num=args.num,
                              force=args.force, project=args.project,
                              timeout=args.timeout)
    if "error" in resp:
        _emit(resp)

    _emit(_merge_data({"status": "ok", "file": os.path.abspath(args.file)}, resp))


# ---------------------------------------------------------------- run

def cmd_run(args):
    if args.max_rows < 1 or args.max_rows > tlk_core.MAX_ROWS_LIMIT:
        _emit({"error": "PARAM",
               "message": f"--max-rows 须在 1~{tlk_core.MAX_ROWS_LIMIT} 之间"
                          f"（服务端上限 {tlk_core.MAX_ROWS_LIMIT}）"})

    resp = tlk_core.dm_run(
        args.code, args.num,
        params=_parse_params_json(args.params_json),
        script_type=args.script_type,
        max_rows=args.max_rows,
        row_data=args.row_data,
        project=args.project,
        timeout=args.timeout,
    )
    if "error" in resp:
        _emit(resp)

    _emit(_merge_data({"status": "ok", "code": args.code, "num": args.num,
                       "scriptType": args.script_type}, resp))


# ---------------------------------------------------------------- validate

def cmd_validate(args):
    columns = validate_model.parse_columns(args.columns)
    _emit(validate_model.validate_file(args.file, args.code, args.num,
                                       columns, env=args.env))


# ---------------------------------------------------------------- 注册

def _add_common(p, timeout=True):
    """加所有子命令共用的 --project（及 --timeout）。"""
    p.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    if timeout:
        p.add_argument("--timeout", type=int, default=tlk_core.DEFAULT_TIMEOUT,
                       help=f"请求超时秒数（默认 {tlk_core.DEFAULT_TIMEOUT}）")


def register(subparsers):
    p = subparsers.add_parser(
        "dict", help="表字典查询（配置驱动，缺省 SYSTEMCODE/30）")
    p.add_argument("table", metavar="TABLE", help="表名，如 BPCUS")
    p.add_argument("--code", help="字典模型 dmCode（缺省用项目配置，再缺省 SYSTEMCODE）")
    p.add_argument("--num", type=int, help="字典模型 dmNum（缺省用项目配置，再缺省 30）")
    p.add_argument("--conn", help="链接代码（缺省用项目配置，再缺省 LINKDB）")
    p.add_argument("--db", help="数据库名（缺省用项目配置，再缺省 LINKDB）")
    p.add_argument("--args", metavar="JSON",
                   help="参数模板（字符串数组，占位符 {table}/{conn}/{db}），"
                        "如 '[\"{conn}\",\"{db}\",\"{table}\"]'")
    p.add_argument("--sample", type=int, default=3, metavar="N",
                   help="列映射未知时输出原始样例行数（默认 3）")
    p.add_argument("--save", action="store_true",
                   help="把本次生效的字典配置写入项目配置（~/.totallink/config.json）")
    _add_common(p)
    p.set_defaults(handler=cmd_dict)

    p = subparsers.add_parser("export", help="导出模型 XML 到文件（linkDMExport）")
    p.add_argument("code", metavar="dmCode")
    p.add_argument("num", metavar="dmNum", type=int)
    p.add_argument("-o", "--output", required=True, metavar="FILE",
                   help="输出文件路径")
    _add_common(p)
    p.set_defaults(handler=cmd_export)

    p = subparsers.add_parser("import", help="导入模型 XML 落库（linkDMImport）")
    p.add_argument("file", metavar="FILE", help="模型 XML 文件")
    p.add_argument("--force", action="store_true",
                   help="目标编号已存在时覆盖（默认拒绝）")
    p.add_argument("--code", help="落库模型代码（缺省用 XML 内嵌）")
    p.add_argument("--num", type=int, help="落库模型编号（缺省用 XML 内嵌）")
    _add_common(p)
    p.set_defaults(handler=cmd_import)

    p = subparsers.add_parser("run", help="设计态运行模型（linkDMRun，不计配额）")
    p.add_argument("code", metavar="dmCode")
    p.add_argument("num", metavar="dmNum", type=int)
    p.add_argument("--params-json", default="[]", metavar="JSON",
                   help="参数数组（JSON 数组），空位传 \"\"，如 '[\"\"]'")
    p.add_argument("--script-type", type=int, default=0,
                   help="0=执行查询；其他值只回展开后的脚本，不执行数据库（默认 0）")
    p.add_argument("--max-rows", type=int, default=tlk_core.DEFAULT_MAX_ROWS,
                   metavar="N",
                   help=f"返回行数上限（默认 {tlk_core.DEFAULT_MAX_ROWS}，"
                        f"上限 {tlk_core.MAX_ROWS_LIMIT}）")
    p.add_argument("--row-data", type=json.loads, default={},
                   help="替换脚本里 #列名# 的数据行（JSON 字典）")
    _add_common(p)
    p.set_defaults(handler=cmd_run)

    p = subparsers.add_parser("validate", help="模型 XML 静态诊断（不走网络）")
    p.add_argument("file", metavar="FILE", help="模型 XML 文件")
    p.add_argument("code", nargs="?", metavar="dmCode",
                   help="校验 XML 内 ModelCode 是否等于该值")
    p.add_argument("num", nargs="?", type=int, metavar="dmNum",
                   help="校验 XML 内 ModelNum 是否等于该值")
    p.add_argument("--columns", metavar="COL1,COL2",
                   help="实际返回列（取自 tlk model run 的 columns），"
                        "用于 CubeSetting 覆盖检查")
    p.add_argument("--env", choices=("fb", "app"), default=None,
                   help="目标环境标签：fb=FB 表单模型（500 检查）；"
                        "app=APP 模型（H5 族成对性/非空检查）")
    p.set_defaults(handler=cmd_validate)
