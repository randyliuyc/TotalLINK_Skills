#!/usr/bin/env python3
"""模型静态诊断的回归测试。

语料即 golden set：674→673 个真实语料应当全部 0 error
（2026-11-14 校准前有 5 个，其中 4 个是级别误判、1 个是损坏数据已删除）。

pytest 可原样收集本文件；不装 pytest 时也可直接跑：
    python3 -m unittest discover tests
"""

import glob
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "model-designer", "scripts"))

import validate_model  # noqa: E402

CORPUS_DIR = os.path.join(ROOT, "model-designer", "references", "samples-corpus")
# 2026-11-14 删除 1 个损坏语料（ModelSetting 为 0x7F）后的基线
CORPUS_BASELINE = 673


def corpus_files():
    return sorted(
        glob.glob(os.path.join(CORPUS_DIR, "**", "*.xml"), recursive=True)
    )


def errors_of(result):
    return [d for d in result.get("diagnostics", []) if d["severity"] == "error"]


def codes_of(result, severity=None):
    return [
        d["code"]
        for d in result.get("diagnostics", [])
        if severity is None or d["severity"] == severity
    ]


def validate_text(xml):
    """把 XML 文本写成临时文件后校验（validate_file 只接受路径）。"""
    fd, path = tempfile.mkstemp(suffix=".xml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(xml)
        return validate_model.validate_file(path)
    finally:
        os.unlink(path)


MINIMAL = """<SysDataModelXML>
  <ModelCode>TESTA01</ModelCode>
  <ModelNum>{num}</ModelNum>
  <ModelDesc>t</ModelDesc>
  <SysModelFlag>false</SysModelFlag>
  <ImageFile>#LINKRES#1</ImageFile>
  <MD5HASH></MD5HASH>
  {extra}
</SysDataModelXML>"""


class CorpusRegressionTest(unittest.TestCase):
    def test_corpus_not_empty(self):
        self.assertGreater(len(corpus_files()), 0, "语料目录为空")

    def test_corpus_count_matches_baseline(self):
        """语料数量变化应当是有意的：删/加语料时同步这个基线。"""
        self.assertEqual(len(corpus_files()), CORPUS_BASELINE)

    def test_no_error_on_real_corpus(self):
        for path in corpus_files():
            rel = os.path.relpath(path, ROOT)
            with self.subTest(corpus=rel):
                errs = errors_of(validate_model.validate_file(path))
                self.assertEqual(
                    errs, [], f"{rel} 出现 error 级诊断：{errs}"
                )


class RuleCalibrationTest(unittest.TestCase):
    """2026-11-14 与维护者逐条确认过的级别口径，改动需同步这里。"""

    def test_system_box_param_index_10_is_allowed(self):
        """{10} 是系统传入的调用方文本框内容，不是第 11 个用户参数。"""
        result = validate_text(
            MINIMAL.format(num=10, extra="<SQLScript>SELECT 1 WHERE A LIKE '%{10}%'</SQLScript>")
        )
        self.assertEqual(errors_of(result), [])
        self.assertNotIn("PARAM_INDEX_UNDEFINED", codes_of(result))

    def test_param_index_11_is_error(self):
        result = validate_text(
            MINIMAL.format(num=10, extra="<SQLScript>SELECT {11}</SQLScript>")
        )
        self.assertIn("PARAM_INDEX_UNDEFINED", codes_of(result, "error"))

    def test_unknown_para_type_is_info_not_error(self):
        """TEXTAREA / 字符型 等词表外取值：引擎不因此拒导入，只作提示。"""
        result = validate_text(
            MINIMAL.format(
                num=10,
                extra="<ParaLabel01>Scan</ParaLabel01><ParaType01>TEXTAREA</ParaType01>"
                      "<SQLScript>SELECT {0}</SQLScript>",
            )
        )
        self.assertIn("PARATYPE_ILLEGAL", codes_of(result, "info"))
        self.assertNotIn("PARATYPE_ILLEGAL", codes_of(result, "error"))

    def test_empty_cube_colname_is_warning_not_error(self):
        """空 COLNAME 条目无效，但语料里存在这种写法（模型标题行/设计器残留）。"""
        result = validate_text(
            MINIMAL.format(
                num=10,
                extra="<CubeSetting><DMCubeSetting>"
                      "<COLNAME></COLNAME><CAPTION>图片</CAPTION>"
                      "<COLTYPE>LANGUAGE-zh</COLTYPE>"
                      "</DMCubeSetting></CubeSetting>",
            )
        )
        self.assertIn("CUBE_COLNAME", codes_of(result, "warning"))
        self.assertNotIn("CUBE_COLNAME", codes_of(result, "error"))

    def test_sysmodel_flag_true_is_still_error(self):
        """硬规则不变：SysModelFlag=true 必须拦截。"""
        # 单独构造：MINIMAL 里已有 SysModelFlag，重复元素会掩盖本用例
        result = validate_text(
            "<SysDataModelXML>"
            "<ModelCode>TESTA01</ModelCode><ModelNum>10</ModelNum>"
            "<SysModelFlag>true</SysModelFlag>"
            "</SysDataModelXML>"
        )
        self.assertIn("SYSMODELFLAG", codes_of(result, "error"))

    def test_inline_flag_is_detected(self):
        """--LINKxxx 缀在语句行尾也要认出来（原先只扫行首）。"""
        result = validate_text(
            MINIMAL.format(
                num=10,
                extra="<SQLScript>SELECT 1 --LINKBADFLAG</SQLScript>",
            )
        )
        self.assertIn("FLAG_UNKNOWN", codes_of(result, "warning"))

    def test_inline_flag_wrong_field_is_detected(self):
        """行尾写法也要做「标记写错字段」判定。"""
        result = validate_text(
            MINIMAL.format(
                num=10,
                extra="<SQLUpdateScript>UPDATE T SET A=1 --LINKNOGROUP</SQLUpdateScript>",
            )
        )
        self.assertIn("FLAG_WRONG_FIELD", codes_of(result, "warning"))

    def test_bad_root_tag_is_error(self):
        result = validate_text("<NotAModel><ModelCode>X</ModelCode></NotAModel>")
        self.assertIn("ROOT_TAG", codes_of(result, "error"))

    def test_missing_file_returns_io_error(self):
        result = validate_model.validate_file(os.path.join(ROOT, "no-such-file.xml"))
        self.assertEqual(result.get("error"), "IO")


if __name__ == "__main__":
    unittest.main(verbosity=2)
