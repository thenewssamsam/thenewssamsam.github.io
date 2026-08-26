"""
publisher_github.py — 發布到 GitHub Pages
用法：
1. 生成文章 Markdown
2. 自動 commit 和 push 到 GitHub
3. GitHub Pages 自動部署
4. 自動發布到 Bluesky（可選）
"""

import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path


class GitHubPublisher:
    def __init__(self, repo_path=None, enable_bluesky=True):
        # 使用傳入的路徑，或從環境變數中讀取，或使用預設值
        if repo_path is None:
            repo_path = os.getenv('GITHUB_REPO_PATH', '/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam')
        self.repo_path = Path(repo_path)
        self.posts_dir = self.repo_path / "_posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        self.enable_bluesky = enable_bluesky
        self.bluesky_publisher = None
        
        # 初始化 Bluesky 發布器
        if enable_bluesky:
            try:
                from bluesky_publisher import get_bluesky_publisher
                self.bluesky_publisher = get_bluesky_publisher()
                if self.bluesky_publisher:
                    print("✅ Bluesky 發布器已初始化")
                    # 🆕 設置為禁止所有人回覆
                    self.bluesky_publisher.config.reply_restriction = "disabled"
                    print("🔒 Bluesky 設置：關閉所有人回覆")
            except Exception as e:
                print(f"⚠️  Bluesky 發布器初始化失敗：{str(e)}")
                self.bluesky_publisher = None

    def sanitize_filename(self, title):
        """清潔標題，用於檔案名稱"""
        # 移除特殊字符
        sanitized = re.sub(r'[^a-zA-Z0-9\s-]', '', title)
        # 用連字符替換空格
        sanitized = re.sub(r'\s+', '-', sanitized)
        # 轉小寫
        sanitized = sanitized.lower()
        # 移除多餘的連字符
        sanitized = re.sub(r'-+', '-', sanitized)
        return sanitized.strip('-')[:80]  # 限制長度

    def clean_yaml_value(self, value):
        """清理 YAML 值，移除問題字符"""
        if not value:
            return ""
        # 轉為字符串
        value = str(value)
        # 移除管道符和其他特殊字符
        value = value.replace('|', '').replace('[', '').replace(']', '')
        # 移除多餘空白
        value = re.sub(r'\s+', ' ', value).strip()
        # 移除引號（如果已有）避免雙重引號
        value = value.replace('"', "'")
        # 限制長度，避免 YAML 換行
        value = value[:150]
        return value

    def generate_markdown(self, article_data):
        """
        從文章資料生成 Markdown
        """
        title = self.clean_yaml_value(article_data.get('title', 'Untitled'))
        content = article_data.get('content', '')
        url = article_data.get('original_url', '')
        lens = self.clean_yaml_value(article_data.get('lens', 'AUTO'))
        date = article_data.get('date', datetime.now())

        # 格式化日期 - Jekyll 只需要日期部分
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        date_str = date.strftime("%Y-%m-%d")
        
        # 簡化 lens（只取主要部分）
        lens_simple = lens.split(' ')[0].lower() if lens else 'news'
        
        # 清理 URL，移除特殊字符
        url = url.replace('"', "'") if url else ""
        
        # 生成簡單的 front matter
        # ✅ 移除 categories: [news] 行
        # 這樣 Jekyll 預設 permalink 就會是 /:year/:month/:day/:title.html（無 /news/）
        # 與首頁顯示的 URL 格式保持一致
        front_matter = f"""---
layout: post
title: {repr(title)}
date: {date_str}
published: true
tags:
  - {lens_simple}
author: Sam
source_url: {repr(url)}
---

"""
        
        # 組合 Markdown
        markdown = front_matter + content
        
        return markdown

    def save_markdown(self, markdown, title):
        """
        保存 Markdown 檔案到 _posts 目錄
        檔名格式：YYYY-MM-DD-title.md
        """
        now = datetime.now()
        date_prefix = now.strftime("%Y-%m-%d")
        filename = f"{date_prefix}-{self.sanitize_filename(title)}.md"
        filepath = self.posts_dir / filename
        
        # 如果已存在同名檔案，加上時間戳
        counter = 1
        base_filepath = filepath
        while filepath.exists():
            name = f"{date_prefix}-{self.sanitize_filename(title)}-{counter}.md"
            filepath = self.posts_dir / name
            counter += 1
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return str(filepath)

    def regenerate_sitemap(self):
        """
        重新生成 sitemap.xml（Hugo 風格 index 格式）
        """
        try:
            sitemap_script = self.repo_path / "generate_hugo_sitemap.py"
            if not sitemap_script.exists():
                return False, "Hugo 風格 Sitemap 生成腳本不存在"
            
            # 執行 Python 腳本
            result = subprocess.run(
                ['python3', str(sitemap_script)],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "✅ Hugo 風格 Sitemap 已更新"
            else:
                return False, f"Hugo 風格 Sitemap 生成失敗：{result.stderr}"
        except Exception as e:
            return False, f"❌ Hugo 風格 Sitemap 生成異常：{str(e)}"

    def commit_and_push(self, file_path, commit_message=None):
        """
        Commit 和 push 到 GitHub
        """
        try:
            os.chdir(self.repo_path)
            
            # Stage 檔案
            subprocess.run(['git', 'add', file_path], check=True, capture_output=True)
            
            # Commit
            if not commit_message:
                title = Path(file_path).stem
                commit_message = f"Auto-publish: {title}"
            
            # 重新生成 sitemap（新增）
            sitemap_success, sitemap_msg = self.regenerate_sitemap()
            if sitemap_success:
                # 如果 sitemap 更新成功，就 add 到同一個 commit (Hugo 風格: sitemap.xml + sitemap*.xml + 生成器腳本)
                subprocess.run(['git', 'add', 'sitemap.xml', 'sitemap1.xml', 'sitemap2.xml', 'sitemap3.xml', 'generate_hugo_sitemap.py'], capture_output=True)
                commit_message += " (with sitemap update)"
            
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
            
            # Pull before push to handle remote changes
            subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], capture_output=True)
            
            # Push
            result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                msg = f"✅ 發布成功：{file_path}"
                if sitemap_success:
                    msg += f"\n   {sitemap_msg}"
                return True, msg
            else:
                return False, f"Push 失敗：{result.stderr}"
        
        except subprocess.CalledProcessError as e:
            return False, f"❌ Git 操作失敗：{str(e)}"
        except Exception as e:
            return False, f"❌ 發布失敗：{str(e)}"

    def publish(self, article_data):
        """
        完整發布流程
        """
        try:
            # 1. 生成 Markdown
            markdown = self.generate_markdown(article_data)
            
            # 2. 保存檔案
            file_path = self.save_markdown(markdown, article_data['title'])
            
            # 3. Commit 和 Push
            success, message = self.commit_and_push(file_path)
            
            if success:
                # ⚠️ 重要：確保 URL 與首頁生成的連結路徑一致
                # Jekyll 默認 permalink: /:year/:month/:day/:title.html (無 /news/)
                # 這與首頁顯示的 URL 格式一致
                filename = Path(file_path).stem
                print(f"📁 檔名處理: {filename}")
                
                # 從檔名提取日期和標題
                parts = filename.split('-', 3)  # 分割為 [year, month, day, title]
                print(f"📊 檔名分割: {parts}")
                
                if len(parts) >= 4:
                    year, month, day = parts[0], parts[1], parts[2]
                    title = parts[3]
                    # 移除結尾的連字符（如果有）
                    title = title.rstrip('-')
                    # ✅ 移除 /news/ 前綴，改為 Jekyll 預設的 /:year/:month/:day/:title.html 格式
                    url = f"https://johnthenews.netlify.app/{year}/{month}/{day}/{title}.html"
                    print(f"🔗 生成的 URL: {url}")
                else:
                    url = f"https://johnthenews.netlify.app/{filename}.html"
                    print(f"🔗 備用 URL: {url}")
                
                # 4. 更新 sitemap.txt
                try:
                    sitemap_path = self.repo_path / "sitemap.txt"
                    with open(sitemap_path, 'a', encoding='utf-8') as f:
                        f.write(url + '\n')
                    print(f"   🗺️ 已添加 URL 到 sitemap.txt")
                except Exception as e:
                    print(f"   ⚠️  更新 sitemap.txt 失敗: {str(e)}")
                
                # 5. 發布到 Bluesky（如果啟用）
                bluesky_result = None
                if self.enable_bluesky and self.bluesky_publisher:
                    try:
                        article_title = article_data.get('title', '')
                        article_content = article_data.get('content', '')
                        source_url = article_data.get('original_url', '')
                        
                        print(f"\n📱 發布到 Bluesky...")
                        print(f"   🔗 文章 URL：{url}")
                        print(f"   📰 標題：{article_title[:60]}")
                        print(f"   🌐 來源：{source_url[:50] if source_url else '無'}")
                        
                        # 🆕 使用新的 Bluesky 格式：摘要 + 兩個 URL
                        # 從文章內容提取簡短摘要（會自動截短至 20-25 個英文單字以容納兩個 URL）
                        
                        # 先認證 Bluesky 發布器（如果還未認證）
                        if not self.bluesky_publisher.is_authenticated:
                            print(f"   🔐 Bluesky 認證中...")
                            if not self.bluesky_publisher.authenticate():
                                raise Exception("Bluesky 認證失敗")
                            print(f"   ✅ Bluesky 已認證")
                        
                        # 清理 HTML 內容（使用品質控制系統）
                        from quality_control import QualityControl
                        qc = QualityControl()
                        clean_content = qc.clean_html(article_content)
                        
                        # 提取前 100 個詞（會被截短以容納兩個 URL）
                        words = clean_content.split()[:100]
                        summary = ' '.join(words)
                        
                        # 使用新的 generate_social_post() 方法生成貼文（包含兩個 URL）
                        social_post = self.bluesky_publisher.generate_social_post(
                            article_title=article_title,
                            article_url=url,
                            source_url=source_url,  # 包含來源 URL（第二個 URL）
                            article_summary=summary
                        )
                        
                        print(f"   📝 貼文：{social_post.char_count}/300 字符")
                        
                        # 發布
                        bluesky_result = self.bluesky_publisher.publish_post(social_post)
                        
                        if bluesky_result['success']:
                            print(f"   ✅ Bluesky 發布成功")
                            print(f"   📎 URL Facets：{bluesky_result.get('url_facets_count', 0)} 個可點擊連結")
                            print(f"   📝 文字長度：{bluesky_result.get('char_count', 0)} 字元")
                            print(f"   🔗 Post URI：{bluesky_result['post_uri']}")
                        else:
                            print(f"   ⚠️  Bluesky 發布失敗：{bluesky_result.get('error', '未知錯誤')}")
                    except Exception as e:
                        print(f"   ⚠️  Bluesky 發布異常：{str(e)}")
                
                return {
                    'success': True,
                    'message': message,
                    'file': file_path,
                    'url': url,
                    'bluesky': bluesky_result
                }
            else:
                return {
                    'success': False,
                    'message': message,
                    'file': file_path
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"❌ 發布失敗：{str(e)}"
            }

    def publish_multiple_with_comments(self, articles_data, interval_minutes=5):
        """
        批次發布多篇文章到 GitHub 和 Bluesky，並添加聯盟評論
        
        Args:
            articles_data: 文章資料列表
            interval_minutes: 每篇文章之間的間隔時間（分鐘）
        
        Returns:
            發布結果列表
        """
        results = []
        total_articles = len(articles_data)
        
        print(f"\n🚀 開始批次發布 {total_articles} 篇文章")
        print(f"⏱️  每篇文章間隔：{interval_minutes} 分鐘")
        
        for i, article_data in enumerate(articles_data, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{total_articles}] 處理文章：{article_data.get('title', 'Untitled')[:60]}")
            print(f"{'='*60}")
            
            # 1. 發布主貼文
            result = self.publish(article_data)
            results.append(result)
            
            if result['success']:
                print(f"✅ [{i}/{total_articles}] 主貼文發布成功")
                
                # 2. 發布聯盟評論（如果 Bluesky 發布成功）
                if self.enable_bluesky and self.bluesky_publisher and result.get('bluesky', {}).get('success'):
                    try:
                        print(f"\n💬 開始發布聯盟評論...")
                        
                        # 使用 publish_post_with_comments 方法，傳入現有貼文資訊
                        bluesky_data = result.get('bluesky', {})
                        post_uri = bluesky_data.get('post_uri', '')
                        post_cid = bluesky_data.get('post_cid', '')
                        
                        comments_result = self.bluesky_publisher.publish_post_with_comments(
                            post_text=bluesky_data.get('text', ''),
                            article_url=result.get('url', ''),
                            use_existing_post=True,
                            existing_post_uri=post_uri,
                            existing_post_cid=post_cid
                        )
                        
                        if comments_result['success']:
                            print(f"✅ 聯盟評論發布完成：{len(comments_result.get('comment_urls', []))} 則")
                        else:
                            print(f"⚠️  聯盟評論發布失敗：{comments_result.get('error', '未知錯誤')}")
                            
                    except Exception as e:
                        print(f"⚠️  聯盟評論發布異常：{str(e)}")
            else:
                print(f"❌ [{i}/{total_articles}] 主貼文發布失敗")
            
            # 等待間隔時間（最後一篇文章不需要等待）
            if i < total_articles:
                print(f"\n⏳ 等待 {interval_minutes} 分鐘後繼續下一篇文章...")
                time.sleep(interval_minutes * 60)  # 轉換為秒
        
        print(f"\n{'='*60}")
        print(f"📊 批次發布完成")
        print(f"{'='*60}")
        
        # 統計結果
        success_count = sum(1 for r in results if r['success'])
        print(f"成功：{success_count}/{total_articles}")
        
        return results
