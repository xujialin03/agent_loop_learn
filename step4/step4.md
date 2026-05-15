# 第 4 阶段：单步 Agent（One-shot Tool Use）

## 🎯 阶段目标

让模型**自动决定**是否调用工具（但只调用一次）。

> **单步 Agent = 思考 + 行动**

这是实现完整 Agent Loop 的重要一步。

---

## 📋 本阶段内容

1. **理解单步 Agent** - 模型自己决定调用工具
2. **工具描述** - 告诉模型可用的工具
3. **执行流程** - 解析指令并执行工具
4. **结果汇总** - 将工具结果整理成自然语言回答

---

## 🧠 核心概念

### 单步 Agent 流程

```
用户输入 → LLM 判断 → 是否调用工具？
                        ↓
                    是 / 否
                    ↓
              执行工具 / 直接回答
                    ↓
              整理结果给用户
```

### 工具描述格式

```python
tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "city": {
                "type": "string",
                "description": "城市名称，如北京、上海"
            }
        }
    }
]
```

---

## 🧩 核心实现

### 完整示例代码

```python
# step4_one_shot_agent.py

import json
import requests
import re
from pathlib import Path

# 加载配置
config_path = Path.cwd() / ".." / "config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

MODEL_CONFIG = config["model"]

# ========== 工具定义 ==========

tools = [
    {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "city": {
                "type": "string",
                "description": "城市名称，如北京、上海"
            }
        }
    },
    {
        "name": "calculate",
        "description": "进行数学计算",
        "parameters": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '2 + 3 * 4'"
            }
        }
    },
    {
        "name": "get_time",
        "description": "获取当前时间",
        "parameters": {}
    }
]

def get_weather(city: str) -> str:
    """获取天气"""
    weather_database = {
        "北京": {"天气": "晴天", "温度": "25°C"},
        "上海": {"天气": "多云", "温度": "23°C"},
        "广州": {"天气": "小雨", "温度": "28°C"}
    }
    if city in weather_database:
        data = weather_database[city]
        return f"{city}的天气：{data['天气']}，温度{data['温度']}"
    return f"未知城市: {city}"

def calculate(expression: str) -> str:
    """计算器"""
    try:
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            return f"{expression} = {eval(expression)}"
        return "非法表达式"
    except:
        return "计算错误"

def get_time() -> str:
    """获取时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

# 工具映射
tool_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_time": get_time
}

# ========== LLM 调用 ==========

def call_llm(messages: list) -> str:
    """调用 LLM"""
    url = f"{MODEL_CONFIG['base_url']}/v1/chat/completions"
    payload = {
        "model": MODEL_CONFIG['name'],
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 200
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 错误：{str(e)}"

def extract_json(response: str) -> dict:
    """提取 JSON"""
    try:
        return json.loads(response)
    except:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
        return None

# ========== 单步 Agent 核心逻辑 ==========

def run_single_step_agent(user_input: str) -> str:
    """
    运行单步 Agent
    
    Args:
        user_input: 用户输入
        
    Returns:
        最终回答
    """
    # 构建工具描述
    tools_description = "\n".join([
        f"{i+1}. {tool['name']}: {tool['description']}"
        for i, tool in enumerate(tools)
    ])
    
    system_prompt = f"""
你是一个智能助手，可以使用工具来帮助回答问题。

可用工具：
{tools_description}

请输出结构化的 JSON 响应：
{{
  "thought": "你的思考过程",
  "action": "工具名称或 'finish'",
  "params": {{参数对象}}
}}

如果不需要工具，action 填 "finish"，params 为空对象。
"""
    
    # 第一步：获取模型的决策
    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_input}
    ]
    
    response = call_llm(messages)
    action = extract_json(response)
    
    if not action:
        return f"模型响应无法解析: {response}"
    
    print(f"🤔 思考: {action.get('thought', '')}")
    print(f"⚡ 行动: {action.get('action', '')}")
    
    # 第二步：执行工具或直接回答
    if action["action"] == "finish":
        # 不需要调用工具，直接生成回答
        return call_llm([{"role": "user", "content": user_input}])
    else:
        # 调用工具
        tool_name = action["action"]
        params = action.get("params", {})
        
        if tool_name not in tool_map:
            return f"未知工具: {tool_name}"
        
        # 调用工具
        tool_func = tool_map[tool_name]
        try:
            tool_result = tool_func(**params)
            print(f"🔧 工具结果: {tool_result}")
            
            # 第三步：用工具结果生成最终回答
            summary_prompt = f"""
根据以下工具执行结果，用自然语言回答用户问题：

工具结果：{tool_result}
用户问题：{user_input}
"""
            return call_llm([{"role": "user", "content": summary_prompt}])
        
        except Exception as e:
            return f"工具调用失败: {str(e)}"

if __name__ == "__main__":
    print("🤖 单步 Agent 演示\n")
    
    test_cases = [
        "北京今天天气怎么样？",
        "123 + 456 等于多少？",
        "你好，介绍一下你自己",
        "现在几点了？"
    ]
    
    for question in test_cases:
        print(f"\n{'='*50}")
        print(f"👤 用户：{question}")
        answer = run_single_step_agent(question)
        print(f"🤖 回答：{answer}")
```

---

## 🔍 核心知识点

### 1. 工具描述的重要性

```python
tools = [
    {
        "name": "工具名称",
        "description": "工具用途，越详细越好",
        "parameters": {
            "参数名": {
                "type": "类型",
                "description": "参数说明"
            }
        }
    }
]
```

### 2. 执行流程

```python
def run_agent(user_input):
    # 1. 获取模型决策
    action = get_structured_output(user_input)
    
    # 2. 判断是否调用工具
    if action["action"] == "finish":
        return direct_answer(user_input)
    
    # 3. 执行工具
    result = execute_tool(action["action"], action["params"])
    
    # 4. 总结回答
    return summarize(result, user_input)
```

---

## ✅ 验证标准

运行程序，应该看到：

```
==================================================
👤 用户：北京今天天气怎么样？
🤔 思考: 用户询问北京天气，需要调用 get_weather 工具
⚡ 行动: get_weather
🔧 工具结果: 北京的天气：晴天，温度25°C
🤖 回答：北京今天是晴天，温度25°C。
```

---

## 📝 练习题

1. **基础**: 添加更多工具（如日期转换、单位换算）
2. **进阶**: 实现工具参数的自动提取
3. **挑战**: 添加工具调用失败的重试机制

---

## 🔗 下一步

完成这个阶段后，进入 **[第 5 阶段：Agent Loop](../step5/step5.md)**，实现完整的思考-行动-观察循环。
