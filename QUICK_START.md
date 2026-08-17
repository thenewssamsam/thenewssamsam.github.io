# 快速開始

## 5 分鐘快速設定

### 1. 建立 GitHub Repository
```
Repository 名稱：thenewssamsam.github.io
可見性：Public
```

### 2. 推送代碼到 GitHub
```bash
cd beyondthenewssam
git init
git remote add origin https://github.com/thenewssamsam/thenewssamsam.github.io.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 3. 啟用 GitHub Pages
Settings → Pages → Branch: main → Save

### 4. 添加 Secrets（用於 GitHub Actions）
Settings → Secrets → New secret
- Name: `GEMINI_API_KEY`
- Value: 你的 Gemini API Key

### 5. 手動測試一次
Actions → Auto-Publish Articles → Run workflow

## 網站網址

```
https://thenewssamsam.github.io
```

## 自動發布時間

每天下午 2 點（台北時間）自動發布新文章。

## 所需的環境變數

在 `.env` 或 GitHub Secrets 中：

```
GEMINI_API_KEY=你的_key
```

## 文章會自動放在

```
_posts/YYYY-MM-DD-title.md
```

每篇文章會自動包含：
- ✅ 標題
- ✅ 發布日期
- ✅ 分類和標籤
- ✅ Google AdSense 廣告（審核通過後）

## 常用命令

```bash
# 檢查本機網站
bundle exec jekyll serve

# 查看本機網站
http://localhost:4000

# 推送更新
git add .
git commit -m "Update"
git push origin main
```

---

更多細節見 `SETUP.md`
