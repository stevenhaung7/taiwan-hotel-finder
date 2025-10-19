#!/bin/bash
# Render 部署啟動腳本

# 啟動 Streamlit 應用
streamlit run hotel_finder_streamlit.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false \
  --server.headless=true