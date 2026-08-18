#!/usr/bin/env python3
"""
生成 sitemap.xml 腳本
用於 GitHub Pages 網站的 SEO 優化
支援文章優先級、更新頻率等設定
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
    生成 sitemap.xml
    
    Args:
        site_url: 網站 URL
        posts_dir: 文章目錄路徑
    """
    
    entries = []
    
    # 1. 主頁
    entries.append({
        'loc': site_url,
        'lastmod': datetime.now().strftime("%Y-%m-%d"),
        'changefreq': 'daily',
        'priority': '1.0'
    })
    
    # 2. About 頁面
    entries.append({
        'loc': urljoin(site_url, '/about.html'),
        'lastmod': datetime.now().strftime("%Y-%m-%d"),
        'changefreq': 'monthly',
        'priority': '0.8'
    })
    
    # 3. 所有文章
    if os.path.exists(posts_dir):
        post_files = sorted([f for f in os.listdir(posts_dir) if f.endswith('.md')], reverse=True)
        
        for post_file in post_files:
            # 從檔名提取日期
            date = extract_date_from_filename(post_file)
            
            # 生成 URL (Jekyll 格式：/news/YYYY/MM/DD/title.html)
            title = post_file.replace('.md', '').split('-', 3)[3]  # 移除日期部分
            url = urljoin(site_url, f'/news/{date.replace("-", "/")}/{title}.html')
            
            entries.append({
                'loc': url,
                'lastmod': date,
                'changefreq': 'monthly',
                'priority': '0.7'
            })
    
    # 生成 XML
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    
    for entry in entries:
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{entry["loc"]}</loc>')
        xml_lines.append(f'    <lastmod>{entry["lastmod"]}</lastmod>')
        xml_lines.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
        xml_lines.append(f'    <priority>{entry["priority"]}</priority>')
        xml_lines.append('  </url>')
    
    xml_lines.append('</urlset>')
    
    return '\n'.join(xml_lines)

def save_sitemap(sitemap_content, output_file='sitemap.xml'):
    """儲存 sitemap.xml"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"✅ Sitemap 已生成：{output_file}")
    print(f"   內容行數：{len(sitemap_content.splitlines())}")

if __name__ == "__main__":
    # 根據執行位置自動偵測
    script_dir = Path(__file__).parent.absolute()
    posts_dir = script_dir / '_posts'
    output_file = script_dir / 'sitemap.xml'
    
    sitemap = generate_sitemap(posts_dir=str(posts_dir))
    save_sitemap(sitemap, str(output_file))
    
    # 印出前 500 字預覽
    print("\n📄 Sitemap 預覽（前 500 字）：")
    print(sitemap[:500] + "..." if len(sitemap) > 500 else sitemap)
