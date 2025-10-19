# Render 部署指南

## 準備工作

1. 確保您的專案檔案都已準備完成：
   - `hotel_finder_streamlit.py` - 主應用程式
   - `hotel_with_latlng.csv` - 酒店資料檔案
   - `requirements.txt` - Python 套件清單
   - `README.md` - 專案說明

## 部署步驟

### 1. 建立 Git 儲存庫並推送程式碼

```bash
# 在專案目錄中初始化 Git
git init

# 加入所有檔案
git add .

# 提交變更
git commit -m "Initial commit: Taiwan Hotel Finder Streamlit App"

# 連接到 GitHub 儲存庫（請先在 GitHub 建立新儲存庫）
git remote add origin https://github.com/YOUR_USERNAME/taiwan-hotel-finder.git

# 推送程式碼
git push -u origin main
```

### 2. 在 Render 上部署

1. **註冊/登入 Render**
   - 前往 https://render.com
   - 使用 GitHub 帳號登入

2. **建立新的 Web Service**
   - 點擊 "New +" 按鈕
   - 選擇 "Web Service"
   - 連接您的 GitHub 儲存庫

3. **配置部署設定**
   - **Name**: `taiwan-hotel-finder`
   - **Environment**: `Python 3`
   - **Region**: `Singapore` (亞洲用戶建議)
   - **Branch**: `main`
   - **Build Command**: `pip install --no-cache-dir -r requirements.txt`
   - **Start Command**: `streamlit run hotel_finder_streamlit.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false --server.headless=true`

4. **環境變數設定**
   - 通常不需要特別設定，Render 會自動處理

5. **部署**
   - 點擊 "Create Web Service"
   - 等待部署完成（通常需要 5-10 分鐘）

### 3. 驗證部署

部署完成後：
1. Render 會提供一個 `.onrender.com` 的網址
2. 點擊網址測試應用程式
3. 確認可以正常查詢酒店

## 後續更新

要更新應用程式：
1. 修改程式碼
2. 提交並推送到 GitHub
3. Render 會自動重新部署

## 注意事項

- 第一次部署可能需要較長時間
- 免費帳戶有使用限制
- 如果遇到記憶體問題，考慮優化 CSV 讀取方式
- 確保 CSV 檔案大小適中，避免超出限制

## 故障排除

如果部署失敗：
1. 檢查 Render 的日誌
2. 確認 requirements.txt 格式正確
3. 驗證程式碼在本機運行正常
4. 檢查檔案路徑是否正確（使用相對路徑）