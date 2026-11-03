#!/usr/bin/env python3
"""TotalLINK CLI 单入口。

本入口独占 `tlk` 命令，拥有 base 四组命令：
  env    list / add / use          项目环境管理
  auth   verify                    环境自检（项目 / URL / 用户 / 额度）
  call   <dmCode> <dmNum>          统一 API 调用（linkDMAIAction）
  tools  search <关键字>           工具发现（SEARCHLIST）

其余命令组由插件提供。插件发现契约（与 base 解耦，base 不认识任何具体插件）：

  1. 在**本文件父目录**（与根 SKILL.md 同级）下的任意子目录放一个 tlk_group.py；
  2. 该模块必须定义：
       GROUP = "<命令组名>"            # 非空字符串，成为 `tlk <GROUP> ...`
       def register(subparsers): ...   # subparsers 是该组的子命令容器
                                       # （已设 dest="action"，你必须 add_parser）
     可选定义 HELP = "<一行说明>"，用于 `tlk --help` 的列表说明；
  3. 目录没有 tlk_group.py 时该组自然消失，base 不做任何兜底；
  4. 两个插件声明同名 GROUP 时直接报错退出；
  5. 插件可直接 `import tlk_core`（入口已把 scripts/ 放入 sys.path）。

用法：
  python3 scripts/tlk.py env list
  python3 scripts/tlk.py env use "TotalLINK 开发环境"
  python3 scripts/tlk.py auth verify
  python3 scripts/tlk.py call TMESCOM01 9 --script-type 0 --params-json '[""]'
  python3 scripts/tlk.py tools search 报销
"""

import argparse
import importlib.util
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tlk_core

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_FILE = "tlk_group.py"


def _print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _emit(obj):
    """打印结果；含 error 字段时以 exit 1 结束。"""
    _print_json(obj)
    if isinstance(obj, dict) and "error" in obj:
        sys.exit(1)


# ---------------------------------------------------------------- base 命令

def cmd_env_list(args):
    _print_json(tlk_core.list_projects())


def cmd_env_add(args):
    if not args.token:
        _emit({"error": "PARAM", "message": "env add 需要配合 --token"})
    _emit(tlk_core.add_project(
        project_name=args.name,
        auth_token=args.token,
        base_url=args.url or tlk_core.DEFAULT_BASE_URL,
    ))


def cmd_env_use(args):
    _emit(tlk_core.set_active_project(args.name))


def cmd_auth_verify(args):
    _emit(tlk_core.verify(project=args.project))


def _parse_params_json(raw):
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        _emit({"error": "PARAM", "message": f"--params-json 不是合法 JSON：{e}"})
    if not isinstance(params, list):
        _emit({"error": "PARAM", "message": "--params-json 必须是 JSON 数组，如 '[\"\"]'"})
    return params


def cmd_call(args):
    _emit(tlk_core.call(
        dm_code=args.dm_code,
        dm_num=args.dm_num,
        params=_parse_params_json(args.params_json),
        script_type=args.script_type,
        row_data=args.row_data,
        table_data=args.table_data,
        project=args.project,
        timeout=args.timeout,
    ))


def cmd_tools_search(args):
    _emit(tlk_core.search_tools(args.keyword, project=args.project))


# ---------------------------------------------------------------- 插件发现

