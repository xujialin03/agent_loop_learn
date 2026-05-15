# 第 5 阶段：Agent Loop（核心突破）

## 🎯 阶段目标

实现真正的 Agent Loop：

> **思考 → 行动 → 观察 → 再思考**

这是从"单步工具调用"到"真正 Agent"的分水岭。

---

## 📋 本阶段内容

1. **理解 Agent Loop** - 核心循环机制
2. **实现循环控制** - while 循环 + max_steps
3. **中间状态记录** - 记录每一步的 thought、action、observation
4. **终止条件** - 决定何时结束循环

---

## 🧠 核心概念

### Agent Loop 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Loop                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Thought   │───▶│   Action    │───▶│   Execute   │     │
│  │   (思考)    │    │   (决定)    │    │   (执行)    │     │
│  └─────────────┘    └─────────────┘    └──────┬──────┘     │
│         ▲                                    │              │
│         │                                    │              │
│         │                                    ▼              │
│         │                           ┌─────────────┐         │
│         │                           │ Observation │         │
│         │                           │   (观察)    │         │
│         └───────────────────────────└─────────────┘         │
│                                                             │
│              ↓ 达到终止条件? ↓                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 循环状态

```python
agent_state = {
    "thought": "当前思考",
    "action": "工具名称或 finish",
    "params": {"参数"},
    "observation": "工具执行结果",
    "history": [  # 所有步骤的记录
        {"thought": "...", "action": "...", "observation": "..."},
        ...
    ]
}
```

---

## 🧩 核心实现

### 完整示例代码

```python
# step5_agent_loop.py

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
            "city": {"type": "string", "description": "城市名称"}
        }
    },
    {
        "name": "calculate",
        "description": "进行数学计算",
        "parameters": {
            "expression": {"type": "string", "description": "数学表达式"}
        }
    },
    {
        "name": "get_time",
        "description": "获取当前时间",
        "parameters": {}
    }
]

def get_weather(city: str) -> str:
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
    try:
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            return f"{expression} = {eval(expression)}"
        return "非法表达式"
    except:
        return "计算错误"

def get_time() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

tool_map = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_time": get_time
}

# ========== LLM 调用 ==========

def call_llm(messages: list) -> str:
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

# ========== Agent Loop 核心逻辑 ==========

def run_agent_loop(user_input: str, max_steps: int = 5) -> str:
    """
    运行完整的 Agent Loop
    
    Args:
        user_input: 用户输入
        max_steps: 最大循环次数（防死循环）
    
    Returns:
        最终回答
    """
    # 初始化状态
    history = []
    
    tools_description = "\n".join([
        f"{i+1}. {tool['name']}: {tool['description']}"
        for i, tool in enumerate(tools)
    ])
    
    system_prompt = f"""
你是一个智能助手，可以使用工具来回答问题。

可用工具：
{tools_description}

请输出结构化的 JSON 响应：
{{
  "thought": "你的思考过程",
  "action": "工具名称或 'finish'",
  "params": {{参数对象}}
}}

注意：
- 如果已经有足够信息回答用户问题，action 填 "finish"
- 如果需要继续调用工具获取更多信息，action 填工具名称
- params 必须是对象类型
"""
    
    print(f"🎯 用户问题: {user_input}")
    print("=" * 60)
    
    for step in range(max_steps):
        print(f"\n📋 步骤 {step + 1}/{max_steps}")
        
        # 构建历史信息
        history_summary = "\n".join([
            f"步骤 {i+1}: 思考={h['thought']}, 行动={h['action']}, 结果={h['observation']}"
            for i, h in enumerate(history)
        ])
        
        # 生成当前步骤的提示
        user_prompt = f"""
用户问题：{user_input}

历史记录：
{history_summary if history_summary else "无"}

请决定下一步行动。
"""
        
        # 第一步：思考并决定行动
        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_prompt.strip()}
        ]
        
        response = call_llm(messages)
        action = extract_json(response)
        
        if not action:
            return f"步骤 {step+1}: 无法解析模型响应"
        
        thought = action.get("thought", "")
        action_name = action.get("action", "")
        params = action.get("params", {})
        
        print(f"🤔 思考: {thought}")
        print(f"⚡ 行动: {action_name}")
        
        # 第二步：检查终止条件
        if action_name == "finish":
            print("🏁 循环结束")
            # 生成最终回答
            final_prompt = f"""
根据以下对话历史，总结回答用户问题：

用户问题：{user_input}

对话历史：
{history_summary if history_summary else "无"}

请用自然语言给出最终回答。
"""
            final_answer = call_llm([{"role": "user", "content": final_prompt}])
            return final_answer
        
        # 第三步：执行工具
        if action_name not in tool_map:
            observation = f"未知工具: {action_name}"
        else:
            try:
                tool_func = tool_map[action_name]
                observation = tool_func(**params)
            except Exception as e:
                observation = f"工具调用失败: {str(e)}"
        
        print(f"🔍 观察: {observation}")
        
        # 第四步：记录状态
        history.append({
            "thought": thought,
            "action": action_name,
            "observation": observation
        })
    
    # 达到最大步数
    return f"⚠️ 已达到最大步数 ({max_steps})，任务未完成"

if __name__ == "__main__":
    print("🤖 Agent Loop 演示\n")
    
    test_cases = [
        "北京今天天气怎么样？",
        "先查北京天气，再查上海天气，然后对比一下",
        "计算 100 + 200，然后告诉我结果"
    ]
    
    for question in test_cases:
        print(f"\n{'='*60}")
        print(f"👤 用户：{question}")
        print(f"{'='*60}")
        answer = run_agent_loop(question)
        print(f"\n🎉 最终回答：{answer}")
```

