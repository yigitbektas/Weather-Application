import requests
import tkinter as tk
from tkinter import messagebox
import base64


BG  ="#a8d4f5"
CARD="#c5e3fa"
TEXT_DARK  = "#1a4d7a"
ENTRY_BG   = "#daeefb"
BORDER     = "#90c4e8"
FAV_BG = "#7cb9f7"
API_KEY = "c6f1ccb36bb11f712321add99d6a954c"

def get_weather_emoji(weather_main):
    weather_main = weather_main.lower()
    if "clear" in weather_main: return "☀️"
    elif "cloud" in weather_main: return "☁️"
    elif "rain" in weather_main or "drizzle" in weather_main: return "🌧️"
    elif "snow" in weather_main: return "❄️"
    elif "thunderstorm" in weather_main: return "⛈️"
    else: return "🌤️"

def get_favorite_weather(city_name):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Sıcaklığı tam sayıya yuvarlayalım (Örn: 28.6 yerine 28 veya 29)
            temp = int(round(data["main"]["temp"])) 
            weather_main = data["weather"][0]["main"] # "Clouds", "Clear" vb.
            emoji = get_weather_emoji(weather_main)
            return temp, emoji
        else:
            return "--", "❓" # Şehir bulunamazsa
    except:
        return "--", "❓" # İnternet yoksa veya hata çıkarsa


def fetch_weather(event = None):
    city = search_entry.get()

    if city == "Search..." or city.strip() == "":
        return

    appid = API_KEY

    # Sıcaklığı Celsius olarak almak için "&units=metric" parametresini ekledik
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={appid}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()

        # Eğer yanıt 200 (Başarılı) değilse, hata mesajını göster
        if response.status_code != 200:
            messagebox.showerror("API Hatası", f"Hata mesajı: {data.get('message', 'Bilinmeyen hata')}")
            return

        city_name = data["name"].upper()
        city_name = city_name.replace(" PROVINCE", "").replace(" CITY", "").strip()
        country = data["sys"]["country"]
        
        temp = int(round(data["main"]["temp"]))
        feels_like = int(round(data["main"]["feels_like"]))
        humidity = data["main"]["humidity"]
        
        # Rüzgar hızını m/s'den km/h'ye çevirip yuvarlıyoruz
        wind_speed_kmh = int(round(data["wind"]["speed"] * 3.6)) 
        
        weather_desc = data["weather"][0]["description"].title()
        weather_main = data["weather"][0]["main"]
        emoji = get_weather_emoji(weather_main)

        # --- ARAYÜZÜ (SAĞ PANELİ) GÜNCELLEME ---
        lbl_city_name.config(text=city_name)
        lbl_country_name.config(text=country)
        lbl_big_icon.config(text=emoji)
        lbl_big_temp.config(text=f"{temp}°C")
        lbl_desc.config(text=weather_desc)
        
        lbl_humidity.config(text=f"Humidity: {humidity}%")
        lbl_wind.config(text=f"Wind: {wind_speed_kmh} km/h")
        lbl_feels_like.config(text=f"Feels Like: {feels_like}°C")

        root.focus_set() # Arama bitince imleci arama kutusundan çıkar

    except Exception as e:
        # Kod tabanlı bir hata oluşursa gerçek hatayı konsola yazdıralım
        print(f"Beklenmeyen Hata: {e}")
        messagebox.showerror("Error", "Unable to fetch weather data")


def _clear_placeholder(event):
    if search_entry.get() == "Search...":
        search_entry.delete(0, "end")


def _add_placeholder(event):
    if search_entry.get() == "":
        search_entry.insert(0, "Search...")

