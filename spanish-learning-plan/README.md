# 2030 世界盃西語學習計畫

零基礎自學西班牙語，目標在 2030 世界盃前達到 B1-B2 程度，可應付球場、旅遊與日常對話。
每日 30-60 分鐘，全部使用免費資源，純前端工具、資料只存在瀏覽器本機（免登入）。

## 功能

- **今日任務**：每日固定任務清單＋打卡、連續 streak
- **進度**：五階段學習藍圖（入門 → A2 → B1 → B2 → 世足生存會話），含 3-6 個月檢核點
- **單字卡**：Leitner box 間隔複習系統，依階段解鎖題庫（含世足/足球主題單元）
- **口說**：從「A1 → A2」階段起，每週對話次數／時長追蹤
- **資源庫**：Duolingo、YouTube、Podcast、語言交換App 等免費資源，依階段推薦
- **設定**：瀏覽器提醒通知、JSON 匯出／匯入備份

## 開發

```bash
npm install
npm run dev      # 本機開發伺服器
npm run build    # 產出 dist/
npm run preview  # 預覽 build 結果
```

## 部署

推送到 `main` 分支（`spanish-learning-plan/**` 有變更時）會透過
`.github/workflows/deploy-spanish-plan.yml` 自動 build 並部署到 GitHub Pages。

第一次啟用需要到 repo 的 **Settings → Pages → Build and deployment → Source**
選擇 **GitHub Actions**。

`vite.config.js` 已將 `base` 設為 `/products/`，對應
`https://<你的帳號>.github.io/products/` 這個網址；若改用其他 repo 名稱或自訂網域，
記得同步調整 `base`。
