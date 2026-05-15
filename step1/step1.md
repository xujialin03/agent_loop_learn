# 第 1 阶段：带上下文的对话（Chat Memory）

## 🎯 阶段目标

让模型能够"记住"之前的对话内容：

> **多轮对话 = 历史消息拼接**

这是从"单次调用"到"智能对话"的关键一步。

---

## 📋 本阶段内容

1. **理解上下文机制** - 什么是 Chat Memory
2. **实现对话历史** - 维护 messages 列表
3. **实践练习** - 创建多轮对话系统

---

## 🧠 核心概念

### 什么是 Chat Memory？

在单次调用中，我们只发送当前的用户输入：

```python
messages = [
    {"role": "user", "content": "你好"}
]
```

在多轮对话中，我们需要维护**完整的对话历史**：

```python
messages = [
    {"role": "user", "content": "我叫张三"},
    {"role": "assistant", "content": "你好，张三！很高兴认识你。"},
    {"role": "user", "content": "我叫什么名字？"}  # 模型需要记住之前的对话
]
```

### Messages 的结构

| Role | 说明 | 示例 |
|------|------|------|
| `system` | 系统提示，设定模型角色 | "你是一个有帮助的助手" |
| `user` | 用户输入 | "你好" |
| `assistant` | 模型回复 | "你好！有什么可以帮你？" |

---

## 🧩 核心实现

### 方案 A：使用配置文件（推荐）

```python
# step1_memory.py

import json
import requests
from pathlib import Path

# 加载配置
config_path = Path.cwd() / ".." / "config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

MODEL_CONFIG = config["model"]

# 初始化对话历史
conversation_history = []

def call_llm_with_history(prompt: str) -> str:
    """
    带上下文的 LLM 调用
    """
    # 将新的用户输入添加到历史
    conversation_history.append({"role": "user", "content": prompt})
    
    url = f"{MODEL_CONFIG['base_url']}/v1/chat/completions"
    
    payload = {
        "model": MODEL_CONFIG['name'],
        "messages": conversation_history,
        "temperature": MODEL_CONFIG.get('temperature', 0.7),
        "max_tokens": MODEL_CONFIG.get('max_tokens', 120000)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        
        # 将模型回复添加到历史
        conversation_history.append({"role": "assistant", "content": answer})
        
        return answer
    except Exception as e:
        return f"❌ 错误：{str(e)}"

if __name__ == "__main__":
    print("🤖 带上下文的聊天机器人（输入 'exit' 退出）")
    while True:
        user_input = input("👤 你：")
        if user_input.lower() == "exit":
            print("👋 再见！")
            break
        answer = call_llm_with_history(user_input)
        print(f"🤖 助手：{answer}\n")
```

### 方案 B：使用 OpenAI API

```python
# step1_openai.py

from openai import OpenAI

client = OpenAI()

# 初始化对话历史（包含系统提示）
conversation_history = [
    {"role": "system", "content": "你是一个有帮助的助手"}
]

def chat_with_history(prompt: str) -> str:
    conversation_history.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history
    )
    
    answer = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": answer})
    
    return answer

if __name__ == "__main__":
    print("🤖 带上下文的聊天机器人（输入 'exit' 退出）")
    while True:
        user_input = input("👤 你：")
        if user_input.lower() == "exit":
            print("👋 再见！")
            break
        answer = chat_with_history(user_input)
        print(f"🤖 助手：{answer}\n")
```

### 方案 C：使用 Ollama

```python
# step1_ollama.py

import requests

# 初始化对话历史
conversation_history = []

def chat_with_history(prompt: str) -> str:
    conversation_history.append({"role": "user", "content": prompt})
    
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3.2",
        "messages": conversation_history,
        "stream": False
    }
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    answer = result["message"]["content"]
    conversation_history.append({"role": "assistant", "content": answer})
    
    return answer

if __name__ == "__main__":
    print("🤖 带上下文的聊天机器人（输入 'exit' 退出）")
    while True:
        user_input = input("👤 你：")
        if user_input.lower() == "exit":
            print("👋 再见！")
            break
        answer = chat_with_history(user_input)
        print(f"🤖 助手：{answer}\n")
```

---

## 🔍 核心知识点

### 1. 对话历史管理

```python
# 初始状态
conversation_history = []

# 用户输入后
conversation_history.append({"role": "user", "content": "我叫张三"})

# 模型回复后
conversation_history.append({"role": "assistant", "content": "你好，张三！"})

# 最终状态
conversation_history = [
    {"role": "user", "content": "我叫张三"},
    {"role": "assistant", "content": "你好，张三！"}
]
```

### 2. Token 管理

随着对话进行，历史消息会越来越长，消耗的 token 也会增加：

```python
# 简单的历史截断策略
def trim_history(max_messages: int = 10):
    global conversation_history
    if len(conversation_history) > max_messages:
        # 保留最近的 max_messages 条消息
        conversation_history = conversation_history[-max_messages:]
```

### 3. 系统提示的作用

系统提示可以设定模型的行为和角色：

```python
conversation_history = [
    {"role": "system", "content": "你是一位专业的数学老师，请用简单易懂的方式解答问题"}
]
```

---

## ✅ 验证标准

运行程序，测试多轮对话：

```
🤖 带上下文的聊天机器人（输入 'exit' 退出）
👤 你：我叫张三
🤖 助手：你好，张三！很高兴认识你。

👤 你：我叫什么名字？
🤖 助手：你叫张三。

👤 你：exit
👋 再见！
```

---

## 🚧 常见错误排查

### 错误 1: 上下文丢失
```
Q: 我叫张三
A: 你好，张三！
Q: 我叫什么名字？
A: 抱歉，我不记得了。
```
**解决**: 确保每次调用都传递完整的 `conversation_history`

### 错误 2: Token 超限
```
Error: context_length_exceeded
```
**解决**: 实现历史截断机制

### 错误 3: 角色错误
```
Error: Invalid role: 'assistent'
```
**解决**: 检查 role 拼写，只能是 `system`、`user` 或 `assistant`

---

## 📝 练习题

1. **基础**: 修改代码，添加系统提示让模型扮演特定角色
2. **进阶**: 实现历史消息截断功能，限制最多保存 10 条消息
3. **挑战**: 添加对话保存/加载功能，可以保存聊天记录到文件

---

## 🔗 下一步

完成这个阶段后，进入 **[第 2 阶段：手动工具调用](../step2/step2.md)**，学习如何让模型使用工具。

> 👉 **重要提示**: 到这里，你只是一个"聊天机器人"，还不是真正的 Agent！
