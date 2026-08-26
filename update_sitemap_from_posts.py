#!/usr/bin/env python3
"""
從 _posts 目錄重新生成 sitemap.txt
確保所有現有文章都在 sitemap 中
"""
import os
from pathlib import Path
from datetime import datetime

def generate_url_from_filename(filename):
    """從文件名生成 URL"""
    if filename.startswith('2026-'):
        parts = filename.replace('.md', '').split('-')
        if len(parts) >= 4:
            year, month, day = parts[0], parts[1], parts[2]
            title = '-'.join(parts[3:])
            # 移除結尾的連字符
            title = title.rstrip('-')
            return f"https://johnthenews.netlify.app/{year}/{month}/{day}/{title}.html"
    return None

def main():
    posts_dir = Path("/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam/_posts")
    sitemap_path = Path("/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam/sitemap.txt")
    
    print("🚀 從 _posts 目錄重新生成 sitemap.txt...")
    
    # 讀取現有 sitemap (保留主頁和靜態頁面)
    existing_urls = set()
    if sitemap_path.exists():
        with open(sitemap_path, 'r', encoding='utf-8') as f:
            for line in f:
                url = line.strip()
                if url and not url.startswith('#'):
                    existing_urls.add(url)
    
    # 遍歷所有 markdown 文件
    all_urls = []
    post_count = 0
    
    for md_file in sorted(posts_dir.glob("*.md")):
        url = generate_url_from_filename(md_file.name)
        if url:
            all_urls.append(url)
            post_count += 1
    
    print(f"📄 找到 {post_count} 個文章文件")
    
    # 添加主頁和靜態頁面
    static_urls = [
        "https://johnthenews.netlify.app/",
        "https://johnthenews.netlify.app/about.html"
    ]
    
    # 合併所有 URL
    final_urls = static_urls + all_urls
    
    # 寫入 sitemap.txt
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        for url in final_urls:
            f.write(url + '\n')
    
    print(f"✅ 已生成 {len(final_urls)} 個 URL 到 sitemap.txt")
    print(f"   - 靜態頁面: {len(static_urls)}")
    print(f"   - 文章頁面: {post_count}")
    
    print(f"\n💡 下一步:")
    print(f"   cd /Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam")
    print(f"   python3 generate_hugo_sitemap.py")
    print(f"   git add sitemap.txt sitemap.xml sitemap*.xml")
    print(f"   git commit -m 'Update sitemap with all current posts'")
    print(f"   git push")

if __name__ == "__main__":
    main()