# 第 3 阶段：结构化输出（Tool Calling 前置）

## 🎯 阶段目标

让模型输出"可解析的结构化数据"，而不仅仅是自然语言。

> **结构化输出 = JSON 格式 + 严格约束**

这是实现自动工具调用的关键前置技能。

---

## 📋 本阶段内容

1. **理解结构化输出** - 为什么需要 JSON 格式
2. **Prompt 工程** - 引导模型输出 JSON
3. **输出解析** - 验证和解析 JSON
4. **错误处理** - 处理格式错误

---

## 🧠 核心概念

### 为什么需要结构化输出？

在手动工具调用阶段，人类负责决定调用哪个工具。但真正的 Agent 需要：

1. **模型自己决定**调用什么工具
2. **模型输出指令**告诉程序如何调用
3. **程序解析指令**并执行工具

这就需要结构化输出：

```python
# 模型输出的结构化指令
{
  "action": "get_weather",
  "input": {"city": "北京"}
}
```

### 结构化输出格式

```json
{
  "thought": "用户问北京天气，我需要调用天气查询工具",
  "action": "get_weather",
  "params": {
    "city": "北京"
  }
}
```

---

## 🧩 核心实现

### 完整示例代码

```python
# step3_structured_output.py

import json
import requests
from pathlib import Path

# 加载配置
config_path = Path.cwd() / ".." / "config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

MODEL_CONFIG = config["model"]

def call_llm(messages: list) -> str:
    """调用 LLM 模型"""
    url = f"{MODEL_CONFIG['base_url']}/v1/chat/completions"
    
    payload = {
        "model": MODEL_CONFIG['name'],
        "messages": messages,
        "temperature": 0.0,  # 低温度保证输出稳定
        "max_tokens": MODEL_CONFIG.get('max_tokens', 200)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 错误：{str(e)}"

def extract_json(response: str) -> dict:
    """
    从模型响应中提取 JSON
    
    Args:
        response: 模型响应文本
        
    Returns:
        解析后的 JSON 对象，如果解析失败返回 None
    """
    try:
        # 尝试直接解析
        return json.loads(response)
    except json.JSONDecodeError:
        # 尝试查找 JSON 块
        import re
        # 匹配 { ... } 模式
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
        return None

def get_structured_output(user_input: str) -> dict:
    """
    获取模型的结构化输出
    
    Args:
        user_input: 用户输入
        
    Returns:
        结构化的工具调用指令
    """
    # 系统提示：强制输出 JSON 格式
    system_prompt = """
你是一个工具调用专家。请根据用户的问题，决定是否需要调用工具，并输出结构化的 JSON 响应。

可用工具：
1. get_weather(city): 获取指定城市的天气
2. calculate(expression): 数学计算
3. get_time(): 获取当前时间

输出格式（必须是有效的 JSON）：
{
  "thought": "你的思考过程",
  "action": "工具名称或 'finish' 如果不需要调用工具",
  "params": {"参数名": "参数值"}
}

示例：
用户：北京天气怎么样？
输出：
{
  "thought": "用户询问北京的天气，需要调用 get_weather 工具",
  "action": "get_weather",
  "params": {"city": "北京"}
}

用户：你好
输出：
{
  "thought": "用户只是打招呼，不需要调用工具",
  "action": "finish",
  "params": {}
}
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_input}
    ]
    
    response = call_llm(messages)
    print(f"📝 模型原始输出:\n{response}\n")
    
    # 解析 JSON
    structured_data = extract_json(response)
    
    if structured_data:
        print(f"✅ 成功解析结构化输出:")
        print(json.dumps(structured_data, indent=2, ensure_ascii=False))
        return structured_data
    else:
        print("❌ 无法解析结构化输出")
        return None

if __name__ == "__main__":
    # 测试示例
    test_cases = [
        "北京今天天气怎么样？",
        "1 + 2 等于多少？",
        "你好，我是张三",
        "现在几点了？"
    ]
    
    for question in test_cases:
        print(f"\n{'='*50}")
        print(f"👤 用户：{question}")
        get_structured_output(question)
```

---

## 🔍 核心知识点

### 1. Prompt 约束技巧

```python
system_prompt = """
你必须输出 JSON 格式，格式如下：
{
  "action": "...",
  "params": {...}
}
"""
```

### 2. JSON 解析方法

```python
def extract_json(text):
    # 方法1：直接解析
    try:
        return json.loads(text)
    except:
        pass
    
    # 方法2：正则提取
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    
    return None
```

### 3. 参数验证

```python
def validate_action(structured_data):
    required_fields = ["action", "params"]
    
    if not all(field in structured_data for field in required_fields):
        return False, "缺少必要字段"
    
    valid_actions = ["get_weather", "calculate", "get_time", "finish"]
    if structured_data["action"] not in valid_actions:
        return False, f"无效的 action: {structured_data['action']}"
    
    return True, "验证通过"
```

---

## ✅ 验证标准

运行程序，应该看到：

```
==================================================
👤 用户：北京今天天气怎么样？
📝 模型原始输出:
{"thought":"用户询问北京天气，需要调用get_weather工具","action":"get_weather","params":{"city":"北京"}}

✅ 成功解析结构化输出:
{
  "thought": "用户询问北京天气，需要调用get_weather工具",
  "action": "get_weather",
  "params": {
    "city": "北京"
  }
}
```

---

## 🚧 常见错误排查

### 错误 1: JSON 格式错误
```
输出：{action: "get_weather", params: {city: "北京"}}
```
**解决**: 在 prompt 中强调必须使用双引号

### 错误 2: 模型输出多余内容
```
输出：好的，我来查询天气。{"action": "get_weather"}
```
**解决**: 使用正则表达式提取 JSON 部分

---

## 📝 练习题

1. **基础**: 修改代码，添加更多工具（如股票查询）
2. **进阶**: 实现 JSON Schema 验证，确保输出符合预期格式
3. **挑战**: 添加重试机制，当 JSON 解析失败时要求模型重新输出

---

## 🔗 下一步

完成这个阶段后，进入 **[第 4 阶段：单步 Agent](../step4/step4.md)**，实现模型自动决定是否调用工具。
