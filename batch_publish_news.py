"""
批次發布多個新聞網址
支援從文件或命令行參數讀取網址列表
"""

import sys
import os
import time
import json
import random
from datetime import datetime
from pathlib import Path

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def load_urls_from_file(file_path):
    """從文件載入網址列表"""
    urls = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳過空行和註釋
                    urls.append(line)
        print(f"✅ 從文件載入 {len(urls)} 個網址")
        return urls
    except Exception as e:
        print(f"❌ 載入文件失敗: {str(e)}")
        return []

def save_progress(progress_file, completed_urls, failed_urls):
    """保存進度到文件"""
    try:
        progress = {
            'completed': completed_urls,
            'failed': failed_urls,
            'timestamp': datetime.now().isoformat()
        }
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️  保存進度失敗: {str(e)}")

def load_progress(progress_file):
    """從文件載入進度"""
    try:
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                return progress.get('completed', []), progress.get('failed', [])
    except Exception as e:
        print(f"⚠️  載入進度失敗: {str(e)}")
    return [], []

def process_single_url(url, publisher, enable_bluesky=True):
    """處理單個網址"""
    try:
        from scraper import scrape
        from generator import generate
        from dotenv import load_dotenv
        
        # 載入環境變數
        load_dotenv()
        
        print(f"\n{'='*60}")
        print(f"📰 處理網址: {url[:60]}...")
        print(f"{'='*60}")
        
        # 1. 抓取文章
        print(f"📥 Step 1: 抓取文章內容...")
        scrape_result = scrape(url)
        
        if not scrape_result.is_ok:
            print(f"❌ 抓取失敗: {scrape_result.error}")
            return False, url, "抓取失敗"
        
        print(f"✅ 抓取成功: {scrape_result.title[:60]}...")
        
        # 2. 生成文章
        print(f"✍️  Step 2: 生成文章...")
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if not gemini_api_key:
            print(f"❌ 缺少 GEMINI_API_KEY")
            return False, url, "缺少API密鑰"
        
        gen_result = generate(
            scrape_result,
            gemini_api_key=gemini_api_key,
            lens="AUTO",
            model="models/gemini-3.5-flash-lite"
        )
        
        if not gen_result.is_ok:
            print(f"❌ 生成失敗: {gen_result.error}")
            return False, url, "生成失敗"
        
        print(f"✅ 生成成功: {gen_result.title[:60]}...")
        
        # 3. 準備文章數據
        article_data = {
            'title': gen_result.title or gen_result.seo_title or "Untitled",
            'content': gen_result.html_body,
            'original_url': url,
            'date': datetime.now(),
            'lens': 'AUTO'
        }
        
        # 4. 發布到 GitHub 和 Bluesky
        print(f"🌐 Step 3: 發布到 GitHub Pages...")
        result = publisher.publish(article_data)
        
        if result['success']:
            print(f"✅ GitHub 發布成功")
            print(f"   🔗 URL: {result['url'][:50]}...")
            
            # Bluesky 發布
            if enable_bluesky and result.get('bluesky'):
                bluesky_data = result['bluesky']
                if bluesky_data.get('success'):
                    print(f"✅ Bluesky 主貼文發布成功")
                    print(f"   字符數: {bluesky_data.get('char_count', 'N/A')}/300")
                    
                    # 發布聯盟評論
                    print(f"💬 發布聯盟評論...")
                    try:
                        from bluesky_publisher import get_bluesky_publisher
                        bluesky_publisher = get_bluesky_publisher()
                        
                        if bluesky_publisher:
                            comments_result = bluesky_publisher.publish_post_with_comments(
                                post_text=bluesky_data.get('text', ''),
                                article_url=result['url'],
                                use_existing_post=True,
                                existing_post_uri=bluesky_data.get('post_uri', ''),
                                existing_post_cid=bluesky_data.get('post_cid', '')
                            )
                            
                            if comments_result['success']:
                                print(f"✅ 聯盟評論發布完成: {len(comments_result.get('comment_urls', []))} 則")
                            else:
                                print(f"⚠️  聯盟評論發布失敗: {comments_result.get('error', '未知錯誤')}")
                    except Exception as e:
                        print(f"⚠️  聯盟評論發布異常: {str(e)}")
                else:
                    print(f"⚠️  Bluesky 發布失敗: {bluesky_data.get('error', '未知錯誤')}")
            
            return True, url, result['url']
        else:
            print(f"❌ 發布失敗: {result['message']}")
            return False, url, result['message']
            
    except Exception as e:
        print(f"❌ 處理過程出現錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, url, str(e)

def batch_process(urls, enable_bluesky=True, interval_minutes=5, progress_file='batch_progress.json'):
    """批次處理多個網址"""
    # 載入進度
    completed_urls, failed_urls = load_progress(progress_file)
    
    # 過濾已完成的網址
    remaining_urls = [url for url in urls if url not in completed_urls]
    
    print(f"\n🚀 開始批次處理")
    print(f"{'='*60}")
    print(f"總網址數: {len(urls)}")
    print(f"已完成: {len(completed_urls)}")
    print(f"待處理: {len(remaining_urls)}")
    print(f"Bluesky: {'啟用' if enable_bluesky else '禁用'}")
    print(f"間隔時間: {interval_minutes} 分鐘")
    print(f"{'='*60}")
    
    if not remaining_urls:
        print("✅ 所有網址都已處理完成")
        return True
    
    # 初始化發布器
    try:
        from publisher_github import GitHubPublisher
        publisher = GitHubPublisher(enable_bluesky=enable_bluesky)
        print("✅ 發布器初始化成功")
    except Exception as e:
        print(f"❌ 發布器初始化失敗: {str(e)}")
        return False
    
    # 處理每個網址
    success_count = 0
    total_remaining = len(remaining_urls)
    
    for i, url in enumerate(remaining_urls, 1):
        print(f"\n📍 進度: [{i}/{total_remaining}]")
        
        success, processed_url, result = process_single_url(url, publisher, enable_bluesky)
        
        if success:
            success_count += 1
            completed_urls.append(processed_url)
            print(f"✅ [{i}/{total_remaining}] 處理成功")
        else:
            failed_urls.append({'url': processed_url, 'error': result})
            print(f"❌ [{i}/{total_remaining}] 處理失敗: {result}")
        
        # 保存進度
        save_progress(progress_file, completed_urls, failed_urls)
        
        # 間隔時間（只在成功時等待，失敗時直接跳過）
        if success and i < total_remaining:
            # 隨機間隔：1秒到5秒之間
            random_interval = random.randint(1, 5)
            print(f"\n⏳ 隨機等待 {random_interval} 秒後繼續...")
            time.sleep(random_interval)
        elif not success:
            print(f"\n⚡ 失敗，直接跳到下一個網址（不等待）")
    
    # 最終統計
    print(f"\n{'='*60}")
    print(f"📊 批次處理完成")
    print(f"{'='*60}")
    print(f"總網址數: {len(urls)}")
    print(f"成功: {success_count}")
    print(f"失敗: {len(failed_urls)}")
    print(f"成功率: {success_count/len(urls)*100:.1f}%")
    
    if failed_urls:
        print(f"\n❌ 失敗的網址:")
        for failed in failed_urls:
            print(f"   {failed['url'][:60]}... - {failed['error'][:40]}")
    
    # 如果有成功的文章，更新 sitemap
    if success_count > 0:
        print(f"\n🗺️ 更新 sitemap...")
        try:
            import subprocess
            import shutil
            
            # 獲取腳本目錄
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sitemap_script = os.path.join(script_dir, "generate_hugo_sitemap.py")
            
            # 獲取倉庫目錄（假設在腳本目錄的父目錄）
            repo_dir = os.path.dirname(script_dir)
            
            # 複製 sitemap 生成器到倉庫目錄
            target_script = os.path.join(repo_dir, "generate_hugo_sitemap.py")
            shutil.copy(sitemap_script, target_script)
            
            # 調用 Hugo 風格的 sitemap 生成器
            subprocess.run(["python3", target_script], check=True, cwd=repo_dir)
            
            # 提交 sitemap (Hugo 風格: index + 所有子文件 + 生成器腳本)
            subprocess.run(["git", "add", "sitemap.xml", "sitemap1.xml", "sitemap2.xml", "sitemap3.xml", "generate_hugo_sitemap.py"], check=True, cwd=repo_dir)
            subprocess.run(["git", "commit", "-m", "Auto-update Hugo-style sitemap after batch publish"], check=True, cwd=repo_dir)
            subprocess.run(["git", "push"], check=True, cwd=repo_dir)
            
            print(f"✅ Sitemap 已更新並提交")
        except Exception as e:
            print(f"⚠️ Sitemap 更新失敗: {str(e)}")
    
    return success_count == len(remaining_urls)

def main():
    # 解析命令行參數
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3.11 batch_publish_news.py <網址1> <網址2> ...")
        print("  python3.11 batch_publish_news.py --file <網址列表文件>")
        print("  python3.11 batch_publish_news.py --file urls.txt --no-bluesky")
        print("  python3.11 batch_publish_news.py --file urls.txt --interval 10")
        sys.exit(1)
    
    urls = []
    enable_bluesky = True
    interval_minutes = 1  # 默認1分鐘（實際使用隨機20-60秒）
    progress_file = 'batch_progress.json'
    
    # 解析參數
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg == '--file':
            if i + 1 < len(sys.argv):
                file_path = sys.argv[i + 1]
                urls = load_urls_from_file(file_path)
                i += 2
            else:
                print("❌ --file 需要指定文件路徑")
                sys.exit(1)
        elif arg == '--no-bluesky':
            enable_bluesky = False
            i += 1
        elif arg == '--interval':
            if i + 1 < len(sys.argv):
                interval_minutes = int(sys.argv[i + 1])
                i += 2
            else:
                print("❌ --interval 需要指定分鐘數")
                sys.exit(1)
        elif arg == '--progress':
            if i + 1 < len(sys.argv):
                progress_file = sys.argv[i + 1]
                i += 2
            else:
                print("❌ --progress 需要指定文件路徑")
                sys.exit(1)
        else:
            # 直接是網址
            urls.append(arg)
            i += 1
    
    if not urls:
        print("❌ 沒有提供網址")
        sys.exit(1)
    
    # 執行批次處理
    success = batch_process(urls, enable_bluesky, interval_minutes, progress_file)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()