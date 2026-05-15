# 第 0 阶段：Hello World（单次调用）

## 🎯 阶段目标

理解最核心的概念：

> **LLM = 一个函数**

输入 → 调用模型 → 输出

这是所有 Agent 开发的起点。

---

## 📦 环境准备

### 1. 安装依赖

```bash
# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate

# 安装 OpenAI SDK（以 OpenAI 为例）
pip install openai
```

### 2. 获取 API Key

你需要一个 API Key：
- **OpenAI**: https://platform.openai.com/api-keys
- **其他提供商**: vLLM、Ollama、本地部署等

### 3. 设置环境变量

```bash
export OPENAI_API_KEY="你的 API_KEY"
```

---

## 🧩 核心实现

### 方案 A：使用 OpenAI API

```python
# step0_openai.py

from openai import OpenAI

# 初始化客户端
client = OpenAI(api_key="你的 API_KEY")  # 或从环境变量读取

# 定义 LLM 函数
def call_llm(prompt: str) -> str:
    """
    最简单的 LLM 调用
    输入：用户提示
    输出：模型回复
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 或 gpt-3.5-turbo
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 主程序
if __name__ == "__main__":
    user_input = input("Q: ")
    answer = call_llm(user_input)
    print(f"A: {answer}")
```

### 方案 B：使用 vLLM 本地模型

```python
# step0_vllm.py

import requests
import json

def call_llm(prompt: str) -> str:
    """
    调用本地 vLLM 服务
    假设 vLLM 运行在 http://localhost:8000
    """
    url = "http://localhost:8000/v1/chat/completions"
    
    payload = {
        "model": "your-model-name",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    return result["choices"][0]["message"]["content"]

if __name__ == "__main__":
    user_input = input("Q: ")
    answer = call_llm(user_input)
    print(f"A: {answer}")
```

### 方案 C：使用 Ollama（最简单）

```python
# step0_ollama.py

import requests

def call_llm(prompt: str) -> str:
    """
    调用本地 Ollama 服务
    假设 Ollama 运行在 http://localhost:11434
    """
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3.2",  # 或其他已下载的模型
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    return result["message"]["content"]

if __name__ == "__main__":
    user_input = input("Q: ")
    answer = call_llm(user_input)
    print(f"A: {answer}")
```

---

## 🔍 核心知识点

### 1. API 调用结构

```
请求 = {
    "model": "模型名称",
    "messages": [
        {"role": "user", "content": "输入"}
    ]
}

响应 = {
    "choices": [
        {"message": {"content": "输出"}}
    ]
}
```

### 2. Prompt 基础

- **简单提示**: 直接输入问题
- **系统提示**: 可以添加 system role 来设定角色
  ```python
  messages = [
      {"role": "system", "content": "你是一个助手"},
      {"role": "user", "content": "你好"}
  ]
  ```

### 3. 参数说明

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `temperature` | 创造性控制 | 0.7 |
| `max_tokens` | 最大输出长度 | 不限制 |
| `top_p` | 采样范围 | 1.0 |

---

## ✅ 验证标准

运行程序，应该看到：

```
Q: 你好
A: 你好！有什么可以帮你？
```

或者：

```
Q: 1+1 等于多少？
A: 1+1 等于 2。
```

---

## 🚧 常见错误排查

### 错误 1: API Key 无效
```
Error: Invalid API key
```
**解决**: 检查 `OPENAI_API_KEY` 是否正确设置

### 错误 2: 模型不存在
```
Error: Model not found
```
**解决**: 确认模型名称拼写，或更换可用模型

### 错误 3: 网络超时
```
Error: Connection timeout
```
**解决**: 检查网络连接，或使用本地模型

---

## 📝 练习题

1. **基础**: 修改代码，让模型以"诗人"的身份回答问题
2. **进阶**: 添加错误处理，当 API 调用失败时给出友好提示
3. **挑战**: 尝试用不同的模型（如 gpt-3.5-turbo vs gpt-4o-mini），比较输出差异

---

## 🔗 下一步

完成这个阶段后，进入 **[第 1 阶段：带上下文的对话](../step1/step1.md)**，让模型能够记住之前的对话内容。
