# OfficeCLI DOCX 后端（可选）

## 定位与选择

OfficeCLI 是本 Skill 的可选 DOCX 自动生成、校验与预览后端，不是软件开发、项目分析、测试、业务理解或 Markdown 草稿撰写的前置条件。

启动环境检查时，如果 OfficeCLI 缺失或版本不匹配，只提示用户一次：

- 现在安装/切换到已验证版本，以便后续自动生成 Word；
- 跳过 OfficeCLI，继续完成软件工程、测试、业务理解和 Markdown/TXT 材料。

用户选择跳过时，不得停止工作流。正式材料阶段使用 `build_docx_from_md.py --text-only` 生成申请表 TXT 和生成报告；操作手册及代码材料 Markdown 保留在 `草稿/`，用户可以自行用 Word/WPS 排版。不得把 Markdown 伪装成 DOCX，不得声称完成 DOCX 校验或页数验证。

用户以后希望自动生成 Word 时，可以再安装 OfficeCLI 并重新执行环境检查。此前已确认的业务理解和 Markdown 内容不需要因为安装 OfficeCLI 而重新开发。

## 固定版本与边界

- 已验证版本：`1.0.151`。
- 官方发布页：https://github.com/iOfficeAI/OfficeCLI/releases/tag/v1.0.151
- 本仓库不复制 OfficeCLI 源码或二进制；OfficeCLI 继续按其 Apache-2.0 许可证独立分发。
- 只有用户选择自动 DOCX 生成时才要求全局安装；不下载到被分析项目、本 Skill 或输出目录。
- 运行时设置 `OFFICECLI_SKIP_UPDATE=1` 和 `OFFICECLI_NO_AUTO_RESIDENT=1`，避免版本漂移、后台文件锁和延迟落盘。
- 未选择 OfficeCLI 时，不自动改用 python-docx、Pandoc、.NET 或其他 DOCX 后端。

## 全局安装与检测

Windows PowerShell 使用官方安装命令：

```powershell
irm https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.ps1 | iex
```

macOS / Linux 使用官方安装命令：

```bash
curl -fsSL https://raw.githubusercontent.com/iOfficeAI/OfficeCLI/main/install.sh | bash
```

安装脚本会把 OfficeCLI 放入全局命令目录并更新 PATH。如果当前进程尚未识别更新后的 PATH，可重启 coding agent 后再运行：

```bash
officecli --version
# 预期输出：1.0.151
```

只从当前进程 PATH 查找全局 `officecli` / `officecli.exe`。不得使用 `OFFICECLI_PATH`、`--officecli` 或项目内二进制。当前版本不匹配时，可切换到固定版本；如用户明确接受兼容性风险，可显式传入 `--allow-untested-officecli`。

## 写入策略

只有在 OfficeCLI 可用且用户选择 DOCX 模式时执行：

- 每个 DOCX 先 `create --force --locale zh-CN`，再用一个原子 `batch --stop-on-error` 写入主要内容。
- A4、页边距、默认字体、黑色文字、页眉和页码写入文档，不依赖模板文件。
- 主要内容完成后读取 `/theme`，把 major/minor 的拉丁、东亚和复杂文字字体统一为 Times New Roman / SimSun，再通过 OfficeCLI `raw-set` 整体替换主题根节点。
- 页眉左侧为软件全称和版本号，右侧为 PAGE 字段。
- 代码材料不使用 Word 自动行号；所有代码段落连续写入正文，最终分页由 Word 排版引擎自动完成。
- 重新抽取或生成时清理同一软件名下与当前模式冲突的旧代码草稿和旧代码 DOCX。

## 校验策略

选择 DOCX 模式时：

1. `officecli validate <file> --json`：OpenXML 结构错误必须为 0。
2. 重新读取主题，确认字体槽符合要求。
3. `officecli view <file> issues --json`：内容/格式提示写入生成报告。
4. Windows 且安装 Microsoft Word 时，使用 `view stats --page-count --json` 检查实际分页。
5. 生成预览并用 Word/WPS 复核最终分页。

选择 text-only 模式时：

- 校验申请表 TXT 是否与已确认 Markdown 字段一致。
- 校验业务理解、操作手册和代码材料 Markdown 是否存在。
- 校验源代码材料能否回溯到用户确认的项目源码。
- 明确记录未生成 DOCX、未执行 OpenXML 校验、未验证 Word 分页。

## 常用命令

```bash
officecli --version
officecli validate output.docx --json
officecli view output.docx issues --json
officecli view output.docx stats --page-count --json
officecli view output.docx screenshot --grid auto --render auto -o preview.png
```
