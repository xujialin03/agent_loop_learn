#!/usr/bin/env python3
"""
模型测试脚本
用于验证模型配置是否正确，模型服务是否可访问
"""

import json
import os
import requests


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_model():
    """测试模型是否可用"""
    config = load_config()
    model_config = config["model"]

    print("=" * 50)
    print("🧪 模型配置测试")
    print("=" * 50)
    print(f"提供商：{model_config['provider']}")
    print(f"模型：{model_config['name']}")
    print(f"地址：{model_config['base_url']}")
    print(f"最大 token: {model_config['max_tokens']}")
    print("=" * 50)

    # 测试连接
    url = f"{model_config['base_url']}/v1/chat/completions"

    payload = {
        "model": model_config['name'],
        "messages": [{"role": "user", "content": "你好"}],
        "temperature": model_config.get('temperature', 0.7),
        "max_tokens": 100
    }

    print("\n📡 正在测试模型连接...\n")

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        print("✅ 测试成功！\n")
        print(f"Q: 你好")
        print(f"A: {answer}\n")
        print("=" * 50)
        print("🎉 模型配置正常，可以开始学习！")
        print("=" * 50)
        return True

    except requests.exceptions.ConnectionError:
        print("❌ 测试失败：无法连接到模型服务")
        print(f"   请确认 {model_config['base_url']} 已启动并可访问")
        return False

    except requests.exceptions.Timeout:
        print("❌ 测试失败：请求超时")
        print("   请检查网络连接或服务器状态")
        return False

    except Exception as e:
        print(f"❌ 测试失败：{str(e)}")
        return False


if __name__ == "__main__":
    success = test_model()
    exit(0 if success else 1)
