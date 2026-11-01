# GitHub Actions + Playwright 自动截图

本流程适用于源码托管在 GitHub、项目能够在 GitHub Actions Runner 中启动的 Web 软件。它解决云浏览器无法访问开发机 `localhost`、私有网络或本地运行环境的问题。

## 工作方式

1. GitHub Actions checkout 当前项目，在隔离 Runner 中安装项目依赖和 Playwright 浏览器。
2. Actions 启动真实软件服务，等待健康检查地址可访问。
3. Playwright 启动 Chromium，通过真实页面控件执行填写、点击、文件上传、导航和结果检查。
4. 每个核心页面在实际交互完成后保存 PNG，不通过 DOM 改写、伪造接口响应或静态 HTML 模拟页面。
5. 将原始截图保存到 `软件著作权申请资料/截图原始/`，将归档副本保存到 `软件著作权申请资料/截图/`。
6. 生成 `截图/截图清单.json`，记录 `method=playwright-github-actions`、页面顺序、图片路径和原始图片来源。
7. 通过 GitHub Actions artifact 保存运行日志和验收报告；在有仓库写权限时，将截图与清单提交回仓库。
8. 若已取得用户的 Markdown 确认，再按截图清单将 PNG 插入正式操作手册 Word。未确认 Markdown 时，只归档截图，不自动覆盖正式 Word。

## 工作流要求

- 工作流必须由 `workflow_dispatch` 或受控的 push 路径触发；避免截图文件本身触发无限循环。
- 对私有仓库使用最小权限。若需提交截图，显式配置 `permissions: contents: write`，并确保仓库策略允许 Actions 写入。
- 应固定 Python、项目依赖和 Playwright 版本范围；使用 `python -m playwright install --with-deps chromium` 安装浏览器及系统依赖。
- 服务只需绑定 Runner 本机地址，例如 `127.0.0.1`，不要为截图临时开放公网端口。
- 用健康检查等待服务就绪；记录 Streamlit stdout/stderr；无论成功或失败都上传诊断 artifact。
- 浏览器验收必须断言真实页面内容和操作结果。仅仅能打开首页或生成 PNG 不算页面验收通过。
- 对需要密钥的设置页面，只能使用明确标注的非真实演示值；不得把生产 API Key 写入脚本、日志、截图或仓库。
- 截图应有足够视口高度，确保关键表格、结果、图表和提示完整可见。若页面较长，可按不同区域分开截图。
- 截图需核验文件非空、PNG 文件头正确、文件大小合理，并与手册模块一一对应。

## 清单格式

项目工作流可以直接生成清单，格式如下：

```json
{
  "status": "ok",
  "method": "playwright-github-actions",
  "screenshots": [
    {
      "route": "单次评估",
      "url": "http://127.0.0.1:8501",
      "path": "项目/软件著作权申请资料/截图/01-单次评估.png",
      "source": "项目/软件著作权申请资料/截图原始/01-单次评估.png"
    }
  ],
  "errors": []
}
```

`path` 和 `source` 建议使用相对仓库根目录的路径，避免记录 GitHub Runner 临时绝对路径导致下次构建无法找到图片。清单状态只有在全部必需页面均通过操作断言且截图文件校验成功时才可写为 `ok`。

## 与操作手册和 Word 的衔接

- 按 `manual_modules` 和操作手册截图预留顺序组织图片。
- 截图必须对应真实页面和真实操作状态，不应为了凑数重复截取相同页面。
- 截图归档完成后，先由用户检查 Markdown 和图片；通过 `markdown` 门禁后再生成或刷新 Word。
- 如果截图未完成，继续保留 Word 中可见的截图预留文字，不得用空白图或示意图替代。
