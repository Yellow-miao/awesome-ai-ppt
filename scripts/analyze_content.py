#!/usr/bin/env python3
"""
DeepPresenter 工作流 - 内容分析与大纲生成
读取知识库文档，调用 AI 生成 PPT 大纲
"""
import os
import glob
import argparse
from pathlib import Path


def read_knowledge_base(input_dir: str) -> str:
    """读取知识库所有文档"""
    content = []
    for ext in ['*.md', '*.txt']:
        for filepath in glob.glob(os.path.join(input_dir, ext)):
            with open(filepath, 'r', encoding='utf-8') as f:
                content.append(f"# {Path(filepath).stem}\n{f.read()}")
    return '\n\n'.join(content)


def generate_outline(content: str, api_endpoint: str, api_key: str, model: str = "gpt-4o") -> str:
    """
    调用 AI 分析内容，生成 PPT 大纲
    api_endpoint: API 端点，如 https://api.openai.com/v1/chat/completions
    api_key: 你的 API Key
    """
    import requests
    
    response = requests.post(
        api_endpoint,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'model': model,
            'messages': [
                {'role': 'system', 'content': '''你是一个 PPT 策划专家。
根据提供的知识库内容，生成一份 PPT 大纲。
格式要求：
- 10-20 页
- 每页有标题和 3-5 个要点
- 逻辑清晰，适合演示
- 输出格式：Markdown'''},
                {'role': 'user', 'content': content}
            ],
            'temperature': 0.7
        }
    )
    return response.json()['choices'][0]['message']['content']


def main():
    parser = argparse.ArgumentParser(description='知识库内容分析与大纲生成')
    parser.add_argument('--input', '-i', default='input', help='知识库目录')
    parser.add_argument('--output', '-o', default='output/outline.md', help='大纲输出路径')
    parser.add_argument('--api', default=os.getenv('TEXT_API_ENDPOINT'), help='API 端点')
    parser.add_argument('--key', default=os.getenv('TEXT_API_KEY'), help='API Key')
    parser.add_argument('--model', default='gpt-4o', help='模型名称')
    args = parser.parse_args()
    
    if not args.api or not args.key:
        print("错误：需要设置 TEXT_API_ENDPOINT 和 TEXT_API_KEY 环境变量')
        print('或使用 --api 和 --key 参数')
        return 1
    
    print(f'读取知识库: {args.input}')
    kb_content = read_knowledge_base(args.input)
    print(f'知识库大小: {len(kb_content)} 字符')
    
    print('生成大纲...')
    outline = generate_outline(kb_content, args.api, args.key, args.model)
    
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(outline)
    
    print(f'大纲已生成: {args.output}')
    return 0


if __name__ == '__main__':
    exit(main())
