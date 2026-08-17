"""
publisher_github.py — 發布到 GitHub Pages
用法：
1. 生成文章 Markdown
2. 自動 commit 和 push 到 GitHub
3. GitHub Pages 自動部署
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path


class GitHubPublisher:
    def __init__(self, repo_path="/Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam"):
        self.repo_path = Path(repo_path)
        self.posts_dir = self.repo_path / "_posts"
        self.posts_dir.mkdir(parents=True, exist_ok=True)

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
        # 移除管道符和其他特殊字符
        value = str(value).replace('|', '').replace('[', '').replace(']', '')
        # 移除多餘空白
        value = re.sub(r'\s+', ' ', value).strip()
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

        # 格式化日期
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
        
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 簡化 lens（只取主要部分）
        lens_simple = lens.split(' ')[0].lower() if lens else 'news'
        
        # 生成簡單的 front matter
        front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: [news]
tags: [{lens_simple}]
author: Sam
source_url: "{url}"
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
            
            subprocess.run(['git', 'commit', '-m', commit_message], check=True, capture_output=True)
            
            # Push
            result = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True, text=True)
            
            if result.returncode == 0:
                return True, f"✅ 發布成功：{file_path}"
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
                return {
                    'success': True,
                    'message': message,
                    'file': file_path,
                    'url': f"https://thenewssamsam.github.io/{Path(file_path).stem}/"
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