def create_city_card(parent, city_name, icon, temp):
    # Dış Çerçeve (Mavi Kart)
    card = tk.Frame(parent, bg=FAV_BG, height=60)
    card.pack_propagate(False) # Kartın içindeki yazılara göre küçülmesini engelle, 60px yüksekliği koru
    card.pack(fill="x", pady=6, padx=15) # fill="x" ile sağa sola yasla


    lbl_delete = tk.Label(card, text="❌", font=("Segoe UI Emoji", 10), bg=FAV_BG, fg="#ff4d4d", cursor="hand2")
    lbl_delete.pack(side="right", padx=(0, 10))

    # Şehir Adı (En sola yapıştırıyoruz)
    tk.Label(card, text=city_name, font=("Segoe UI", 16, "bold"), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="left", padx=20)

    # Sıcaklık Değeri (En sağa yapıştırıyoruz - sağdan sola doğru eklenecek)
    tk.Label(card, text=f"{temp}°C", font=("Segoe UI", 16), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="right", padx=20)

    # Hava Durumu İkonu (Sıcaklık değerinin hemen soluna yerleşir)
    tk.Label(card, text=icon, font=("Segoe UI Emoji", 16), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="right", padx=5)
    
    def on_card_click(event):
        # 1. Arama kutusunun içini temizle
        search_entry.delete(0, "end")
        # 2. Tıklanan şehrin adını arama kutusuna yaz
        search_entry.insert(0, city_name)
        # 3. Sağ tarafı güncellemek için mevcut fetch_weather fonksiyonunu çağır
        fetch_weather()

    def remove_from_favorites(event):
        if city_name in favorite_cities:
            favorite_cities.remove(city_name)
            update_favorites_ui() # Arayüzü güncelle

    # Silme ikonuna silme fonksiyonunu bağla
    lbl_delete.bind("<Button-1>", remove_from_favorites)    

    # Tıklama olayını karta ve içindeki tüm etiketlere bağla
    card.bind("<Button-1>", on_card_click)
    card.config(cursor="hand2") # Fare üzerine gelince el işareti çıksın (UX için iyi bir detay)
    
    # Kartın içindeki yazılara (Label'lara) tıklanırsa da çalışması için döngü
    for child in card.winfo_children():
        child.bind("<Button-1>", on_card_click)
        child.config(cursor="hand2")
    
         



root = tk.Tk()
root.title("Weather App")
root.geometry("820x620")
root.configure(background=BG)


left_frame = tk.Frame(root, bg = CARD, width = 340, height = 560, relief = "groove")
left_frame.pack(side = "left", expand = "yes",padx = (0,16), pady = 0)
left_frame.pack_propagate(False)

right_frame = tk.Frame(root, bg = CARD, width = 420, height = 560)
right_frame.pack(side = "right",expand = "yes")
right_frame.pack_propagate(False)



# Create and configure labels and entry fields
weather_label = tk.Label(left_frame, text="Hava Durumu", font=("Segoe UI", 20, "bold"), bg=CARD, fg=TEXT_DARK)
weather_label.pack(pady= (20, 4))

image_label = tk.Label(left_frame, text="⛅", font=("Segoe UI Emoji", 48),
                 bg=CARD).pack(pady=(0, 8))


search_frame = tk.Frame(left_frame, bg=ENTRY_BG, bd=4, highlightbackground=BORDER, highlightthickness=1)
search_frame.pack(padx=24, pady=(0, 12), fill="x")

search_entry = tk.Entry(search_frame, bg=ENTRY_BG, fg=TEXT_DARK, font=("Segoe UI", 12), bd=0,
                        insertbackground=TEXT_DARK, relief="flat")
search_entry.insert(0,"Search...")

tk.Label(search_frame, text="🔍", bg=ENTRY_BG,
                 font=("Segoe UI Emoji", 12)).pack(side="left", padx=(1, 0))

search_entry.pack(side="left", fill="x", expand=True, pady=4)


search_entry.bind("<FocusIn>", _clear_placeholder)
search_entry.bind("<FocusOut>", _add_placeholder)
search_entry.bind("<Return>", fetch_weather) #entry'in entere tıklanınca bir fonk'a gitmesini sağladık.

city_list_frame = tk.Frame(left_frame, bg=CARD)
city_list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

favorite_cities = ["London", "New York", "Istanbul", "Ankara"]

def update_favorites_ui():
    # Önce sol paneldeki (city_list_frame) mevcut tüm kartları temizle
    for widget in city_list_frame.winfo_children():
        widget.destroy()
        
    # Başlığı yeniden ekle
    tk.Label(city_list_frame, text="FAVORITE CITIES", font=("Segoe UI", 10, "bold"), 
             bg=CARD, fg=TEXT_DARK).pack(pady=(2, 0))

    # Güncel listedeki şehirleri tekrar oluştur
    for city in favorite_cities:
        temp, icon = get_favorite_weather(city)
        create_city_card(city_list_frame, city, icon, temp)


