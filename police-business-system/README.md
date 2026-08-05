# 業務管理系統（Phase 1 / MVP）

警察機關行政單位用的業務管理系統，讓每位業務承辦人一目了然自己名下有哪些業務、
規定/計畫的最新版本與歷史版本、敘獎週期到期狀況，並在人員異動時完整保留交接紀錄，
避免換人辦理時斷點。部署在 Synology NAS（DS425+）的 Docker 環境上，僅供機關內網存取。

## 範圍

**這次做的（Phase 1）**
- 業務樹狀結構（不限層數，只有最底層節點才掛實際資料）
- 規定/計畫版本管理（完整版本歷史，可回溯查閱）
- 敘獎週期追蹤與狀態燈號提醒（可開始敘獎 / 即將逾期 / 已逾期）
- 公文/補充資料上傳＋手動重點摘要，掃描檔自動 OCR 建立可搜尋文字
- 人員異動（交接）：整批移轉業務並保留完整承辦歷程
- 業務樹結構異動歷程（管理者可查）

**之後才做（Phase 2，這次不做）**
- 分析已上傳舊檔，自動產生獎勵建議名冊、公文簽文初稿
- 因為 DS425+ 沒有獨立顯卡，Phase 2 若要上地端 LLM，需另外評估是否要外接一台
  有顯卡的內網主機；NAS 本身只適合跑 OCR 這類輕量任務

## 角色與權限

| 角色 | 權限 |
|---|---|
| 管理者（科長/股長） | 總覽全部業務進度、建立頂層業務大類、執行人員異動（交接）、查看結構異動歷程、指派/移除承辦人 |
| 承辦人 | 只看/編輯自己身兼主辦或協辦的節點；可在自己已有份的節點下自行新增子節點（不用核准）；上傳規定/計畫/公文並填寫摘要 |

帳號密碼系統自建（8 人規模不需要接 AD/LDAP），僅限內網存取，不對外網開放。

## 資料模型

- `BusinessNode`：不限層數的業務樹。只有沒有子節點的「葉節點」才是實際的工作項目，
  掛規定/計畫、敘獎週期、附件、承辦人指派；上層節點純粹是分類用的資料夾。
- `NodeAssignment`：節點目前的承辦人指派（主辦/協辦）。
- `AssignmentHistory`：完整承辦歷程（節點—承辦人—起訖日期），交接時只結束舊紀錄、
  新增新紀錄，不覆蓋。
- `RegulationVersion`：規定/計畫的每一次上傳都是新版本，前一版自動標記失效日期。
- `AwardCycle` / `AwardRecord`：敘獎週期設定（季/半年/年＋起算日），系統自動算出
  每期的結束日與「結束日 + 1 個月緩衝期」的最終期限，並依剩餘天數計算狀態燈號。
- `Attachment`：公文/補充資料，含手動填寫的重點摘要；掃描檔會另外跑 OCR。
- `NodeChangeLog`：業務樹結構的新增/改名/搬移紀錄。

詳見 `app/models.py`。

## 技術棧

- **後端**：FastAPI + SQLAlchemy，SQLite 資料庫（8 人規模足夠，檔案型資料庫備份簡單）
- **前端**：純 HTML + Vanilla JS（`app/static/`），呼叫後端 JSON API，不上重的前端框架
- **OCR**：Tesseract（繁中語言包），只有在抽不到文字層時才觸發
- **部署**：Docker Compose，跑在 Synology DS425+ 的 Container Manager 上

## 本機開發

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATA_DIR=./data uvicorn app.main:app --reload
python seed.py admin admin123 管理者姓名   # 建立第一個管理者帳號
```

開瀏覽器打開 `http://localhost:8000/static/index.html`。

## 部署到 NAS

```bash
docker compose up -d --build
docker compose exec app python seed.py admin <密碼> <姓名>
```

資料庫檔案與上傳檔案都會存在掛載的 `./data` 目錄，建議搭配 Synology Hyper Backup
備份這個目錄。

## 已知限制 / 待補事項

- 目前沒有前端的權限驗證 UI 細節（例如管理者專用頁面），API 層已有權限檢查，
  之後可依實際使用情況加強前端提示。
- `AwardRecord` 是在查詢時（`ensure_records_up_to_today`）動態補齊，量體變大後
  可以改成排程（APScheduler）每日跑一次，先產生好紀錄再查詢。
- 尚未寫自動化測試，建議之後補上 API 層的 pytest 測試。
