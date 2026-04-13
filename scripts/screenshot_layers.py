#!/usr/bin/env python3
"""
DeepPresenter 工作流 - Playwright 分层截图
对 HTML 页面进行分层截图：完整页、背景层、文字层
"""
import os
import argparse
from pathlib import Path


def screenshot_layers(slide_html: str, output_dir: str, viewport: tuple = (1280, 720)):
    """
    对单页 HTML 进行分层截图
    输出：
    - {name}_full.png    : 完整页面
    - {name}_bg.png      : 仅背景层
    """
    from playwright.sync_api import sync_playwright
    
    name = Path(slide_html).stem
    os.makedirs(output_dir, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': viewport[0], 'height': viewport[1]})
        
        page.goto(f'file://{os.path.abspath(slide_html)}')
        page.wait_for_load_state('networkidle')
        
        # Layer 1: 完整页面
        page.screenshot(
            path=os.path.join(output_dir, f'{name}_full.png'),
            full_page=False
        )
        
        # Layer 2: 隐藏文字层，仅保留背景
        page.evaluate('''
            () => {
                const content = document.querySelector('.content');
                if (content) content.style.display = 'none';
                const title = document.querySelector('.title');
                if (title) title.style.display = 'none';
                const points = document.querySelectorAll('.point-item, .points');
                points.forEach(p => p.style.display = 'none');
                const accent = document.querySelector('.accent-line');
                if (accent) accent.style.display = 'none';
            }
        ''')
        page.screenshot(
            path=os.path.join(output_dir, f'{name}_bg.png'),
            full_page=False
        )
        
        browser.close()
    
    return f'{name}_full.png', f'{name}_bg.png'


def batch_screenshot(slides_dir: str, output_dir: str, viewport: tuple = (1280, 720)):
    """批量处理所有 HTML 文件"""
    from playwright.sync_api import sync_playwright
    
    os.makedirs(output_dir, exist_ok=True)
    
    slide_files = sorted([
        f for f in os.listdir(slides_dir) 
        if f.endswith('.html')
    ])
    
    print(f'找到 {len(slide_files)} 个 HTML 文件')
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for slide_file in slide_files:
            slide_path = os.path.join(slides_dir, slide_file)
            name = Path(slide_file).stem
            
            page = browser.new_page(viewport={'width': viewport[0], 'height': viewport[1]})
            page.goto(f'file://{os.path.abspath(slide_path)}')
            page.wait_for_load_state('networkidle')
            
            # Full page
            page.screenshot(
                path=os.path.join(output_dir, f'{name}_full.png'),
                full_page=False
            )
            
            # Background only
            page.evaluate('''
                () => {
                    const content = document.querySelector('.content');
                    if (content) content.style.display = 'none';
                }
            ''')
            page.screenshot(
                path=os.path.join(output_dir, f'{name}_bg.png'),
                full_page=False
            )
            
            page.close()
            print(f'  已处理: {slide_file}')
        
        browser.close()
    
    print(f'截图完成: {output_dir}/')


def main():
    parser = argparse.ArgumentParser(description='Playwright 分层截图')
    parser.add_argument('--slides', '-s', required=True, help='HTML 文件目录')
    parser.add_argument('--output', '-o', default='screenshots', help='截图输出目录')
    parser.add_argument('--width', '-w', type=int, default=1280, help='页面宽度')
    parser.add_argument('--height', '-h', type=int, default=720, help='页面高度')
    args = parser.parse_args()
    
    batch_screenshot(args.slides, args.output, (args.width, args.height))


if __name__ == '__main__':
    exit(main())
