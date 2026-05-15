# 第 6 阶段：模型做计划（Planning）

## 🎯 阶段目标

让模型学会"先思考再行动"，制定详细的执行计划。

> **计划 + 执行 = 复杂任务解决**

这是让 Agent 具备"远见"和"策略思维"的关键。

---

## 📋 本阶段内容

1. **理解计划机制** - 任务分解与规划
2. **实现计划生成** - 让模型输出执行步骤
3. **计划执行** - 按计划逐步执行
4. **计划修正** - 根据执行结果调整计划

---

## 🧠 核心概念

### 计划驱动的 Agent

```
用户任务 → 生成计划 → 执行步骤1 → 执行步骤2 → ... → 总结
              ↓                    ↑
              └────────────────────┘
                 动态修正计划
```

### 计划格式

```json
{
  "plan": [
    {"step": 1, "action": "get_weather", "params": {"city": "北京"}, "reason": "获取北京天气"},
    {"step": 2, "action": "get_weather", "params": {"city": "上海"}, "reason": "获取上海天气"},
    {"step": 3, "action": "finish", "params": {}, "reason": "总结对比结果"}
  ]
}
```

---

## 🧩 核心实现

### 完整示例代码

```python
# step6_planning_agent.py

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
        "parameters": {"city": {"type": "string", "description": "城市名称"}}
    },
    {
        "name": "calculate",
        "description": "进行数学计算",
        "parameters": {"expression": {"type": "string", "description": "数学表达式"}}
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
        "max_tokens": 300
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

# ========== 计划生成 ==========

def generate_plan(user_input: str) -> list:
    """
    生成执行计划
    
    Args:
        user_input: 用户任务
        
    Returns:
        计划步骤列表
    """
    tools_description = "\n".join([
        f"{i+1}. {tool['name']}: {tool['description']}"
        for i, tool in enumerate(tools)
    ])
    
    system_prompt = f"""
你是一个智能规划师。请根据用户的任务，制定详细的执行计划。

可用工具：
{tools_description}

请输出结构化的 JSON 响应：
{{
  "plan": [
    {{"step": 步骤号, "action": "工具名称或 'finish'", "params": {{参数对象}}, "reason": "理由"}},
    ...
  ]
}}

注意：
- 如果不需要工具，直接用 "finish" 总结即可
- 每个步骤应该有明确的目的
"""
    
    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_input}
    ]
    
    response = call_llm(messages)
    result = extract_json(response)
    
    if result and "plan" in result:
        return result["plan"]
    return None

# ========== 计划执行 ==========

def execute_plan(plan: list) -> str:
    """
    执行计划
    
    Args:
        plan: 计划步骤列表
        
    Returns:
        最终结果
    """
    execution_history = []
    
    print("📋 执行计划：")
    for i, step in enumerate(plan):
        step_num = step.get("step", i+1)
        action = step.get("action", "")
        params = step.get("params", {})
        reason = step.get("reason", "")
        
        print(f"\n📍 步骤 {step_num}: {action}")
        print(f"   理由: {reason}")
        
        if action == "finish":
            print("🏁 计划执行完成")
            break
            
        if action not in tool_map:
            print(f"❌ 未知工具: {action}")
            execution_history.append(f"步骤 {step_num}: 未知工具 {action}")
            continue
            
        try:
            tool_func = tool_map[action]
            result = tool_func(**params)
            print(f"✅ 结果: {result}")
            execution_history.append(f"步骤 {step_num}: {action} -> {result}")
        except Exception as e:
            print(f"❌ 执行失败: {str(e)}")
            execution_history.append(f"步骤 {step_num}: {action} -> 失败: {str(e)}")
    
    # 总结
    summary = "\n".join(execution_history)
    final_prompt = f"""
根据以下执行历史，总结回答用户问题：

执行历史：
{summary}

请用自然语言给出最终总结。
"""
    
    return call_llm([{"role": "user", "content": final_prompt}])

# ========== 主函数 ==========

def run_planning_agent(user_input: str) -> str:
    """
    运行计划驱动的 Agent
    
    Args:
        user_input: 用户任务
        
    Returns:
        最终回答
    """
    print(f"🎯 用户任务: {user_input}")
    print("=" * 60)
    
    # 生成计划
    print("\n🧠 正在生成计划...")
    plan = generate_plan(user_input)
    
    if not plan:
        return "无法生成计划"
    
    print("✅ 计划生成成功：")
    for step in plan:
        print(f"   [{step['step']}] {step['action']} - {step['reason']}")
    
    # 执行计划
    print("\n🚀 正在执行计划...")
    result = execute_plan(plan)
    
    return result

if __name__ == "__main__":
    print("🤖 计划驱动的 Agent 演示\n")
    
    test_cases = [
        "帮我查询北京和上海的天气，然后对比一下哪个城市更适合旅游",
        "计算 100 + 200，然后乘以 3，最后告诉我结果",
        "先告诉我现在几点，再查一下北京天气"
    ]
    
    for task in test_cases:
        print(f"\n{'='*60}")
        print(f"👤 用户：{task}")
        print(f"{'='*60}")
        answer = run_planning_agent(task)
        print(f"\n🎉 最终回答：{answer}")
```

