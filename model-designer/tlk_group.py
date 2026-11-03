#!/usr/bin/env python3
"""model 命令组（TotalLINK 数据模型设计）。

由 `scripts/tlk.py` 按插件契约发现并注册，成为 `tlk model <子命令>`：

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
HELP = "数据模型设计：导出 / 导入 / 运行 / 静态校验"

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
    _emit(validate_model.validate_file(args.file, args.code, args.num, columns))


# ---------------------------------------------------------------- 注册

def _add_common(p, timeout=True):
    """加所有子命令共用的 --project（及 --timeout）。"""
    p.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    if timeout:
        p.add_argument("--timeout", type=int, default=tlk_core.DEFAULT_TIMEOUT,
                       help=f"请求超时秒数（默认 {tlk_core.DEFAULT_TIMEOUT}）")


def register(subparsers):
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
    p.set_defaults(handler=cmd_validate)