def _load_plugin_module(dir_name, plugin_path):
    """按文件路径加载插件模块（目录名参与模块名，避免同名冲突）。"""
    module_name = f"tlk_plugin_{dir_name}"
    spec = importlib.util.spec_from_file_location(module_name, plugin_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def discover_plugins(subparsers):
    """
    扫描与 SKILL.md 同级的子目录，注册其中的 tlk_group.py。

    - 目录缺席 → 该组不存在（无兜底、无报错）
    - 同名 GROUP → 报错退出
    """
    if not os.path.isdir(BASE_DIR):
        return

    seen = {}
    for dir_name in sorted(os.listdir(BASE_DIR)):
        if dir_name.startswith("."):
            continue
        plugin_path = os.path.join(BASE_DIR, dir_name, PLUGIN_FILE)
        if not os.path.isfile(plugin_path):
            continue

        module = _load_plugin_module(dir_name, plugin_path)

        group = getattr(module, "GROUP", None)
        if not isinstance(group, str) or not group.strip():
            _emit({
                "error": "PLUGIN",
                "message": f"插件 {plugin_path} 未定义非空的 GROUP 字符串",
            })
        group = group.strip()

        register = getattr(module, "register", None)
        if not callable(register):
            _emit({
                "error": "PLUGIN",
                "message": f"插件 {plugin_path} 未提供 register(subparsers) 函数",
            })

        if group in seen:
            _emit({
                "error": "PLUGIN",
                "message": f"命令组 '{group}' 重复声明：{seen[group]} 与 {plugin_path}",
            })
        seen[group] = plugin_path

        group_parser = subparsers.add_parser(
            group,
            help=getattr(module, "HELP", f"{group} 命令组（插件）"),
        )
        group_sub = group_parser.add_subparsers(dest="action", metavar="<子命令>")
        group_sub.required = True
        register(group_sub)


# ---------------------------------------------------------------- 参数骨架

def build_parser():
    parser = argparse.ArgumentParser(
        prog="tlk",
        description="TotalLINK 命令行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  tlk env list\n"
            "  tlk env add \"测试环境\" --token \"tlk_...\" --url \"http://host:8088\"\n"
            "  tlk env use \"TotalLINK 开发环境\"\n"
            "  tlk auth verify\n"
            "  tlk call TMESCOM01 9 --script-type 0 --params-json '[\"\"]'\n"
            "  tlk tools search 报销"
        ),
    )
    subparsers = parser.add_subparsers(dest="group", metavar="<命令组>")

    # --- env
    env_parser = subparsers.add_parser("env", help="项目环境管理")
    env_sub = env_parser.add_subparsers(dest="action", metavar="<子命令>")
    env_sub.required = True

    p = env_sub.add_parser("list", help="列出所有项目，标记活跃项目")
    p.set_defaults(handler=cmd_env_list)

    p = env_sub.add_parser("add", help="新增或更新项目配置")
    p.add_argument("name", metavar="<项目名>")
    p.add_argument("--token", required=True, metavar="TOKEN", help="auth_token（tlk_ 开头）")
    p.add_argument("--url", metavar="URL", help=f"base_url（默认 {tlk_core.DEFAULT_BASE_URL}）")
    p.set_defaults(handler=cmd_env_add)

    p = env_sub.add_parser("use", help="切换活跃项目（精确匹配项目名）")
    p.add_argument("name", metavar="<项目名>")
    p.set_defaults(handler=cmd_env_use)

    # --- auth
    auth_parser = subparsers.add_parser("auth", help="认证与环境自检")
    auth_sub = auth_parser.add_subparsers(dest="action", metavar="<子命令>")
    auth_sub.required = True

    p = auth_sub.add_parser("verify", help="自检当前项目：项目 / URL / 用户 / 额度")
    p.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    p.set_defaults(handler=cmd_auth_verify)

    # --- call
    p = subparsers.add_parser("call", help="调用工具（POST linkDMAIAction）")
    p.add_argument("dm_code", metavar="dmCode", help="工具代码，如 TMESCOM01")
    p.add_argument("dm_num", metavar="dmNum", type=int, help="工具编号，如 9")
    p.add_argument("--script-type", type=int, required=True,
                   help="操作类型，取工具的 script_type 值（整数 0-4）")
    p.add_argument("--params-json", default="[]", metavar="JSON",
                   help="Para 参数数组（JSON 数组），空位传 \"\"，如 '[\"\",\"2026-06-18\"]'")
    p.add_argument("--row-data", type=json.loads, default={},
                   help="rowData JSON 字典（按工具说明按需传入）")
    p.add_argument("--table-data", type=json.loads, default=[],
                   help="tableData JSON 数组（按工具说明按需传入）")
    p.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    p.add_argument("--timeout", type=int, default=tlk_core.DEFAULT_TIMEOUT,
                   help=f"请求超时秒数（默认 {tlk_core.DEFAULT_TIMEOUT}，需大于服务端降速等待时间）")
    p.set_defaults(handler=cmd_call)

    # --- tools
    tools_parser = subparsers.add_parser("tools", help="工具发现")
    tools_sub = tools_parser.add_subparsers(dest="action", metavar="<子命令>")
    tools_sub.required = True

    p = tools_sub.add_parser("search", help="按关键字搜索可用工具（SEARCHLIST）")
    p.add_argument("keyword", metavar="<关键字>")
    p.add_argument("--project", help="指定项目名（不传则使用活跃项目）")
    p.set_defaults(handler=cmd_tools_search)

    # --- 插件组（目录缺席时自然消失）
    discover_plugins(subparsers)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    handler = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return

    handler(args)


if __name__ == "__main__":
    main()
