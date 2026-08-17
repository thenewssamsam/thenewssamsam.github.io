# GitHub Pages 自動發布系統 — 完整設定指南

## 第 1 步：在 GitHub 建立 Repository

1. 進入 [GitHub](https://github.com)
2. 建立新 Repository，名稱必須是：**`thenewssamsam.github.io`**
3. 選擇「Public」（必須，GitHub Pages 需要）
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
git commit -m "Initial commit - GitHub Pages setup"
git push -u origin main
```

## 第 3 步：設定 GitHub Actions Secrets

GitHub Actions 需要 API 金鑰。設定方法：

1. 進入 Repository → Settings → Secrets and variables → Actions
2. 點擊「New repository secret」
3. 添加以下 secrets：

| Name | Value |
|------|-------|
| GEMINI_API_KEY | 你的 Gemini API Key |

> ⚠️ **重要**：不要在代碼裡放 API Key，一定要用 Secrets

## 第 4 步：啟用 GitHub Pages

1. Repository → Settings → Pages
2. Source 選擇「Deploy from a branch」
3. Branch 選擇「main」，資料夾選「/ (root)」
4. 點擊「Save」

等待幾分鐘，你的網站會在 `https://thenewssamsam.github.io` 上線！

## 第 5 步：測試自動發布

### 方式 1：手動觸發（測試用）

1. Repository → Actions
2. 選擇「Auto-Publish Articles」
3. 點擊「Run workflow」
4. 選擇「main」分支
5. 點擊「Run workflow」

等待執行，檢查是否成功。

### 方式 2：等待排定時間

GitHub Actions 設定為每天下午 2 點自動運行（台北時間）。

## 第 6 步：申請 Google AdSense

1. 進入 [Google AdSense](https://www.google.com/adsense)
2. 點擊「開始使用」
3. 輸入你的網站 URL：`https://thenewssamsam.github.io`
4. 填寫申請表

> ⚠️ **等待時間**：AdSense 通常 2-3 週才會審核。審核成功後，才能在網站上放廣告。

## 第 7 步：添加 AdSense 到網站

AdSense 審核通過後：

1. 進入 AdSense 帳戶，複製你的 **Publisher ID**（格式：`ca-pub-xxxxxxxxxx`）
2. 編輯檔案 `_layouts/post.html`
3. 替換這行：
   ```
   data-ad-client="ca-pub-XXXXXXXXX"
   ```
   改成：
   ```
   data-ad-client="ca-pub-你的ID"
   ```
4. Commit 和 push：
   ```bash
   git add _layouts/post.html
   git commit -m "Add AdSense publisher ID"
   git push
   ```

GitHub Pages 會自動更新網站。

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

### 檢查發布狀態

1. Repository → Actions
2. 查看最近的 workflow runs
3. 點擊進去看詳細日誌

### 常見問題

**Q: GitHub Pages 不更新？**
A: 等待 1-2 分鐘。GitHub Pages 需要時間重新構建。查看 Repository → Settings → Pages 的「Last deployed」時間。

**Q: AdSense 廣告沒出現？**
A: 
1. 檢查 Publisher ID 是否正確
2. 確認網站在 AdSense 審核通過名單中
3. 等待 24-48 小時，Google 需要時間掃描你的網站

**Q: 文章沒有發布？**
A: 檢查 Actions 的執行日誌：
1. Repository → Actions
2. 點擊最近的 workflow run
3. 查看 logs 了解問題

---

## 完成！

你現在有：
✅ 完全免費的網站（GitHub Pages）
✅ 自動發布系統（GitHub Actions）
✅ 無限文章數量
✅ Google AdSense 廣告（審核通過後）

祝你成功！
