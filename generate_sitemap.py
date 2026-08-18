#!/usr/bin/env python3
"""
生成 sitemap.txt 腳本
用於 GitHub Pages 網站的 SEO 優化
使用純文本格式（URL + ISO 8601 時間戳）
"""

import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

def extract_date_from_filename(filename):
    """從檔名提取日期 (YYYY-MM-DD-xxx.md 格式)"""
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-', filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return datetime.now().strftime("%Y-%m-%d")

def generate_sitemap(site_url="https://thenewssamsam.github.io", posts_dir="_posts"):
    """
    生成 sitemap.txt（純文本格式）
    
    格式：URL + ISO 8601 時間戳（例如：https://example.com/page.html2026-08-17T14:43:32Z）
    
    Args:
        site_url: 網站 URL
        posts_dir: 文章目錄路徑
    """
    
    lines = []
    
    # 1. 主頁
    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append(f"{site_url}{now}")
    
    # 2. About 頁面
    lines.append(f"{urljoin(site_url, '/about.html')}{now}")
    
    # 3. 所有文章
    if os.path.exists(posts_dir):
        post_files = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md')], reverse=True)
        
        for post_file in post_files:
            # 從檔名提取日期
            date = extract_date_from_filename(post_file)
            
            # 生成 URL (Jekyll 格式：/news/YYYY/MM/DD/title.html)
            title = post_file.replace('.md', '').split('-', 3)[3]  # 移除日期部分
            url = urljoin(site_url, f'/news/{date.replace("-", "/")}/{title}.html')
            
            # 使用文章日期作為時間戳（設為當天中午）
            timestamp = f"{date}T12:00:00Z"
            lines.append(f"{url}{timestamp}")
    
    return '\n'.join(lines)

def save_sitemap(sitemap_content, output_file='sitemap.txt'):
    """儲存 sitemap.txt"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"✅ Sitemap 已生成：{output_file}")
    print(f"   URL 數量：{len(sitemap_content.splitlines())}")

if __name__ == "__main__":
    # 根據執行位置自動偵測
    script_dir = Path(__file__).parent.absolute()
    posts_dir = script_dir / '_posts'
    output_file = script_dir / 'sitemap.txt'
    
    sitemap = generate_sitemap(posts_dir=str(posts_dir))
    save_sitemap(sitemap, str(output_file))
    
    # 印出前 5 行預覽
    print("\n📄 Sitemap 預覽（前 5 行）：")
    lines = sitemap.splitlines()
    for i, line in enumerate(lines[:5], 1):
        print(f"{i}. {line}")