def add_to_favorites():
    # Sağ panelde büyük harflerle yazan şehir adını al ve İlk Harfi Büyük formata çevir
    current_city = lbl_city_name.cget("text").title()
    
    # Şehir zaten listede yoksa ekle
    if current_city.lower() not in [c.lower() for c in favorite_cities]:
        favorite_cities.append(current_city)
        update_favorites_ui() # Arayüzü güncelle
        messagebox.showinfo("Başarılı", f"{current_city} favorilere eklendi!")
    else:
        messagebox.showinfo("Bilgi", f"{current_city} zaten favorilerinizde bulunuyor.")

update_favorites_ui()

header_frame = tk.Frame(right_frame, bg=CARD)
header_frame.pack(fill="x", padx=40, pady=(40, 10))

lbl_city_name = tk.Label(header_frame, text="ISTANBUL", font=("Segoe UI", 26, "bold"), bg=CARD, fg="white")
lbl_city_name.pack(anchor="w",pady=0)

lbl_country_name = tk.Label(header_frame, text="TR", font=("Segoe UI", 12), bg=CARD, fg=TEXT_DARK)
lbl_country_name.pack(anchor="w",pady=0)

# 2. ORTA BÖLÜM (Sol ve Sağ Kolonlar İçin Taşıyıcı)
details_frame = tk.Frame(right_frame, bg=CARD)
details_frame.pack(fill="x", padx=40, pady=10)

# 2A. Sol Kolon (Büyük İkon, Derece ve Buton)
left_details = tk.Frame(details_frame, bg=CARD)
left_details.pack(side="left", fill="y", pady=0)

lbl_big_icon = tk.Label(left_details, text="⛅", font=("Segoe UI Emoji", 35), bg=CARD, fg="white")
lbl_big_icon.pack(pady=(0, 1), padx=(0, 10))

lbl_big_temp = tk.Label(left_details, text="28°C", font=("Segoe UI", 48, "bold"), bg=CARD, fg="white")
lbl_big_temp.pack(anchor="w")

lbl_desc = tk.Label(left_details, text="Mostly Sunny", font=("Segoe UI", 11), bg=CARD, fg=TEXT_DARK)
lbl_desc.pack(anchor="w", pady=(0, 15))

btn_add_fav = tk.Button(left_details, text="+ Add to Favorites", font=("Segoe UI", 10, "bold"), 
                        bg=FAV_BG, fg="white", bd=0, activebackground=BORDER, command=add_to_favorites, padx=10, pady=8)
btn_add_fav.pack(anchor="w")

# 2B. Sağ Kolon (Nem, Rüzgar vb. Detaylar)
right_details = tk.Frame(details_frame, bg=CARD)
right_details.pack(side="right", fill="y", pady=(20, 0))

lbl_humidity = tk.Label(right_details, text="Humidity: 65%", font=("Segoe UI", 11), bg=CARD, fg=TEXT_DARK)
lbl_humidity.pack(anchor="w", pady=3)

lbl_wind = tk.Label(right_details, text="Wind: 15 km/h", font=("Segoe UI", 11), bg=CARD, fg=TEXT_DARK)
lbl_wind.pack(anchor="w", pady=3)


lbl_feels_like = tk.Label(right_details, text="Feels Like: 30°C", font=("Segoe UI", 11), bg=CARD, fg=TEXT_DARK)
lbl_feels_like.pack(anchor="w", pady=3)

forecast_frame = tk.Frame(right_frame, bg=ENTRY_BG, bd=0)
forecast_frame.pack(fill="x", padx=30, pady=(30, 16))

# 5 günlük sahte veri listesi (Görseldeki gibi dizmek için)
days_data = [("MON", "⛅", "29°C"), ("TUE", "☀️", "27°C"), ("WED", "☁️", "27°C"), 
             ("THU", "🌧️", "25°C"), ("FRI", "☀️", "30°C")]

for day, icon, t in days_data:
    day_box = tk.Frame(forecast_frame, bg=ENTRY_BG)
    day_box.pack(side="left", expand=True, fill="both", pady=15)
    
    tk.Label(day_box, text=day, font=("Segoe UI", 9, "bold"), bg=ENTRY_BG, fg=TEXT_DARK).pack()
    tk.Label(day_box, text=icon, font=("Segoe UI Emoji", 18), bg=ENTRY_BG).pack(pady=4)
    tk.Label(day_box, text=t, font=("Segoe UI", 10), bg=ENTRY_BG, fg=TEXT_DARK).pack()


# Start the GUI main loop
root.mainloop()