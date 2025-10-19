import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import io

# 設定頁面配置
st.set_page_config(
    page_title="🏨 台灣星級飯店地理查詢", 
    layout="wide",
    page_icon="🏨",
    initial_sidebar_state="collapsed"
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    /* 主要背景和色彩方案 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* 標題樣式 */
    .title-container {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .title-text {
        font-size: 3.5rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .subtitle-text {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* 搜尋區域樣式 */
    .search-container {
        background: rgba(255,255,255,0.95);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* 結果卡片樣式 */
    .result-card {
        background: rgba(255,255,255,0.95);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
    }
    
    /* 指標卡片樣式 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 表格樣式 */
    .hotel-table {
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .hotel-table th {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 1rem;
        text-align: center;
        font-weight: bold;
    }
    
    .hotel-table td {
        padding: 0.8rem;
        border-bottom: 1px solid #eee;
        text-align: center;
    }
    
    .hotel-table tr:hover {
        background-color: #f8f9ff;
    }
    
    /* 下載按鈕特殊樣式 */
    .download-btn {
        background: linear-gradient(45deg, #28a745, #20c997);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# 使用相對路徑，適用於雲端部署
CSV_FILE = "hotel_with_latlng.csv"

@st.cache_data
def download_hotel_data():
    """載入飯店資料，使用 pandas 處理"""
    try:
        if not os.path.exists(CSV_FILE):
            st.error(f"找不到飯店資料檔案！請確認 {CSV_FILE} 存在")
            return None
        df = pd.read_csv(CSV_FILE, encoding="utf-8")
        return df
    except Exception as e:
        st.error(f"載入資料時發生錯誤：{str(e)}")
        return None

def get_location_latlng(address):
    """取得地點的經緯度"""
    try:
        geolocator = Nominatim(user_agent="hotel_finder_streamlit")
        location = geolocator.geocode(address + ", Taiwan")  # 加入台灣，提高搜尋準確度
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except Exception as e:
        st.error(f"地理編碼時發生錯誤：{str(e)}")
        return None

def filter_star_hotels(df):
    """篩選星級飯店"""
    # 只要「標章」欄有「星級」兩字就視為星級旅館
    return df[df['標章'].astype(str).str.contains("星級", na=False)]

def create_result_table(hotels_df):
    """創建美化的結果表格 HTML"""
    html = """
    <div class="hotel-table">
    <table style='width: 100%; border-collapse: collapse;'>
    <thead>
        <tr class="header-row">
            <th>🏨 飯店名稱</th>
            <th>⭐ 星級標章</th>
            <th>📍 地址</th>
            <th>📞 聯絡電話</th>
            <th>📏 距離 (公里)</th>
        </tr>
    </thead>
    <tbody>
    """
    
    for _, hotel in hotels_df.iterrows():
        html += f"""
        <tr>
            <td style='font-weight: bold; color: #2E86AB;'>{hotel['飯店名稱']}</td>
            <td style='color: #F39C12; font-weight: bold;'>{hotel['星級標章']}</td>
            <td>{hotel['地址']}</td>
            <td>{hotel['電話']}</td>
            <td style='font-weight: bold; color: #E74C3C;'>{hotel['距離(公里)']}</td>
        </tr>
        """
    
    html += """
    </tbody>
    </table>
    </div>
    """
    return html

# 主頁面 - 美化的標題區域
st.markdown("""
<div class="title-container">
    <div class="title-text">🏨 台灣星級飯店地理查詢</div>
    <div class="subtitle-text">✨ 探索台灣最優質的住宿體驗 | 智能地理搜尋系統</div>
</div>
""", unsafe_allow_html=True)

# 功能特色展示
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🎯</h3>
        <p><strong>精準搜尋</strong></p>
        <p>10公里範圍內</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>⭐</h3>
        <p><strong>星級飯店</strong></p>
        <p>品質保證</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>📍</h3>
        <p><strong>距離排序</strong></p>
        <p>最近優先</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <h3>📥</h3>
        <p><strong>結果下載</strong></p>
        <p>CSV 格式</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 搜尋區域
st.markdown('<div class="search-container">', unsafe_allow_html=True)
st.markdown("### 🔍 開始您的飯店搜尋之旅")

# 載入資料（移到側邊欄外面，避免重複載入）
df = download_hotel_data()

# 在側邊欄顯示篩選選項
with st.sidebar:
    st.markdown("### 🎛️ 篩選設定")
    
    # 1. 星級篩選器
    st.markdown("#### ⭐ 星級篩選")
    if df is not None:
        # 獲取所有星級選項
        star_options = df['標章'].unique().tolist()
        star_options.sort()
        
        # 添加 "全部" 選項
        star_filter_options = ["🌟 全部星級"] + [f"⭐ {star}" for star in star_options if "星" in str(star)]
        
        selected_star = st.selectbox(
            "選擇星級標準",
            options=star_filter_options,
            help="篩選特定星級的飯店"
        )
    else:
        selected_star = "� 全部星級"
    
    # 2. 搜尋範圍調整
    st.markdown("#### 📍 搜尋範圍")
    distance_range = st.slider(
        "設定搜尋距離 (公里)",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        help="調整搜尋範圍，預設為 10 公里"
    )
    
    # 3. 飯店規模篩選（基於房間數）
    st.markdown("#### 🏨 飯店規模")
    if df is not None:
        # 基於房間數分類飯店規模
        room_filter = st.selectbox(
            "選擇飯店規模",
            options=[
                "🏨 全部規模",
                "🏠 精品小型 (50間以下)",
                "🏢 中型規模 (50-150間)",
                "🏨 大型飯店 (150-300間)",
                "🏰 超大型 (300間以上)"
            ],
            help="根據房間數量篩選飯店規模"
        )
    else:
        room_filter = "🏨 全部規模"
    
    # 4. 溫泉篩選
    st.markdown("#### ♨️ 溫泉標章")
    hot_spring_filter = st.checkbox(
        "🌊 僅顯示溫泉飯店",
        help="篩選有溫泉標章的飯店"
    )
    
    st.markdown("---")
    
    # 系統資訊
    st.markdown("### 📋 系統資訊")
    if df is not None:
        st.success(f"✅ 已載入 {len(df)} 筆飯店資料")
        
        # 顯示篩選統計
        filtered_count = len(df)
        if selected_star != "🌟 全部星級":
            star_name = selected_star.replace("⭐ ", "")
            filtered_count = len(df[df['標章'] == star_name])
        
        if hot_spring_filter:
            hot_spring_count = len(df[df['溫泉標章'] == '是'])
            st.info(f"♨️ 溫泉飯店：{hot_spring_count} 間")
        
        st.info(f"🌟 涵蓋全台星級飯店")
    else:
        st.error("❌ 資料載入失敗")

# 搜尋輸入區域
col1, col2 = st.columns([4, 1])

with col1:
    place = st.text_input(
        "🏙️ 請輸入您想搜尋的地點", 
        placeholder="例如：台北市信義區、高雄市左營區、台中市西屯區、桃園機場",
        help="💡 輸入您想查詢的地點，系統會搜尋附近10公里內的星級飯店"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # 對齊按鈕
    search_button = st.button("🔍 開始搜尋", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# 查詢處理
if search_button and place:
    if df is None:
        st.error("❌ 無法載入飯店資料，請稍後再試")
        st.stop()
    
    with st.spinner(f"🔍 正在搜尋 {place} 附近 {distance_range} 公里內的星級飯店..."):
        loc = get_location_latlng(place)
        
    if loc is None:
        st.error("❌ 查無此地點，請確認地名是否正確或嘗試更具體的地址")
        st.info("💡 建議輸入格式：縣市 + 區域（如：台北市信義區、高雄市左營區）")
    else:
        st.success(f"✅ 找到 {place} 的位置：緯度 {loc[0]:.6f}, 經度 {loc[1]:.6f}")
        
        # 應用篩選條件
        filtered_df = df.copy()
        
        # 1. 篩選星級飯店（基本篩選）
        filtered_df = filter_star_hotels(filtered_df)
        
        # 2. 應用星級篩選器
        if selected_star != "🌟 全部星級":
            star_name = selected_star.replace("⭐ ", "")
            filtered_df = filtered_df[filtered_df['標章'] == star_name]
        
        # 3. 應用溫泉篩選
        if hot_spring_filter:
            filtered_df = filtered_df[filtered_df['溫泉標章'] == '是']
        
        # 4. 應用房間數篩選（飯店規模）
        if room_filter != "🏨 全部規模":
            if room_filter == "🏠 精品小型 (50間以下)":
                filtered_df = filtered_df[filtered_df['房間數'].astype(float) < 50]
            elif room_filter == "🏢 中型規模 (50-150間)":
                filtered_df = filtered_df[
                    (filtered_df['房間數'].astype(float) >= 50) & 
                    (filtered_df['房間數'].astype(float) <= 150)
                ]
            elif room_filter == "🏨 大型飯店 (150-300間)":
                filtered_df = filtered_df[
                    (filtered_df['房間數'].astype(float) > 150) & 
                    (filtered_df['房間數'].astype(float) <= 300)
                ]
            elif room_filter == "🏰 超大型 (300間以上)":
                filtered_df = filtered_df[filtered_df['房間數'].astype(float) > 300]
        
        # 5. 搜尋指定範圍內的飯店
        hotels = []
        
        for _, row in filtered_df.iterrows():
            try:
                hotel_loc = (float(row['lat']), float(row['lng']))
                distance = geodesic(loc, hotel_loc).km
                if distance <= distance_range:  # 使用用戶設定的距離範圍
                    hotels.append({
                        "飯店名稱": row['旅宿名稱'],
                        "星級標章": row['標章'],
                        "地址": row['地址'],
                        "電話": row.get('電話或手機', 'N/A'),
                        "房間數": row.get('房間數', 'N/A'),
                        "溫泉": "♨️" if row.get('溫泉標章', '') == '是' else "",
                        "距離(公里)": round(distance, 2)
                    })
            except Exception:
                continue
        
        # 按距離排序
        hotels = sorted(hotels, key=lambda x: x['距離(公里)'])
        
        if hotels:
            # 美化的結果標題
            # 生成搜尋條件描述
            search_conditions = []
            if selected_star != "🌟 全部星級":
                search_conditions.append(selected_star.replace("⭐ ", ""))
            if hot_spring_filter:
                search_conditions.append("♨️ 溫泉飯店")
            if room_filter != "🏨 全部規模":
                search_conditions.append(room_filter.split(" ")[1])
            
            condition_text = " | ".join(search_conditions) if search_conditions else "全部類型"
            
            st.markdown(f"""
            <div class="result-card">
                <h2 style="color: #2E86AB; text-align: center; margin-bottom: 1rem;">
                    🎉 搜尋結果：{place} 附近 {distance_range}km 內的星級飯店
                </h2>
                <p style="text-align: center; color: #666; font-size: 1.1rem;">
                    篩選條件：{condition_text}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # 統計資訊 - 美化版
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>🏨</h3>
                    <h2>{len(hotels)}</h2>
                    <p>找到飯店 (間)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                closest_distance = min([h['距離(公里)'] for h in hotels])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>📍</h3>
                    <h2>{closest_distance:.1f}</h2>
                    <p>最近距離 (公里)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                furthest_distance = max([h['距離(公里)'] for h in hotels])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>�</h3>
                    <h2>{furthest_distance:.1f}</h2>
                    <p>最遠距離 (公里)</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                five_star_count = len([h for h in hotels if '五星' in h['星級標章']])
                st.markdown(f"""
                <div class="metric-card">
                    <h3>⭐</h3>
                    <h2>{five_star_count}</h2>
                    <p>五星飯店 (間)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # 顯示結果表格 - 使用 pandas dataframe
            df_result = pd.DataFrame(hotels)
            
            # 美化的表格顯示
            st.markdown("### 📊 詳細搜尋結果")
            st.dataframe(
                df_result, 
                use_container_width=True, 
                height=400,
                column_config={
                    "飯店名稱": st.column_config.TextColumn(
                        "🏨 飯店名稱",
                        help="星級飯店名稱",
                        width="large"
                    ),
                    "星級標章": st.column_config.TextColumn(
                        "⭐ 星級標章",
                        help="政府認證星級標章"
                    ),
                    "地址": st.column_config.TextColumn(
                        "📍 地址",
                        help="飯店完整地址",
                        width="large"
                    ),
                    "電話": st.column_config.TextColumn(
                        "📞 聯絡電話",
                        help="飯店聯絡電話"
                    ),
                    "房間數": st.column_config.NumberColumn(
                        "🏢 房間數",
                        help="飯店總房間數",
                        format="%d",
                        width="small"
                    ),
                    "溫泉": st.column_config.TextColumn(
                        "♨️ 溫泉",
                        help="是否有溫泉設施",
                        width="small"
                    ),
                    "距離(公里)": st.column_config.NumberColumn(
                        "📏 距離(公里)",
                        help="距離查詢地點的直線距離",
                        format="%.2f",
                        width="small"
                    )
                }
            )
            
            # 修復 CSV 編碼問題的下載功能
            def create_csv_download_pandas(df_data, location_name):
                # 使用 pandas to_csv 並確保編碼正確
                csv_string = df_data.to_csv(index=False, encoding='utf-8')
                # 添加 BOM 標記
                csv_with_bom = '\ufeff' + csv_string
                return csv_with_bom
            
            # 生成 CSV 內容
            csv_data = create_csv_download_pandas(df_result, place)
            
            # 美化的下載按鈕區域
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.download_button(
                    label="📥 下載查詢結果 (CSV)",
                    data=csv_data.encode('utf-8'),
                    file_name=f"{place}_星級飯店查詢結果_{len(hotels)}間.csv",
                    mime="text/csv; charset=utf-8",
                    use_container_width=True,
                    type="secondary"
                )
            
            # 額外資訊提示
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                <h4 style="color: #495057; margin-bottom: 0.5rem;">💡 使用小貼士</h4>
                <ul style="color: #6c757d; margin-bottom: 0;">
                    <li>點擊上方按鈕可下載完整搜尋結果 CSV 檔案</li>
                    <li>結果已按距離遠近排序，最近的飯店在最上方</li>
                    <li>表格支援排序和篩選功能</li>
                    <li>CSV 檔案採用 UTF-8 編碼，確保中文正常顯示</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # 美化的無結果頁面
            st.markdown(f"""
            <div class="result-card" style="text-align: center; padding: 3rem;">
                <h2 style="color: #e74c3c;">😔 很抱歉</h2>
                <p style="font-size: 1.2rem; color: #7f8c8d;">在 <strong>{place}</strong> {distance_range}公里內找不到符合條件的星級飯店</p>
                <div style="background: #fff3cd; padding: 1rem; border-radius: 10px; margin-top: 1rem;">
                    <h4 style="color: #856404;">💡 建議嘗試</h4>
                    <ul style="color: #856404; text-align: left;">
                        <li>增加搜尋範圍距離</li>
                        <li>調整星級篩選條件</li>
                        <li>取消溫泉或規模限制</li>
                        <li>搜尋其他鄰近地點</li>
                        <li>嘗試較大的城市中心區域</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 美化的頁面底部
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
           padding: 2rem; 
           border-radius: 15px; 
           text-align: center; 
           color: white; 
           margin-top: 3rem;">
    <h3 style="margin-bottom: 1rem;">🏨 台灣星級飯店地理查詢系統</h3>
    <div style="display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;">
        <div>
            <p style="margin: 0;"><strong>🎯 智能篩選</strong><br>多條件自定義搜尋</p>
        </div>
        <div>
            <p style="margin: 0;"><strong>⭐ 星級品質</strong><br>政府認證飯店分級</p>
        </div>
        <div>
            <p style="margin: 0;"><strong>� 彈性距離</strong><br>5-30公里自由調整</p>
        </div>
        <div>
            <p style="margin: 0;"><strong>♨️ 溫泉特色</strong><br>溫泉飯店專門篩選</p>
        </div>
    </div>
    <hr style="border-color: rgba(255,255,255,0.3); margin: 1.5rem 0;">
    <p style="margin: 0; opacity: 0.9;">
        💻 技術支援：Streamlit + Pandas + Geopy | 
        📊 資料來源：政府開放資料平台 | 
        <a href="https://github.com/stevenhaung7/taiwan-hotel-finder" target="_blank" 
           style="color: #FFE4B5; text-decoration: none;">
           🔗 GitHub 開源專案
        </a>
    </p>
</div>
""", unsafe_allow_html=True)