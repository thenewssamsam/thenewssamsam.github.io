#!/usr/bin/env python3
"""
生成 Sitemap 腳本（標準 sitemaps.org XML 格式 + 純文字備用）
用於 GitHub Pages 網站的 SEO 優化

輸出：
- sitemap.xml：標準 XML 格式（Google / Bing 優先讀取）
- sitemap.txt：純文字格式（備用，每行一個 URL）
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

def generate_entries(site_url="https://thenewssamsam.github.io", posts_dir="_posts"):
    """
    生成所有 sitemap 條目（不含外層標籤的內部資料）
    
    回傳 list of dict: [{'url': ..., 'lastmod': 'YYYY-MM-DD'}]
    """
    entries = []
    today = datetime.now().strftime("%Y-%m-%d")

    # 1. 主頁（優先級最高）
    entries.append({
        'url': site_url + '/',
        'lastmod': today,
        'changefreq': 'daily',
        'priority': '1.0',
    })

    # 2. About 頁面
    entries.append({
        'url': urljoin(site_url, '/about.html'),
        'lastmod': today,
        'changefreq': 'weekly',
        'priority': '0.8',
    })

    # 3. 所有文章
    if os.path.exists(posts_dir):
        post_files = sorted(
            [f for f in os.listdir(posts_dir) if f.endswith('.md')],
            reverse=True,
        )
        for post_file in post_files:
            date = extract_date_from_filename(post_file)
            # 生成 URL (Jekyll 格式：/news/YYYY/MM/DD/title.html)
            title = post_file.replace('.md', '').split('-', 3)[3]
            url = urljoin(site_url, f'/news/{date.replace("-", "/")}/{title}.html')

            entries.append({
                'url': url,
                'lastmod': date,
                'changefreq': 'monthly',
                'priority': '0.6',
            })

    return entries

def generate_sitemap_xml(site_url="https://thenewssamsam.github.io", posts_dir="_posts"):
    """
    生成標準 sitemap.xml（符合 sitemaps.org 規範）
    """
    entries = generate_entries(site_url, posts_dir)

    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_header += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml_footer = '</urlset>\n'

    url_blocks = []
    for e in entries:
        block = "  <url>\n"
        block += f"    <loc>{e['url']}</loc>\n"
        block += f"    <lastmod>{e['lastmod']}</lastmod>\n"
        block += f"    <changefreq>{e['changefreq']}</changefreq>\n"
        block += f"    <priority>{e['priority']}</priority>\n"
        block += "  </url>\n"
        url_blocks.append(block)

    return xml_header + ''.join(url_blocks) + xml_footer

def generate_sitemap_txt(site_url="https://thenewssamsam.github.io", posts_dir="_posts"):
    """
    生成純文字 sitemap.txt（每行一個 URL，作為備用）
    """
    entries = generate_entries(site_url, posts_dir)
    return '\n'.join(e['url'] for e in entries) + '\n'

def save_file(content, output_file):
    """儲存檔案"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已生成：{output_file}  ({len(content.splitlines())} 行)")

if __name__ == "__main__":
    script_dir = Path(__file__).parent.absolute()
    posts_dir = script_dir / '_posts'

    sitemap_xml = generate_sitemap_xml(posts_dir=str(posts_dir))
    sitemap_txt = generate_sitemap_txt(posts_dir=str(posts_dir))

    save_file(sitemap_xml, str(script_dir / 'sitemap.xml'))
    save_file(sitemap_txt, str(script_dir / 'sitemap.txt'))

    print("\n📄 sitemap.xml 預覽（前 5 個 URL）：")
    lines = sitemap_xml.splitlines()
    preview = [l for l in lines if '<loc>' in l][:5]
    for i, line in enumerate(preview, 1):
        # 去掉 <loc> 標籤以方便閱讀
        clean = line.replace('    <loc>', '').replace('</loc>', '')
        print(f"  {i}. {clean}")