---

## 🔍 核心知识点

### 1. 计划生成

```python
def generate_plan(user_input):
    # 提示模型输出结构化的计划
    system_prompt = """
请输出执行计划：
{
  "plan": [
    {"step": 1, "action": "...", "params": {...}, "reason": "..."},
    ...
  ]
}
"""
    # 调用模型生成计划
```

### 2. 计划执行

```python
def execute_plan(plan):
    for step in plan:
        action = step["action"]
        params = step["params"]
        
        if action == "finish":
            break
            
        # 执行工具
        result = tool_map[action](**params)
        
        # 记录结果
```

### 3. 计划修正

```python
# 可以在执行过程中动态调整计划
if execution_failed:
    # 请求模型修正计划
    revised_plan = revise_plan(original_plan, error_info)
```

---

## ✅ 验证标准

运行程序，应该看到：

```
============================================================
👤 用户：帮我查询北京和上海的天气，然后对比一下哪个城市更适合旅游
============================================================

🧠 正在生成计划...
✅ 计划生成成功：
   [1] get_weather - 查询北京天气
   [2] get_weather - 查询上海天气
   [3] finish - 总结对比结果

🚀 正在执行计划...
📋 执行计划：

📍 步骤 1: get_weather
   理由: 查询北京天气
✅ 结果: 北京的天气：晴天，温度25°C

📍 步骤 2: get_weather
   理由: 查询上海天气
✅ 结果: 上海的天气：多云，温度23°C

📍 步骤 3: finish
   理由: 总结对比结果
🏁 计划执行完成

🎉 最终回答：北京今天是晴天，温度25°C；上海是多云，温度23°C。北京天气更好，更适合旅游。
```

---

## 📝 练习题

1. **基础**: 添加计划可视化功能，用图表展示计划步骤
2. **进阶**: 实现计划修正机制，当步骤失败时自动调整
3. **挑战**: 实现多任务并行规划

---

## 🎉 学习完成

你已经完成了完整的 Agent 开发学习路线！

| 阶段 | 能力 |
|------|------|
| 第0阶段 | 单次调用 |
| 第1阶段 | 上下文对话 |
| 第2阶段 | 手动工具调用 |
| 第3阶段 | 结构化输出 |
| 第4阶段 | 单步工具调用 |
| 第5阶段 | Agent Loop |
| 第6阶段 | 计划能力 |

你的 Agent 现在具备：
- ✅ 自主思考
- ✅ 工具使用
- ✅ 循环迭代
- ✅ 计划制定
- ✅ 结果总结

---

## 🚀 下一步

尝试扩展你的 Agent：
1. 添加更多实用工具（搜索、数据库查询等）
2. 接入真实的 API（天气 API、新闻 API 等）
3. 实现更复杂的决策逻辑
4. 学习使用 LangChain、AutoGPT 等框架
