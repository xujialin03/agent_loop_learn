# 第 2 阶段：手动工具调用（非 Agent）

## 🎯 阶段目标

让模型"间接"使用工具，但**由人类决定何时调用**。

> **工具调用 = 函数调用 + 结果注入**

这是学习 Agent 自动工具调用的重要铺垫。

---

## 📋 本阶段内容

1. **理解工具概念** - Tool = Python 函数
2. **创建工具函数** - 如天气查询、计算器
3. **手动调用流程** - 用户提问 → 人类判断 → 调用工具 → 喂给模型

---

## 🧠 核心概念

### 什么是工具？

在 AI Agent 中，工具就是可以被调用的 Python 函数：

```python
def get_weather(city: str) -> str:
    """获取指定城市的天气"""
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，25°C",
        "上海": "多云，23°C",
        "广州": "下雨，28°C"
    }
    return weather_data.get(city, "未知城市")
```

### 手动工具调用流程

```
用户：北京天气怎么样？
    ↓
人类：需要调用天气工具
    ↓
执行：get_weather("北京") → "晴天，25°C"
    ↓
人类：将结果告诉模型
    ↓
模型：根据天气信息生成回答
```

---

## 🧩 核心实现

### 完整示例代码

```python
# step2_manual_tool.py

import json
import requests
from pathlib import Path

# 加载配置
config_path = Path.cwd() / ".." / "config.json"
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

MODEL_CONFIG = config["model"]

# ========== 定义工具函数 ==========

def get_weather(city: str) -> str:
    """
    获取指定城市的天气
    
    Args:
        city: 城市名称
    
    Returns:
        天气描述
    """
    print(f"🔧 调用工具: get_weather({city})")
    
    # 模拟天气 API
    weather_database = {
        "北京": {"天气": "晴天", "温度": "25°C", "湿度": "45%"},
        "上海": {"天气": "多云", "温度": "23°C", "湿度": "60%"},
        "广州": {"天气": "小雨", "温度": "28°C", "湿度": "80%"},
        "深圳": {"天气": "阴天", "温度": "27°C", "湿度": "75%"},
        "杭州": {"天气": "晴转多云", "温度": "24°C", "湿度": "55%"}
    }
    
    if city in weather_database:
        data = weather_database[city]
        return f"{city}的天气：{data['天气']}，温度{data['温度']}，湿度{data['湿度']}"
    else:
        return f"抱歉，暂不支持查询{city}的天气"

def calculate(expression: str) -> str:
    """
    简单计算器
    
    Args:
        expression: 数学表达式，如 "2 + 3 * 4"
    
    Returns:
        计算结果
    """
    print(f"🔧 调用工具: calculate({expression})")
    
    try:
        # 安全计算，只允许基本运算
        allowed_chars = "0123456789+-*/(). "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"计算结果：{expression} = {result}"
        else:
            return "表达式包含非法字符"
    except Exception as e:
        return f"计算错误：{str(e)}"

def get_time() -> str:
    """
    获取当前时间
    
    Returns:
        当前时间字符串
    """
    print(f"🔧 调用工具: get_time()")
    
    from datetime import datetime
    now = datetime.now()
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"

# ========== LLM 调用函数 ==========

def call_llm(messages: list) -> str:
    """调用 LLM 模型"""
    url = f"{MODEL_CONFIG['base_url']}/v1/chat/completions"
    
    payload = {
        "model": MODEL_CONFIG['name'],
        "messages": messages,
        "temperature": MODEL_CONFIG.get('temperature', 0.7),
        "max_tokens": MODEL_CONFIG.get('max_tokens', 100)
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 错误：{str(e)}"

# ========== 手动工具调用逻辑 ==========

def manual_tool_call_demo():
    print("🤖 手动工具调用演示\n")
    
    # 示例 1：天气查询
    user_question = "北京今天天气怎么样？"
    print(f"👤 用户：{user_question}")
    
    # 人类判断需要调用天气工具
    tool_result = get_weather("北京")
    print(f"📊 工具结果：{tool_result}")
    
    # 将工具结果喂给模型
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": f"根据以下信息回答问题：\n{tool_result}\n\n问题：{user_question}"}
    ]
    
    answer = call_llm(messages)
    print(f"🤖 助手：{answer}\n")
    
    # 示例 2：数学计算
    user_question = "123 + 456 等于多少？"
    print(f"👤 用户：{user_question}")
    
    tool_result = calculate("123 + 456")
    print(f"📊 工具结果：{tool_result}")
    
    messages = [
        {"role": "user", "content": f"根据以下计算结果回答：\n{tool_result}\n\n问题：{user_question}"}
    ]
    
    answer = call_llm(messages)
    print(f"🤖 助手：{answer}\n")

if __name__ == "__main__":
    manual_tool_call_demo()
```

---

## 🔍 核心知识点

### 1. 工具定义模式

```python
def tool_name(参数1, 参数2):
    """工具描述"""
    # 执行操作
    return 结果
```

### 2. 工具调用流程

```python
# 1. 用户提问
question = "北京天气？"

# 2. 人类判断需要调用工具
if "天气" in question:
    # 3. 提取参数（城市名）
    city = "北京"
    # 4. 调用工具
    result = get_weather(city)
    # 5. 将结果喂给模型
    answer = call_llm(f"根据天气数据回答：{result}\n问题：{question}")
```

### 3. 工具类型

| 类型 | 示例 | 用途 |
|------|------|------|
| **信息查询** | 天气、新闻、股票 | 获取实时数据 |
| **计算工具** | 计算器、单位转换 | 精确计算 |
| **操作工具** | 文件读写、API调用 | 执行操作 |
| **搜索工具** | Web搜索、数据库查询 | 获取知识 |

---

## ✅ 验证标准

运行程序，应该看到：

```
🤖 手动工具调用演示

👤 用户：北京今天天气怎么样？
🔧 调用工具: get_weather(北京)
📊 工具结果：北京的天气：晴天，温度25°C，湿度45%
🤖 助手：北京今天是晴天，温度25°C，湿度45%。

👤 用户：123 + 456 等于多少？
🔧 调用工具: calculate(123 + 456)
📊 工具结果：计算结果：123 + 456 = 579
🤖 助手：123 + 456 等于 579。
```

---

## 🚧 常见错误排查

### 错误 1: 参数提取错误
```
问题："上海天气如何？"
错误提取：city = "天气"
```
**解决**: 使用更智能的参数提取方法

### 错误 2: 工具结果格式不清晰
```
工具返回：{"weather": "sunny", "temp": 25}
```
**解决**: 将工具结果转换为自然语言描述

---

## 📝 练习题

1. **基础**: 添加一个新工具 `get_stock_price(symbol)` 模拟获取股票价格
2. **进阶**: 创建一个工具选择器，根据用户问题自动选择合适的工具
3. **挑战**: 尝试将工具调用结果用自然语言包装后再喂给模型

---

## 🚨 重要提示

> **这还不是真正的 Agent！**
> 
> 在这个阶段，**人类**负责：
> - 判断是否需要调用工具
> - 选择调用哪个工具
> - 提取工具参数
> 
> 真正的 Agent 应该**自动**完成这些决策！

---

## 🔗 下一步

完成这个阶段后，进入 **[第 3 阶段：结构化输出](../step3/step3.md)**，学习如何让模型输出可解析的结构。
