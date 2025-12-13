# Cherry 风格聊天桌面端（Python）

这个仓库提供一个基于 PySide6 的简易聊天客户端，界面参考 Cherry Studio，包含三栏布局、会话管理、带代码块复制按钮的聊天渲染，以及用于本地演示的模拟 LLM 后端。

## 功能特点
- **三栏界面**：水平分栏的会话列表、聊天区和配置面板。
- **会话管理**：支持新建、切换、重命名、删除会话，历史保存到 `data/sessions.json`。
- **聊天体验**：用户/助手气泡、基础 Markdown 解析，代码块等宽字体显示并可一键复制，新消息自动滚动到底部。
- **会话级配置**：每个会话保存 system prompt、temperature、max tokens，并支持自定义接口 URL、API Key 与模型名。
- **快速预设切换**：在配置面板中可一键选择常用模型预设，覆盖当前会话的接口与模型设置。
- **设置按钮**：通过右栏的「设置」按钮弹窗新增自定义模型预设（含 URL、Key、模型名），并以高亮按钮和图标强调可点状态。
- **模拟 LLM 后端**：`MockLLMClient` 使用流式生成器实现简单的回显响应，方便 UI 演示。

## 运行方式
可通过 `requirements.txt` 安装基础依赖（当前仅包含 PySide6）：

```bash
pip install -r requirements.txt
```

如需直接接入 Claude/其他 HTTP LLM，可额外安装对应 SDK 或 HTTP 客户端，例如：

```bash
pip install anthropic httpx
```

然后启动应用：

```bash
python main.py
```

若不存在历史数据，会自动创建一个默认会话。交互或关闭窗口时，会话会保存到 `data/sessions.json`。