---

## 🔍 核心知识点

### 1. 循环控制

```python
def run_agent_loop(user_input, max_steps=5):
    for step in range(max_steps):
        # 思考 → 行动 → 观察
        action = think()
        
        if action == "finish":
            break
        
        observation = execute(action)
        record(observation)
```

### 2. 终止条件

| 条件 | 说明 |
|------|------|
| `action == "finish"` | 模型认为任务已完成 |
| `step >= max_steps` | 达到最大步数 |
| `error` | 发生错误 |

### 3. 状态记录

```python
history = [
    {
        "thought": "用户问天气，需要调用工具",
        "action": "get_weather",
        "observation": "北京天气：晴天，25°C"
    },
    ...
]
```

---

## ✅ 验证标准

运行程序，应该看到：

```
============================================================
👤 用户：先查北京天气，再查上海天气，然后对比一下
============================================================

📋 步骤 1/5
🤔 思考: 用户需要查询北京和上海的天气并对比，先查北京天气
⚡ 行动: get_weather
🔍 观察: 北京的天气：晴天，温度25°C

📋 步骤 2/5
🤔 思考: 已获取北京天气，现在需要查询上海天气
⚡ 行动: get_weather
🔍 观察: 上海的天气：多云，温度23°C

📋 步骤 3/5
🤔 思考: 已获取两个城市的天气，可以总结回答了
⚡ 行动: finish
🏁 循环结束

🎉 最终回答：北京今天是晴天，温度25°C；上海是多云，温度23°C。北京比上海温度稍高。
```

---

## 📝 练习题

1. **基础**: 添加更多工具，扩展 Agent 能力
2. **进阶**: 实现更智能的终止条件判断
3. **挑战**: 添加反思机制，让 Agent 可以回顾之前的步骤

---

## 🚨 重要里程碑

> **🎉 恭喜！到这里，你已经实现了真正的 Agent！**

你的 Agent 具备：
- ✅ 自主思考能力
- ✅ 工具调用能力
- ✅ 循环迭代能力
- ✅ 结果总结能力

---

## 🔗 下一步

完成这个阶段后，进入 **[第 6 阶段：模型做计划](../step6/step6.md)**，学习如何让 Agent 制定和执行计划。
