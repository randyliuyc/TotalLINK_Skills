#!/usr/bin/env python3
"""tlk_core / tlk 入口的回归测试（不联网）。

覆盖 2026-11-14 确认的三处行为：
  1. 显式 --project 未命中时不得回退到其它项目
  2. 配置文件固定 0600
  3. 配置文件缺 projects 键时不崩栈

pytest 可原样收集本文件；不装 pytest 时：
    python3 -m unittest discover tests
"""

import json
import os
import stat
import sys
import tempfile
import unittest
from argparse import Namespace
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import tlk_core  # noqa: E402


class ConfigFixture(unittest.TestCase):
    """把 tlk_core.CONFIG_PATH 指到临时目录，避免碰用户真实配置。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self._tmp.name, "config.json")
        self._patch = mock.patch.object(tlk_core, "CONFIG_PATH", self.config_path)
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._tmp.cleanup()

    def write_config(self, data):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)


class ProjectResolutionTest(ConfigFixture):
    def test_explicit_missing_project_reports_config(self):
        self.write_config({
            "active": "甲",
            "projects": {"甲": {"auth_token": "tlk_a", "base_url": "http://a:8088"}},
        })
        _, proj_cfg, error = tlk_core._resolve_project("乙")
        self.assertIsNone(proj_cfg)
        self.assertEqual(error["error"], "CONFIG")
        self.assertIn("乙", error["message"])

    def test_no_project_uses_active(self):
        self.write_config({
            "active": "甲",
            "projects": {
                "甲": {"auth_token": "tlk_a", "base_url": "http://a:8088"},
                "乙": {"auth_token": "tlk_b", "base_url": "http://b:8088"},
            },
        })
        key, proj_cfg, error = tlk_core._resolve_project(None)
        self.assertIsNone(error)
        self.assertEqual(key, "甲")
        self.assertEqual(proj_cfg["base_url"], "http://a:8088")

    def test_existing_project_wins_over_active(self):
        self.write_config({
            "active": "甲",
            "projects": {
                "甲": {"auth_token": "tlk_a", "base_url": "http://a:8088"},
                "乙": {"auth_token": "tlk_b", "base_url": "http://b:8088"},
            },
        })
        key, proj_cfg, error = tlk_core._resolve_project("乙")
        self.assertIsNone(error)
        self.assertEqual(key, "乙")

    def test_missing_config_reports_config(self):
        _, proj_cfg, error = tlk_core._resolve_project(None)
        self.assertIsNone(proj_cfg)
        self.assertEqual(error["error"], "CONFIG")


class ConfigFileTest(ConfigFixture):
    def test_save_config_is_0600(self):
        tlk_core.save_config({"active": "甲", "projects": {}})
        mode = stat.S_IMODE(os.stat(self.config_path).st_mode)
        self.assertEqual(mode, 0o600)

    def test_existing_0644_file_is_tightened(self):
        tlk_core.save_config({"active": "甲", "projects": {}})
        os.chmod(self.config_path, 0o644)
        tlk_core.save_config({"active": "乙", "projects": {}})
        mode = stat.S_IMODE(os.stat(self.config_path).st_mode)
        self.assertEqual(mode, 0o600)

    def test_add_project_tolerates_missing_projects_key(self):
        self.write_config({"active": "甲"})  # 手改坏的形态：没有 projects
        result = tlk_core.add_project("乙", "tlk_b", "http://b:8088")
        self.assertEqual(result["status"], "ok")
        cfg = tlk_core.load_all_config()
        self.assertIn("乙", cfg["projects"])

    def test_add_project_on_empty_config(self):
        result = tlk_core.add_project("甲", "tlk_a", "http://a:8088")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["active"], "甲")


class IsFalseTest(unittest.TestCase):
    """isSuccess 可能是字符串 "false"，也可能是布尔 false，两种都算失败。"""

    def test_string_false(self):
        self.assertTrue(tlk_core._is_false("false"))
        self.assertTrue(tlk_core._is_false(" FALSE "))

    def test_bool_false(self):
        self.assertTrue(tlk_core._is_false(False))

    def test_success_values(self):
        for value in ("true", "True", True, None, "", 1):
            with self.subTest(value=value):
                self.assertFalse(tlk_core._is_false(value))


class ParamsJsonTest(unittest.TestCase):
    def test_accepts_array(self):
        self.assertEqual(tlk_core.parse_params_json('["", "x"]'), ["", "x"])

    def test_rejects_non_array(self):
        with self.assertRaises(ValueError):
            tlk_core.parse_params_json('"x"')

    def test_rejects_bad_json(self):
        with self.assertRaises(ValueError):
            tlk_core.parse_params_json("{oops}")


class TokenResolutionTest(unittest.TestCase):
    """--token > --token-stdin > TOTALLINK_TOKEN，且 --token 行为不变。"""

    def setUp(self):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import tlk  # 导入不触发 build_parser，不会扫描插件
        self.tlk = tlk

    def test_token_wins(self):
        args = Namespace(token="tlk_cli", token_stdin=True)
        with mock.patch.dict(os.environ, {"TOTALLINK_TOKEN": "tlk_env"}):
            self.assertEqual(self.tlk._resolve_token(args), "tlk_cli")

    def test_stdin_path(self):
        args = Namespace(token=None, token_stdin=True)
        with mock.patch("sys.stdin", mock.MagicMock(readline=lambda: "tlk_stdin\n")):
            self.assertEqual(self.tlk._resolve_token(args), "tlk_stdin")

    def test_env_path(self):
        args = Namespace(token=None, token_stdin=False)
        with mock.patch.dict(os.environ, {"TOTALLINK_TOKEN": " tlk_env "}):
            self.assertEqual(self.tlk._resolve_token(args), "tlk_env")

    def test_empty_returns_empty(self):
        args = Namespace(token=None, token_stdin=False)
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.tlk._resolve_token(args), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
