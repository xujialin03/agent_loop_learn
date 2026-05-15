# Agent Loop 开发学习项目

一个从入门到精通的 Agent 开发学习路线，通过实践掌握 LLM Agent 的核心技术。

## 🎯 学习目标

通过本项目，你将学会：

- ✅ LLM 的基本调用方式
- ✅ 带上下文的多轮对话
- ✅ 工具调用机制
- ✅ 结构化输出（JSON）
- ✅ 单步 Agent 实现
- ✅ Agent Loop（思考-行动-观察循环）
- ✅ 模型做计划（Planning）

## 📚 学习路线

| 阶段 | 名称 | 核心能力 | 文件 |
|------|------|----------|------|
| **第0阶段** | Hello World | 单次 LLM 调用 | `step0/` |
| **第1阶段** | Chat Memory | 上下文对话 | `step1/` |
| **第2阶段** | 手动工具调用 | 理解工具概念 | `step2/` |
| **第3阶段** | 结构化输出 | JSON 格式输出 | `step3/` |
| **第4阶段** | 单步 Agent | 自动决定调用工具 | `step4/` |
| **第5阶段** | Agent Loop | **核心突破**：思考→行动→观察循环 | `step5/` |
| **第6阶段** | 模型做计划 | Planning 能力 | `step6/` |

## 🛠️ 环境要求

### 模型配置

你需要配置一个兼容 OpenAI API 的模型服务：

- **本地部署**：vLLM / Ollama / llama.cpp 等
- **远程服务**：OpenAI API / 其他兼容服务

### 配置文件

在项目根目录创建 `config.json`：

```json
{
  "model": {
    "provider": "vllm",
    "name": "qwen3.5-122b",
    "base_url": "http://localhost:8000",
    "max_tokens": 120000,
    "temperature": 0.7
  }
}
```

### 依赖安装

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install requests ipython
```

## 🚀 开始学习

按照以下顺序学习：

1. **阅读总览**：`learn.md` - 了解完整学习路线
2. **按阶段学习**：从 `step0/` 到 `step6/`
3. **运行 Notebook**：每个阶段包含 `.ipynb` 和 `.md` 文件

```bash
# 启动 Jupyter Notebook
jupyter notebook

# 或使用 VS Code 打开 .ipynb 文件
```

## 📁 项目结构

```
agent_loop_learn/
├── README.md          # 项目介绍
├── learn.md           # 学习路线总览
├── config.json        # 模型配置
├── test_model.py      # 模型测试脚本
├── step0/             # 第0阶段：单次调用
│   ├── step0.ipynb
│   └── step0.md
├── step1/             # 第1阶段：上下文对话
│   ├── step1.ipynb
│   └── step1.md
├── step2/             # 第2阶段：手动工具调用
│   ├── step2.ipynb
│   └── step2.md
├── step3/             # 第3阶段：结构化输出
│   ├── step3.ipynb
│   └── step3.md
├── step4/             # 第4阶段：单步 Agent
│   ├── step4.ipynb
│   └── step4.md
├── step5/             # 第5阶段：Agent Loop
│   ├── step5.ipynb
│   └── step5.md
└── step6/             # 第6阶段：模型做计划
    ├── step6.ipynb
    └── step6.md
```

## 🧪 测试模型

```bash
python test_model.py
```

确保输出类似：
```
✅ 模型配置正常！
模型名称: qwen3.5-122b
响应时间: 1.23 秒
响应内容: 你好！我是一个智能助手...
```

## 💡 学习建议

1. **循序渐进**：从 step0 开始，逐步深入
2. **动手实践**：运行每个 Notebook，观察输出
3. **修改代码**：尝试修改参数，观察变化
4. **扩展功能**：添加新工具，扩展 Agent 能力

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

> 🎉 **祝你学习愉快！**
