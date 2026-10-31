#!/usr/bin/env python3
"""Check Python and optional OfficeCLI capabilities before the workflow starts."""

from __future__ import annotations

import argparse
import platform
import sys
from pathlib import Path
from typing import Any

from common import ensure_dir, write_json
from officecli_backend import (
    OFFICECLI_DOWNLOAD_URL,
    OFFICECLI_INSTALL_COMMAND,
    TESTED_OFFICECLI_VERSION,
    OfficeCli,
    OfficeCliError,
    pending_windows_officecli_install,
    resolve_officecli,
)


def check_environment() -> dict[str, Any]:
    resolved = resolve_officecli()
    pending_install = pending_windows_officecli_install() if resolved is None else None
    version = "not found"
    error = ""
    if resolved:
        try:
            version = OfficeCli(require_tested_version=False).version
        except OfficeCliError as exc:
            error = str(exc)

    officecli_available = resolved is not None and not error
    tested_version = officecli_available and version == TESTED_OFFICECLI_VERSION
    if tested_version:
        next_action = "OfficeCLI 固定版本已就绪；如需自动生成 DOCX，可以选择使用。"
    elif pending_install:
        next_action = (
            "检测到 OfficeCLI 已安装到官方全局目录，但当前进程尚未获取更新后的 PATH。"
            "可以先跳过 Word 生成继续 Markdown 工作流；需要自动生成 DOCX 时再重启 coding agent 并重新检查。"
        )
    elif not officecli_available:
        next_action = (
            f"OfficeCLI 未就绪。可选安装命令：{OFFICECLI_INSTALL_COMMAND}。"
            "也可以跳过 OfficeCLI，继续软件开发、测试和 Markdown/TXT 材料整理。"
        )
    else:
        next_action = (
            f"当前 OfficeCLI 为 {version}，固定验证版本为 {TESTED_OFFICECLI_VERSION}。"
            "可以选择切换版本，也可以跳过自动 Word 生成，继续 Markdown/TXT 工作流。"
        )

    return {
        "output_directory": "当前目录/软件著作权申请资料",
        "capabilities": {
            "markdown_drafts": True,
            "application_txt": True,
            "officecli": officecli_available,
            "officecli_tested_version": tested_version,
            "docx_create": tested_version,
            "docx_openxml_validate": tested_version,
            "docx_preview": tested_version,
            "native_word_page_count_possible": platform.system() == "Windows",
        },
        "versions": {
            "python": platform.python_version(),
            "officecli": version,
            "officecli_required": TESTED_OFFICECLI_VERSION,
        },
        "paths": {"officecli": str(resolved) if resolved else ""},
        "officecli_install_state": "restart_required" if pending_install else ("ready" if resolved else "not_installed"),
        "final_docx_mode": "officecli" if tested_version else "text-only-available",
        "recommendation": (
            f"OfficeCLI {version} 已就绪；如选择 DOCX 模式，生成时禁用自动更新并使用原子 batch 写入。"
            if tested_version
            else f"OfficeCLI v{TESTED_OFFICECLI_VERSION} 是可选 DOCX 后端；当前不可用不影响软件开发、测试和 Markdown/TXT 草稿整理。"
        ),
        "install_prompt": (
            "OfficeCLI 固定验证版本可用；是否使用自动 DOCX 生成由用户决定。"
            if tested_version
            else (
                "OfficeCLI 已全局安装但当前进程可能需要刷新 PATH；可先跳过，之后需要 DOCX 时再重启并检查。"
                if pending_install
                else f"可选安装 OfficeCLI：{OFFICECLI_INSTALL_COMMAND}；发布页：{OFFICECLI_DOWNLOAD_URL}。也可跳过，后续需要 Word 时再安装。"
            )
        ),
        "requires_user_input": False,
        "confirmation_stage": None,
        "next_action": next_action,
        "officecli_error": error,
    }


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    caps = data["capabilities"]
    lines = [
        "# 软著申请资料生成环境检查",
        "",
        f"- 输出目录：`{data['output_directory']}`",
        f"- 最终 Word 模式：`{data['final_docx_mode']}`",
        f"- Python：`{data['versions']['python']}`",
        f"- OfficeCLI：`{data['versions']['officecli']}`（固定验证版本 `{data['versions']['officecli_required']}`）",
        f"- OfficeCLI 路径：`{data['paths']['officecli'] or '未找到'}`",
        f"- OfficeCLI 安装状态：`{data['officecli_install_state']}`",
        "",
        "## 能力状态",
        "",
        f"- Markdown 草稿：{'可用' if caps['markdown_drafts'] else '不可用'}",
        f"- 申请表 TXT：{'可用' if caps['application_txt'] else '不可用'}",
        f"- OfficeCLI DOCX 生成：{'可用' if caps['docx_create'] else '未就绪（可跳过）'}",
        f"- OpenXML 结构校验：{'可用' if caps['docx_openxml_validate'] else '未就绪（可跳过）'}",
        f"- DOCX 预览：{'可用' if caps['docx_preview'] else '未就绪（可跳过）'}",
        f"- Word 原生页数校验：{'可能可用' if caps['native_word_page_count_possible'] else '需在 Word/WPS 中人工复核'}",
        "",
        "## 建议",
        "",
        data["recommendation"],
        "",
        "## 可选提示",
        "",
        data["install_prompt"],
        "",
        data["next_action"],
        "",
        "OfficeCLI 缺失、需要重启或版本不匹配时，可以跳过并继续 Markdown/TXT 工作流；不得静默安装、升级或自动切换其他 DOCX 后端。",
        "",
    ]
    if data.get("officecli_error"):
        lines.extend(["## OfficeCLI 错误", "", "```text", data["officecli_error"], "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="软件著作权申请资料")
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
    out_dir = ensure_dir(Path(args.out_dir))
    data = check_environment()
    write_json(out_dir / "环境检查.json", data)
    write_markdown(out_dir / "环境检查.md", data)
    print(f"OK environment check: {out_dir}")
    print(f"Final DOCX mode: {data['final_docx_mode']}")
    print(data["recommendation"])
    if data.get("final_docx_mode") != "officecli":
        print("OPTIONAL_DOCX_BACKEND")
        print(f"OPTIONAL_NEXT_ACTION: {data['next_action']}")


if __name__ == "__main__":
    main()
