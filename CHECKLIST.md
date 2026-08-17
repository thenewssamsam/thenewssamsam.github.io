# 部署清單

在執行以下步驟前，確保你已完成所有檢查清單。

## 第一階段：本機準備

- [ ] 已安裝 Git（`git --version` 確認）
- [ ] 已安裝 Python 3.11+（`python3 --version` 確認）
- [ ] 已有 GitHub 帳號
- [ ] 已有 Gemini API Key

## 第二階段：建立 GitHub Repository

- [ ] 登入 GitHub
- [ ] 建立新 Repository：`thenewssamsam.github.io`
- [ ] 設定為 Public
- [ ] 複製 Repository URL

## 第三階段：推送代碼

在終端機執行以下命令：

```bash
cd /Users/yanyaosheng/Desktop/temp/yenyaosam_kiro/beyondthenewssam

# 初始化 git
git init

# 設定遠端
git remote add origin https://github.com/[你的帳號]/thenewssamsam.github.io.git

# 設定使用者
git config user.email "yenyaosam@gmail.com"
git config user.name "Sam"

# 主分支
git branch -M main

# 第一次推送
git add .
git commit -m "Initial commit: GitHub Pages + Auto-publish setup"
git push -u origin main
```

- [ ] Git 推送成功（無錯誤）
- [ ] 檢查 GitHub 是否收到代碼

## 第四階段：啟用 GitHub Pages

在 GitHub 網站上：

- [ ] 進入 Repository Settings
- [ ] 左邊選擇「Pages」
- [ ] Source 設定為「Deploy from a branch」
- [ ] Branch 選擇「main」，資料夾選「/ (root)」
- [ ] 點擊「Save」
- [ ] 等待 1-2 分鐘，網站應在 `https://thenewssamsam.github.io` 上線

檢查：
- [ ] 訪問 `https://thenewssamsam.github.io` — 應看到首頁
- [ ] 確認「Settings → Pages」顯示「Your site is live at...」

## 第五階段：設定 GitHub Actions

- [ ] 進入 Repository Settings
- [ ] 左邊選擇「Secrets and variables → Actions」
- [ ] 點擊「New repository secret」
- [ ] 名稱：`GEMINI_API_KEY`
- [ ] 值：你的 Gemini API Key
- [ ] 點擊「Add secret」

- [ ] 確認 Secret 已添加（不應顯示值）

## 第六階段：測試自動化

- [ ] 進入 Repository → Actions 分頁
- [ ] 選擇「Auto-Publish Articles」workflow
- [ ] 點擊「Run workflow」
- [ ] 選擇 main 分支
- [ ] 點擊綠色「Run workflow」按鈕
- [ ] 等待 2-3 分鐘

檢查結果：
- [ ] Workflow 完成（顯示綠色勾）
- [ ] 檢查 `_posts/` 資料夾是否有新文章
- [ ] 進入 `https://thenewssamsam.github.io` 檢查是否有新文章出現

## 第七階段：申請 Google AdSense

當網站穩定後：

- [ ] 訪問 `https://www.google.com/adsense`
- [ ] 點擊「開始使用」
- [ ] 輸入網站 URL：`https://thenewssamsam.github.io`
- [ ] 填寫申請表並提交
- [ ] 等待 Google 審核（通常 2-3 週）

## 第八階段：添加 AdSense 到網站（AdSense 審核通過後）

- [ ] 登入 AdSense 帳戶
- [ ] 複製 Publisher ID（格式：`ca-pub-xxxxxxxxxx`）
- [ ] 編輯檔案 `_layouts/post.html`
- [ ] 替換 `ca-pub-XXXXXXXXX` 為你的 Publisher ID（共 2 處）
- [ ] Commit 和 Push：
  ```bash
  git add _layouts/post.html
  git commit -m "Add AdSense publisher ID"
  git push
  ```
- [ ] 等待 1-2 分鐘，網站自動更新
- [ ] 檢查文章頁面是否有廣告出現

## 最終檢查

- [ ] 網站能訪問：`https://thenewssamsam.github.io`
- [ ] 首頁能看到最近的文章
- [ ] 文章頁面有 AdSense 廣告位置（即使沒有廣告也要有位置）
- [ ] GitHub Actions 每天自動運行
- [ ] 新文章能自動發布

## 完成！

✅ 恭喜！你現在有了一個完全自動化的、免費的、能賺廣告費的新聞評論網站。

### 接下來

1. **等待流量增長** — 6-12 個月達到 50k 月訪客
2. **考慮升級 AdSense** — 當達到要求後，可申請 Mediavine 等高 CPM 廣告網絡
3. **監控 GitHub Actions** — 確保每天自動發布成功
4. **定期檢查收入** — AdSense 會每月結算一次

---

有問題？查看 `SETUP.md` 或 `QUICK_START.md`。
