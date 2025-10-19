import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os

CSV_FILE = r"C:\hotel_finder_local\hotel_with_latlng.csv"  # 本機檔案路徑

def download_hotel_data():
    if not os.path.exists(CSV_FILE):
        messagebox.showerror("找不到飯店資料檔案！", f"請確認 {CSV_FILE} 存在")
        return None
    df = pd.read_csv(CSV_FILE, encoding="utf-8")
    return df

def get_location_latlng(address):
    geolocator = Nominatim(user_agent="hotel_finder_gui")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None

def filter_star_hotels(df):
    return df[df['標章'].astype(str).str.contains("星級", na=False)]

def clear_tree():
    for item in tree.get_children():
        tree.delete(item)

def query():
    place = entry.get()
    loc = get_location_latlng(place)
    if loc is None:
        messagebox.showerror("查無此地點", "請輸入正確地點")
        return
    df = download_hotel_data()
    if df is None:
        return
    df = filter_star_hotels(df)
    hotels = []
    for _, row in df.iterrows():
        try:
            hotel_loc = (float(row['lat']), float(row['lng']))
            distance = geodesic(loc, hotel_loc).km
            if distance <= 10:
                hotels.append([
                    row['旅宿名稱'],
                    row['標章'],
                    row['地址'],
                    f"{distance:.2f}"
                ])
        except:
            continue
    hotels = sorted(hotels, key=lambda x: float(x[3]))
    clear_tree()
    if not hotels:
        messagebox.showinfo("查詢結果", "查無10公里內星級飯店")
        return
    for h in hotels:
        tree.insert('', tk.END, values=h)

root = tk.Tk()
root.title("台灣星級飯店地理查詢 (tkinter表格版)")
root.geometry("900x550")

tk.Label(root, text="輸入地點：").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

tk.Button(root, text="查詢", command=query).pack(pady=5)

# 建立表格
columns = ("旅宿名稱", "星級標章", "地址", "距離(km)")
tree = ttk.Treeview(root, columns=columns, show="headings", height=20)
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=200 if col != "地址" else 350, anchor="w")
tree.pack(fill="both", expand=True, padx=10, pady=10)

root.mainloop()