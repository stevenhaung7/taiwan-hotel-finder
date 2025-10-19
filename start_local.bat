@echo off
echo 🚀 啟動台灣星級飯店查詢系統...

REM 檢查是否存在虛擬環境
if not exist ".venv" (
    echo ❌ 找不到虛擬環境，請先執行 python -m venv .venv
    pause
    exit /b 1
)

REM 啟動虛擬環境
call .venv\Scripts\activate.bat

REM 檢查 geopy 是否已安裝
python -c "import geopy" 2>nul
if errorlevel 1 (
    echo 📦 安裝 geopy...
    pip install geopy>=2.3.0 --quiet
)

REM 檢查 streamlit 是否已安裝
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚠️  Streamlit 未安裝，啟動 Lite 版本測試...
    python start_lite_version.py
    pause
    exit /b 0
)

REM 啟動 Streamlit 應用程式（優先使用 lite 版本）
echo 🌐 啟動 Streamlit 應用程式 (Lite版本)...
echo 📝 請在瀏覽器中開啟 http://localhost:8501
echo ⏹️  按 Ctrl+C 停止應用程式
echo ℹ️  使用 Lite 版本避免 Windows 編譯問題
echo.

streamlit run hotel_finder_streamlit_lite.py --server.port=8501

pause