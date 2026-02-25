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

        temperature = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        information_label.config(text=f"Temperature: {temperature}°C\nWeather: {weather.capitalize()}")

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

    # Şehir Adı (En sola yapıştırıyoruz)
    tk.Label(card, text=city_name, font=("Segoe UI", 16, "bold"), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="left", padx=20)

    # Sıcaklık Değeri (En sağa yapıştırıyoruz - sağdan sola doğru eklenecek)
    tk.Label(card, text=f"{temp}°C", font=("Segoe UI", 16), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="right", padx=20)

    # Hava Durumu İkonu (Sıcaklık değerinin hemen soluna yerleşir)
    tk.Label(card, text=icon, font=("Segoe UI Emoji", 16), 
             bg=FAV_BG, fg=ENTRY_BG).pack(side="right", padx=5)     


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

tk.Label(city_list_frame, text="FAVORITE CITIES", font=("Segoe UI", 10, "bold"), 
         bg=CARD, fg=TEXT_DARK).pack(pady=(2, 0))

favorite_cities = ["London", "New York", "Istanbul", "Ankara"]

for city in favorite_cities:
    # 1. API'den şehrin güncel verisini çek
    temp, icon = get_favorite_weather(city)
    
    # 2. Kartı güncel verilerle oluştur
    create_city_card(city_list_frame, city, icon, temp)



weather_label = tk.Label(right_frame, text="WEATHER", font=("Segoe UI", 20, "bold"), bg=CARD, fg=TEXT_DARK)
weather_label.pack(pady= (20, 4))    


# Create a label to display weather information
information_label = tk.Label(right_frame, text="")
information_label.pack()





# Start the GUI main loop
root.mainloop()