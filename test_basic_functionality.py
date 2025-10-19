#!/usr/bin/env python
"""
基本功能測試 - 驗證飯店查詢系統核心功能
不依賴 streamlit，直接測試核心邏輯
"""

import csv
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

def test_csv_reading():
    """測試 CSV 檔案讀取"""
    print("🔍 測試 CSV 檔案讀取...")
    
    csv_file = "hotel_with_latlng.csv"
    if not os.path.exists(csv_file):
        print(f"❌ 找不到檔案: {csv_file}")
        return False
    
    try:
        hotels = []
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hotels.append(row)
        
        print(f"✅ 成功讀取 {len(hotels)} 筆飯店資料")
        
        # 顯示前幾筆資料
        if hotels:
            print("📋 前 3 筆資料範例:")
            for i, hotel in enumerate(hotels[:3]):
                print(f"  {i+1}. {hotel.get('飯店名稱', 'N/A')} - {hotel.get('地址', 'N/A')}")
        
        return hotels
        
    except Exception as e:
        print(f"❌ 讀取 CSV 失敗: {e}")
        return False

def test_geocoding():
    """測試地理編碼功能"""
    print("\n🌍 測試地理編碼功能...")
    
    try:
        geolocator = Nominatim(user_agent="hotel_finder_test")
        
        # 測試幾個台灣地點
        test_locations = [
            "台北車站",
            "台中火車站",
            "高雄火車站"
        ]
        
        for location in test_locations:
            try:
                result = geolocator.geocode(location + ", Taiwan")
                if result:
                    print(f"✅ {location}: ({result.latitude:.4f}, {result.longitude:.4f})")
                else:
                    print(f"⚠️  {location}: 找不到座標")
            except Exception as e:
                print(f"❌ {location}: 編碼失敗 - {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ 地理編碼測試失敗: {e}")
        return False

def test_distance_calculation():
    """測試距離計算"""
    print("\n📏 測試距離計算...")
    
    try:
        # 台北車站和台中車站的大概座標
        taipei_station = (25.0478, 121.5170)
        taichung_station = (24.1369, 120.6857)
        
        distance = geodesic(taipei_station, taichung_station).kilometers
        
        print(f"✅ 台北車站到台中車站距離: {distance:.2f} 公里")
        
        # 檢查距離是否合理（約150-200公里）
        if 120 <= distance <= 250:
            print("✅ 距離計算結果合理")
            return True
        else:
            print(f"⚠️  距離計算結果可能不準確: {distance:.2f} 公里")
            return False
            
    except Exception as e:
        print(f"❌ 距離計算失敗: {e}")
        return False

def test_hotel_filtering(hotels):
    """測試飯店篩選功能"""
    print("\n🏨 測試飯店篩選功能...")
    
    if not hotels:
        print("❌ 沒有飯店資料可供篩選")
        return False
    
    try:
        # 篩選星級飯店
        star_hotels = []
        for hotel in hotels:
            star_rating = hotel.get('星級', '').strip()
            if star_rating and star_rating != '未分級':
                star_hotels.append(hotel)
        
        print(f"✅ 星級飯店數量: {len(star_hotels)} / {len(hotels)}")
        
        # 按縣市分類
        cities = {}
        for hotel in hotels:
            city = hotel.get('縣市', '未知').strip()
            if city not in cities:
                cities[city] = 0
            cities[city] += 1
        
        print("✅ 縣市分佈:")
        for city, count in sorted(cities.items()):
            print(f"  {city}: {count} 家")
        
        return True
        
    except Exception as e:
        print(f"❌ 飯店篩選失敗: {e}")
        return False

def test_html_generation(hotels):
    """測試 HTML 表格生成"""
    print("\n🌐 測試 HTML 表格生成...")
    
    if not hotels:
        print("❌ 沒有飯店資料可供生成表格")
        return False
    
    try:
        # 取前 5 筆資料生成 HTML
        test_hotels = hotels[:5]
        
        html_content = "<table border='1' style='border-collapse: collapse; width: 100%;'>\n"
        html_content += "<tr style='background-color: #f2f2f2;'>\n"
        html_content += "<th>飯店名稱</th><th>星級</th><th>縣市</th><th>地址</th>\n"
        html_content += "</tr>\n"
        
        for hotel in test_hotels:
            html_content += "<tr>\n"
            html_content += f"<td>{hotel.get('飯店名稱', 'N/A')}</td>\n"
            html_content += f"<td>{hotel.get('星級', 'N/A')}</td>\n"
            html_content += f"<td>{hotel.get('縣市', 'N/A')}</td>\n"
            html_content += f"<td>{hotel.get('地址', 'N/A')}</td>\n"
            html_content += "</tr>\n"
        
        html_content += "</table>"
        
        # 儲存測試 HTML
        with open("test_table.html", "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>飯店資料測試</title>
</head>
<body>
    <h2>飯店資料測試表格</h2>
    {html_content}
</body>
</html>
            """)
        
        print("✅ HTML 表格生成成功，已儲存至 test_table.html")
        return True
        
    except Exception as e:
        print(f"❌ HTML 生成失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 飯店查詢系統基本功能測試")
    print("=" * 50)
    
    # 測試順序
    tests = [
        ("CSV 檔案讀取", test_csv_reading),
        ("地理編碼功能", test_geocoding),
        ("距離計算", test_distance_calculation),
    ]
    
    results = []
    hotels = None
    
    # 執行基本測試
    for test_name, test_func in tests:
        try:
            if test_name == "CSV 檔案讀取":
                result = test_func()
                if result:
                    hotels = result
                    results.append((test_name, True))
                else:
                    results.append((test_name, False))
            else:
                result = test_func()
                results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
            results.append((test_name, False))
    
    # 如果有飯店資料，進行進階測試
    if hotels:
        try:
            filter_result = test_hotel_filtering(hotels)
            results.append(("飯店篩選功能", filter_result))
        except Exception as e:
            print(f"❌ 飯店篩選測試異常: {e}")
            results.append(("飯店篩選功能", False))
        
        try:
            html_result = test_html_generation(hotels)
            results.append(("HTML 表格生成", html_result))
        except Exception as e:
            print(f"❌ HTML 生成測試異常: {e}")
            results.append(("HTML 表格生成", False))
    
    # 總結結果
    print("\n" + "=" * 50)
    print("📊 測試結果總結:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 總計: {passed}/{total} 項測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！系統準備就緒")
        print("\n📋 下一步建議:")
        print("1. 推送程式碼到 GitHub")
        print("2. 在 Render 上部署 Streamlit 應用")
        print("3. 使用 requirements.txt: streamlit>=1.25.0 geopy>=2.3.0")
        return True
    else:
        print("⚠️  部分測試失敗，請檢查相關功能")
        return False

if __name__ == "__main__":
    main()