#!/bin/bash
# Render 部署啟動腳本
# 更新: 2025-10-19 - 美化標準版

echo "=== 台灣星級飯店查詢系統 ==="
echo "啟動美化標準版本..."
echo "使用文件: hotel_finder_streamlit.py"

# 啟動 Streamlit 應用 (標準版)
streamlit run hotel_finder_streamlit.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.headless=true