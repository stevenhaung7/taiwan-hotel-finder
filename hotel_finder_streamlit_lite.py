import streamlit as st
import csv
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
    """載入飯店資料，使用原生 CSV 模組避免 pandas 依賴"""
    try:
        if not os.path.exists(CSV_FILE):
            st.error(f"找不到飯店資料檔案！請確認 {CSV_FILE} 存在")
            return None
            
        hotels = []
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hotels.append(row)
        
        return hotels
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

def filter_star_hotels(hotels_data):
    """篩選星級飯店"""
    if not hotels_data:
        return []
    
    star_hotels = []
    for hotel in hotels_data:
        badge = hotel.get('標章', '').strip()
        if '星級' in badge:
            star_hotels.append(hotel)
    
    return star_hotels

def create_result_table(hotels):
    """創建結果表格的 HTML"""
    if not hotels:
        return ""
    
    html = """
    <div style='overflow-x: auto;'>
    <table style='width: 100%; border-collapse: collapse; margin: 20px 0;'>
    <thead style='background-color: #f0f2f6;'>
    <tr>
    <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>飯店名稱</th>
    <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>星級標章</th>
    <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>地址</th>
    <th style='padding: 12px; text-align: left; border: 1px solid #ddd;'>電話</th>
    <th style='padding: 12px; text-align: center; border: 1px solid #ddd;'>距離(公里)</th>
    </tr>
    </thead>
    <tbody>
    """
    
    for i, hotel in enumerate(hotels):
        bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
        html += f"""
        <tr style='background-color: {bg_color};'>
        <td style='padding: 10px; border: 1px solid #ddd;'><strong>{hotel['飯店名稱']}</strong></td>
        <td style='padding: 10px; border: 1px solid #ddd;'><span style='color: #ff6b6b;'>{hotel['星級標章']}</span></td>
        <td style='padding: 10px; border: 1px solid #ddd; font-size: 0.9em;'>{hotel['地址']}</td>
        <td style='padding: 10px; border: 1px solid #ddd;'>{hotel['電話']}</td>
        <td style='padding: 10px; border: 1px solid #ddd; text-align: center; font-weight: bold; color: #4CAF50;'>{hotel['距離(公里)']}</td>
        </tr>
        """
    
    html += """
    </tbody>
    </table>
    </div>
    """
    return html

# 主頁面
st.title("🏨 台灣星級飯店地理查詢")
st.markdown("### 🔍 查詢您附近的星級飯店")

# 在側邊欄顯示應用程式資訊
with st.sidebar:
    st.header("📋 應用程式資訊")
    st.write("- 🎯 搜尋範圍：10公里內")
    st.write("- ⭐ 僅顯示星級飯店")
    st.write("- 📍 按距離排序")
    st.write("- 🚀 輕量版本（無需 pandas）")
    
    # 載入資料
    hotels_data = download_hotel_data()
    if hotels_data is not None:
        st.success(f"已載入 {len(hotels_data)} 筆飯店資料")

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
    if hotels_data is None:
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
        star_hotels_data = filter_star_hotels(hotels_data)
        
        if not star_hotels_data:
            st.warning("⚠️ 資料中沒有找到星級飯店")
            st.stop()
            
        hotels = []
        
        for hotel in star_hotels_data:
            try:
                lat = float(hotel.get('lat', 0))
                lng = float(hotel.get('lng', 0))
                
                if lat == 0 or lng == 0:
                    continue
                    
                hotel_loc = (lat, lng)
                distance = geodesic(loc, hotel_loc).km
                
                if distance <= 10:
                    hotels.append({
                        "飯店名稱": hotel.get('旅宿名稱', 'N/A'),
                        "星級標章": hotel.get('標章', 'N/A'),
                        "地址": hotel.get('地址', 'N/A'),
                        "電話": hotel.get('電話或手機', 'N/A'),
                        "距離(公里)": round(distance, 2)
                    })
            except Exception as e:
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
            table_html = create_result_table(hotels)
            st.markdown(table_html, unsafe_allow_html=True)
            
            # 下載功能
            csv_content = "飯店名稱,星級標章,地址,電話,距離(公里)\n"
            for hotel in hotels:
                csv_content += f'"{hotel["飯店名稱"]}","{hotel["星級標章"]}","{hotel["地址"]}","{hotel["電話"]}",{hotel["距離(公里)"]}\n'
            
            st.download_button(
                label="📥 下載查詢結果 (CSV)",
                data=csv_content.encode('utf-8-sig'),
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
    <p>🏨 台灣星級飯店地理查詢系統 (輕量版) | 資料來源：政府開放資料 | 
    <a href='https://github.com/your-repo' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)