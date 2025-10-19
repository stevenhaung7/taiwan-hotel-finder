import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os

# 設定頁面寬度為最大（重要！）
st.set_page_config(
    page_title="台灣星級飯店地理查詢", 
    layout="wide",
    page_icon="🏨",
    initial_sidebar_state="collapsed"
)

# 使用相對路徑，適用於雲端部署
CSV_FILE = "hotel_with_latlng.csv"

@st.cache_data
def download_hotel_data():
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
    # 只要「標章」欄有「星級」兩字就視為星級旅館
    return df[df['標章'].astype(str).str.contains("星級", na=False)]

# 主頁面
st.title("🏨 台灣星級飯店地理查詢")
st.markdown("### 🔍 查詢您附近的星級飯店")

# 在側邊欄顯示應用程式資訊
with st.sidebar:
    st.header("📋 應用程式資訊")
    st.write("- 🎯 搜尋範圍：10公里內")
    st.write("- ⭐ 僅顯示星級飯店")
    st.write("- 📍 按距離排序")
    
    # 載入資料
    df = download_hotel_data()
    if df is not None:
        st.success(f"已載入 {len(df)} 筆飯店資料")

# 使用更好的 UI 佈局
col1, col2 = st.columns([3, 1])

with col1:
    place = st.text_input(
        "請輸入地點", 
        placeholder="例如：高雄市左營區、台北市信義區、台中市西屯區",
        help="輸入您想查詢的地點，系統會搜尋附近10公里內的星級飯店"
    )

with col2:
    st.markdown("&nbsp;")  # 空白行用於對齊
    search_button = st.button("🔍 查詢飯店", type="primary", use_container_width=True)

# 查詢處理
if search_button and place:
    if df is None:
        st.error("❌ 無法載入飯店資料，請稍後再試")
        st.stop()
    
    with st.spinner(f"🔍 正在搜尋 {place} 附近的星級飯店..."):
        loc = get_location_latlng(place)
        
    if loc is None:
        st.error("❌ 查無此地點，請確認地名是否正確或嘗試更具體的地址")
        st.info("💡 建議輸入格式：縣市 + 區域（如：台北市信義區、高雄市左營區）")
    else:
        st.success(f"✅ 找到 {place} 的位置：緯度 {loc[0]:.6f}, 經度 {loc[1]:.6f}")
        
        # 篩選星級飯店
        star_df = filter_star_hotels(df)
        hotels = []
        
        for _, row in star_df.iterrows():
            try:
                hotel_loc = (float(row['lat']), float(row['lng']))
                distance = geodesic(loc, hotel_loc).km
                if distance <= 10:
                    hotels.append({
                        "飯店名稱": row['旅宿名稱'],
                        "星級標章": row['標章'],
                        "地址": row['地址'],
                        "電話": row.get('電話或手機', 'N/A'),
                        "距離(公里)": round(distance, 2)
                    })
            except Exception:
                continue
        
        # 按距離排序
        hotels = sorted(hotels, key=lambda x: x['距離(公里)'])
        
        if hotels:
            st.markdown(f"### 🏨 {place} 附近 10 公里內的星級飯店")
            
            # 添加統計資訊
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🏨 找到飯店", f"{len(hotels)} 間")
            with col2:
                closest_distance = min([h['距離(公里)'] for h in hotels])
                st.metric("📍 最近距離", f"{closest_distance:.1f} 公里")
            with col3:
                furthest_distance = max([h['距離(公里)'] for h in hotels])
                st.metric("📍 最遠距離", f"{furthest_distance:.1f} 公里")
            with col4:
                five_star_count = len([h for h in hotels if '五星' in h['星級標章']])
                st.metric("⭐ 五星飯店", f"{five_star_count} 間")
            
            st.markdown("---")
            
            # 顯示結果表格
            df_result = pd.DataFrame(hotels)
            st.dataframe(
                df_result, 
                use_container_width=True, 
                height=400,
                column_config={
                    "距離(公里)": st.column_config.NumberColumn(
                        "距離(公里)",
                        help="距離查詢地點的直線距離",
                        format="%.1f"
                    )
                }
            )
            
            # 下載功能
            csv = df_result.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下載查詢結果 (CSV)",
                data=csv,
                file_name=f"{place}_星級飯店查詢結果.csv",
                mime="text/csv"
            )
            
        else:
            st.warning(f"😔 很抱歉，在 {place} 10公里內找不到星級飯店")
            st.info("💡 建議：試試其他鄰近地點，或考慮搜尋較大的城市中心區域")

# 頁面底部資訊
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏨 台灣星級飯店地理查詢系統 | 資料來源：政府開放資料 | 
    <a href='https://github.com/your-repo' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)