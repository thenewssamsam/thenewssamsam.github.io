# Netlify 部署系統 — 完整設定指南

## 第 1 步：在 GitHub 建立 Repository

1. 進入 [GitHub](https://github.com)
2. 建立新 Repository，名稱必須是：**`thenewssamsam.github.io`**
3. 選擇「Public」（必須，Netlify 需要）
4. 點擊「Create repository」

## 第 2 步：初始化本機 Git

在終端機執行：

```bash
cd /Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam

# 初始化 git
git init
git branch -M main

# 添加遠端
git remote add origin https://github.com/thenewssamsam/thenewssamsam.github.io.git

# 設定 Git 使用者
git config user.email "yenyaosam@gmail.com"
git config user.name "Your Name"

# 第一次推送
git add .
git commit -m "Initial commit - Netlify setup"
git push -u origin main
```

## 第 3 步：設定 Netlify

### 3.1 創建 Netlify 帳號

1. 訪問 [Netlify](https://app.netlify.com/signup)
2. 使用 GitHub 帳號登入（最簡單）

### 3.2 連接 GitHub 倉庫

1. 在 Netlify 控制台點擊「Add new site」→「Import an existing project」
2. 選擇「GitHub」
3. 授權 Netlify 訪問你的 GitHub
4. 選擇倉庫：`thenewssamsam/thenewssamsam.github.io`

### 3.3 配置構建設置

Netlify 會自動檢測到 `netlify.toml` 文件，確認以下設置：
- **Build command**: `bundle install && bundle exec jekyll build --safe`
- **Publish directory**: `_site`
- **Ruby version**: 3.1（自動設置）

### 3.4 設置自定義域名（可選）

1. 點擊「Site settings」→「Domain management」
2. 點擊「Add custom domain」
3. 輸入你的域名（如果有的話）或使用 Netlify 免費域名

等待幾分鐘，你的網站會在 Netlify 提供的 URL 上線！

## 第 4 步：測試 Netlify 部署

### 觸發重新部署

1. 在 Netlify 控制台點擊「Deploys」標籤
2. 點擊「Trigger deploy」→「Deploy site」
3. 等待部署完成（通常 1-3 分鐘）

### 檢查部署狀態

1. 查看「Deploys」標籤中的最新部署
2. 點擊進去看詳細日誌
3. 確認「Deploy succeeded」

## 第 5 步：添加廣告驗證碼

### Monetag 驗證

廣告商驗證碼已添加到多個位置：

1. **`_layouts/default.html`** - 主佈局文件
2. **`google8d1f88bd01c89473.html`** - Google 驗證文件
3. **`monetag.txt`** - 純文字驗證文件
4. **`monetag_verification.html`** - HTML 驗證文件

驗證碼：`66029fd72330fcc14da7a64dd7375a77`

### Google Search Console

1. 進入 [Google Search Console](https://search.google.com/search-console)
2. 添加網站：使用 Netlify 提供的 URL
3. 選擇驗證方式：HTML 文件驗證
4. 上傳 `google8d1f88bd01c89473.html` 文件
5. 提交 sitemap：`https://your-netlify-url/sitemap.xml`

### AdSense 申請（可選）

1. 進入 [Google AdSense](https://www.google.com/adsense)
2. 點擊「開始使用」
3. 輸入你的網站 URL（Netlify URL）
4. 填寫申請表

> ⚠️ **等待時間**：AdSense 通常 2-3 週才會審核。

## 日常維護

### 手動新增文章

如果要手動新增文章，在 `_posts/` 建立 Markdown 檔案：

檔名格式：`YYYY-MM-DD-title.md`

範例：`2026-08-17-lake-powell.md`

內容格式：

```markdown
---
layout: post
title: Lake Powell Hits Record Low
date: 2026-08-17 14:30:00 +0800
categories: news
tags: [climate, environment]
author: Sam
source_url: https://example.com/article
---

文章內容在這裡...
```

然後 commit 和 push：

```bash
git add _posts/2026-08-17-lake-powell.md
git commit -m "Add: Lake Powell article"
git push
```

Netlify 會自動檢測到變更並開始部署。

### 檢查部署狀態

1. Netlify 控制台 → Deploys
2. 查看最近的部署
3. 點擊進去看詳細日誌

### 本地批次發布系統

使用 Python 腳本進行批次發布：

```bash
cd /Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/kiro_bloggerapi

# 執行批次發布腳本
python batch_publish_news.py
```

此腳本會：
1. 抓取 CNN 文章內容
2. 生成文章內容
3. 發布到 GitHub
4. 可選：發布到 Bluesky
5. 更新 Hugo-style sitemap

### 常見問題

**Q: Netlify 部署失敗？**
A: 檢查以下幾點：
1. 查看 Netlify 部署日誌中的錯誤訊息
2. 確認 `netlify.toml` 文件存在且格式正確
3. 確認 `Gemfile` 包含所有必要的依賴
4. 檢查 Ruby 版本是否設置為 3.1

**Q: 廣告驗證失敗？**
A:
1. 確認 monetag meta 標籤在 `_layouts/default.html` 中
2. 等待 Netlify 完成部署（1-3 分鐘）
3. 使用多種驗證方法（meta 標籤、文件上傳）
4. 聯繫廣告商支援提供詳細錯誤訊息

**Q: Google Search Console 不收錄？**
A:
1. 確認 sitemap 已提交：`https://your-netlify-url/sitemap.xml`
2. 檢查 robots.txt 是否正確引用 sitemap
3. 增加內部連結和外部連結
4. 定期發布高質量內容
5. 等待 Google 爬蟲發現和索引（通常需要幾週）

**Q: 本地發布後沒有同步到 Netlify？**
A:
1. 確認已執行 `git push`
2. 檢查 Netlify 是否檢測到新的 commit
3. 手動觸發 Netlify 部署
4. 查看部署日誌了解問題

---

## 完成！

你現在有：
✅ 完全免費的網站（Netlify）
✅ 自動部署系統（Netlify Git integration）
✅ 全球 CDN 加速
✅ 對 SEO 友好的部署環境
✅ 無限文章數量
✅ 廣告驗證碼已設置
✅ Hugo-style sitemap 支援
✅ 本地批次發布系統
✅ 可選的 Bluesky 社交媒體整合

祝你成功！
