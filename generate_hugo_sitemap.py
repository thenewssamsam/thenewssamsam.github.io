"""
生成 Hugo 風格的 Sitemap Index
將大量 URL 分成多個 sitemap 文件，避免單個文件過大
參考 Hugo 的 sitemap 方式
"""

import re
from datetime import datetime
from pathlib import Path

def extract_date_from_url(url):
    """從 URL 中提取日期"""
    date_match = re.search(r'/(\d{4})/(\d{2})/(\d{2})/', url)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month}-{day}"
    return datetime.now().strftime("%Y-%m-%d")

def generate_sitemap_file(urls, output_path, filename):
    """生成單個 sitemap 文件"""
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for url in urls:
        lastmod = extract_date_from_url(url)
        
        # 根據 URL 類型設置 priority 和 changefreq
        if url == 'https://thenewssamsam.github.io/':
            priority = '1.0'
            changefreq = 'daily'
        elif 'about.html' in url:
            priority = '0.8'
            changefreq = 'weekly'
        else:
            priority = '0.6'
            changefreq = 'monthly'
        
        xml_lines.append('  <url>')
        xml_lines.append(f'    <loc>{url}</loc>')
        xml_lines.append(f'    <lastmod>{lastmod}</lastmod>')
        xml_lines.append(f'    <changefreq>{changefreq}</changefreq>')
        xml_lines.append(f'    <priority>{priority}</priority>')
        xml_lines.append('  </url>')
    
    xml_lines.append('</urlset>')
    
    xml_content = '\n'.join(xml_lines)
    
    sitemap_path = output_path / filename
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return sitemap_path

def generate_sitemap_index(sitemap_files, output_path):
    """生成 sitemap index 文件"""
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_lines.append('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for sitemap_file in sitemap_files:
        # 計算文件 URL
        sitemap_url = f"https://thenewssamsam.github.io/{sitemap_file.name}"
        lastmod = datetime.now().strftime("%Y-%m-%d")
        
        xml_lines.append('  <sitemap>')
        xml_lines.append(f'    <loc>{sitemap_url}</loc>')
        xml_lines.append(f'    <lastmod>{lastmod}</lastmod>')
        xml_lines.append('  </sitemap>')
    
    xml_lines.append('</sitemapindex>')
    
    xml_content = '\n'.join(xml_lines)
    
    sitemap_index_path = output_path / 'sitemap.xml'
    with open(sitemap_index_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return sitemap_index_path

def main():
    """主程序"""
    sitemap_txt = "/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam/sitemap.txt"
    output_dir = Path("/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam")
    
    print("🚀 開始生成 Hugo 風格的 Sitemap Index...")
    
    # 讀取 sitemap.txt
    with open(sitemap_txt, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    print(f"📄 讀取到 {len(urls)} 個 URL")
    
    # 將 URL 分成多個文件（每個文件最多 1000 個 URL）
    max_urls_per_file = 1000
    sitemap_files = []
    
    for i in range(0, len(urls), max_urls_per_file):
        chunk = urls[i:i + max_urls_per_file]
        chunk_num = i // max_urls_per_file + 1
        filename = f'sitemap{chunk_num}.xml'
        
        print(f"   生成 {filename} ({len(chunk)} 個 URL)...")
        sitemap_file = generate_sitemap_file(chunk, output_dir, filename)
        sitemap_files.append(sitemap_file)
    
    # 生成 sitemap index
    print(f"\n📝 生成 sitemap index...")
    sitemap_index = generate_sitemap_index(sitemap_files, output_dir)
    
    print(f"\n✅ 完成!")
    print(f"   - Sitemap Index: {sitemap_index.name}")
    print(f"   - 子 sitemap 文件: {len(sitemap_files)} 個")
    
    for sitemap_file in sitemap_files:
        print(f"     - {sitemap_file.name}")
    
    print(f"\n💡 提示: 將 sitemap.xml 和 sitemap*.xml 提交到 GitHub")
    print(f"   cd /Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam")
    print(f"   git add sitemap.xml sitemap*.xml")
    print(f"   git commit -m 'Add Hugo-style sitemap index'")
    print(f"   git push")

if __name__ == "__main__":
    main()
