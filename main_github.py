"""
main_github.py — GitHub Pages 版本
自動抓取新聞、生成文章、發布到 GitHub Pages
"""

import sys
sys.path.insert(0, '/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/kiro_bloggerapi')

from dotenv import load_dotenv
import os
from pathlib import Path

# 加載環境變數
env_path = Path('/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/kiro_bloggerapi/.env')
load_dotenv(env_path)

from scraper import scrape_multiple
from generator import generate
from publisher_github import GitHubPublisher


def main(urls, output_dir="/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam"):
    """
    主流程：抓取 → 生成 → 發布到 GitHub
    """
    
    publisher = GitHubPublisher(output_dir)
    
    print(f"📋 共 {len(urls)} 篇，開始抓取...\n")
    scraped = scrape_multiple(urls)
    ok = [s for s in scraped if s.is_ok]
    failed = [s for s in scraped if not s.is_ok]
    
    print(f"✅ 抓取成功：{len(ok)} 篇")
    print(f"❌ 抓取失敗：{len(failed)} 篇")
    for s in failed[:5]:
        print(f"   {s.url[:60]} — {s.error}")
    if len(failed) > 5:
        print(f"   ...還有 {len(failed)-5} 篇失敗\n")
    
    print(f"🤖 開始生成 + 發布...\n")
    
    success_count = 0
    fail_gen = 0
    fail_pub = 0
    
    for i, article in enumerate(ok, 1):
        print(f"[{i}/{len(ok)}] 處理：{article.url[:60]}...")
        
        # 生成文章
        generated = generate(article, gemini_api_key=os.getenv('GEMINI_API_KEY'))
        if not generated.is_ok:
            fail_gen += 1
            print(f"  ❌ 生成失敗：{generated.error}")
            continue
        
        # 準備發布資料
        article_data = {
            'title': generated.title,
            'content': generated.html,  # 或用 generated.markdown（如果有的話）
            'original_url': article.url,
            'lens': getattr(generated, 'lens', 'AUTO'),
            'date': generated.date if hasattr(generated, 'date') else None
        }
        
        # 發布到 GitHub
        result = publisher.publish(article_data)
        
        if result['success']:
            success_count += 1
            print(f"  ✅ 發布成功：{result['message']}")
            print(f"     網址：{result['url']}")
        else:
            fail_pub += 1
            print(f"  ❌ 發布失敗：{result['message']}")
    
    print(f"\n🎉 完成！成功 {success_count} 篇，生成失敗 {fail_gen} 篇，發布失敗 {fail_pub} 篇")
    return success_count, fail_gen, fail_pub


if __name__ == "__main__":
    # 測試 URL
    test_urls = [
        'https://edition.cnn.com/2026/08/16/climate/lake-powell-reservoir-record-low-colorado-river'
    ]
    
    main(test_urls)
