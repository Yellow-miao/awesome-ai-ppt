#!/usr/bin/env python3
"""
DeepPresenter 工作流 - HTML 设计稿生成
根据大纲生成带 CSS 样式的 HTML 文件
"""
import os
import re
import argparse
from pathlib import Path


SLIDE_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    width: 1280px; height: 720px;
    overflow: hidden; position: relative;
    background: linear-gradient(135deg, #0a1628 0%, #1a365d 100%);
  }}
  .slide {{
    width: 1280px; height: 720px; position: relative;
    display: flex; flex-direction: column; justify-content: center;
    padding: 60px 80px;
  }}
  .background-image {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background-size: cover; background-position: center; z-index: 0;
    opacity: 0.3;
  }}
  .overlay-mask {{
    position: absolute; top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(180deg, rgba(10,22,40,0.4) 0%, rgba(26,54,93,0.6) 100%);
    z-index: 1;
  }}
  .content {{
    position: relative; z-index: 2;
    max-width: 1100px;
  }}
  .slide-number {{
    position: absolute; bottom: 30px; right: 40px;
    font-size: 14px; color: rgba(255,255,255,0.5);
    z-index: 3;
  }}
  .title {{
    font-size: 48px; font-weight: bold; color: #FFFFFF;
    margin-bottom: 40px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
  }}
  .points {{
    font-size: 22px; color: rgba(255,255,255,0.9);
    line-height: 1.8;
  }}
  .point-item {{
    margin-bottom: 16px; padding-left: 30px;
    position: relative;
  }}
  .point-item::before {{
    content: "▸";
    position: absolute; left: 0; color: #00D5FF;
  }}
  .accent-line {{
    width: 60px; height: 4px;
    background: linear-gradient(90deg, #00D5FF, #0066FF);
    margin-bottom: 20px;
    border-radius: 2px;
  }}
</style>
</head>
<body>
<div class="slide">
  <div class="background-image" style="background-image: url('{bg_image}');"></div>
  <div class="overlay-mask"></div>
  <div class="content">
    <div class="accent-line"></div>
    <h1 class="title">{title}</h1>
    <div class="points">
{points}
    </div>
  </div>
  <div class="slide-number">{slide_num}</div>
</div>
</body>
</html>
'''


def parse_outline(outline_path: str) -> list:
    """解析大纲文件，返回 [(title, [points]), ...]"""
    with open(outline_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    slides = []
    current_title = ''
    current_points = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            if current_title:
                slides.append((current_title, current_points))
            current_title = line.lstrip('#').strip()
            current_points = []
        elif line.startswith(('•', '-', '·', '▸', '►')):
            point = line.lstrip('•-·▸►').strip()
            current_points.append(point)
        elif re.match(r'^\d+[.)、]', line):
            point = re.sub(r'^\d+[.)、]\s*', '', line)
            current_points.append(point)
    
    if current_title:
        slides.append((current_title, current_points))
    
    return slides


def generate_html_slides(slides: list, output_dir: str, bg_image: str = ''):
    """生成 HTML 文件"""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'images'), exist_ok=True)
    
    for i, (title, points) in enumerate(slides):
        points_html = '\n'.join(
            f'      <div class="point-item">{p}</div>' for p in points
        )
        
        html = SLIDE_TEMPLATE.format(
            title=title,
            points=points_html,
            bg_image=bg_image or '../images/default-bg.jpg',
            slide_num=f'{i+1}/{len(slides)}'
        )
        
        filename = f'slide_{i+1:02d}.html'
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(html)
    
    return len(slides)


def main():
    parser = argparse.ArgumentParser(description='生成 HTML 设计稿')
    parser.add_argument('--outline', '-i', required=True, help='大纲文件路径')
    parser.add_argument('--output', '-o', default='slides', help='输出目录')
    parser.add_argument('--bg', default='', help='背景图路径')
    args = parser.parse_args()
    
    print(f'解析大纲: {args.outline}')
    slides = parse_outline(args.outline)
    print(f'解析到 {len(slides)} 页')
    
    count = generate_html_slides(slides, args.output, args.bg)
    print(f'生成了 {count} 页 HTML 设计稿: {args.output}/')


if __name__ == '__main__':
    exit(main())
