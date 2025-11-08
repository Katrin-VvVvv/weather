import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime

city = input("Ведите свой город, на английском и маленькими буквами: ")
URL = f"https://www.gismeteo.ru/weather-{city}/10-days/"

def fetch_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text

def parse_weather(html):
    soup = BeautifulSoup(html, 'html.parser')
    forecasts = []
    
    days = soup.select('div.widget-row.widget-row-days > span.unit')
    temps = soup.select('div.widget-row.widget-row-temperature > div.unit > span.value')
    precips = soup.select('div.widget-row.widget-row-precipitation > div.unit > span.unit_value')


    for i in range(min(7, len(days))):
        date_str = days[i].get('data-day')
        temp_str = temps[i].get_text(strip=True)
        precip_str = precips[i].get_text(strip=True) if i < len(precips) else "0 мм"
        
        forecasts.append({
            "Город": city,
            "Дата": date_str,
            "Температура": temp_str,
            "Осадки": precip_str
        })
    
    return forecasts

def analyze_data(data):
    df = pd.DataFrame(data)
    df['Дата'] = pd.to_datetime(df['Дата'])
    df = df.sort_values('Дата').reset_index(drop=True)
    
    df['Температура_C'] = df['Температура'].str.replace('−', '-').str.replace('°', '').astype(int)
    df['Осадки_мм'] = df['Осадки'].str.replace(' мм', '').astype(float)
    
    stats = {
        'Средняя температура (°C)': round(df['Температура_C'].mean(), 1),
        'Минимальная температура (°C)': df['Температура_C'].min(),
        'Максимальная температура (°C)': df['Температура_C'].max(),
        'Среднее количество осадков (мм)': round(df['Осадки_мм'].mean(), 1),
        'Дней с осадками': (df['Осадки_мм'] > 0).sum()
    }
    return df, stats

def save_to_console(df, stats):
    print("=== Прогноз погоды на неделю ===\n")
    for _, row in df.iterrows():
        print(f"Дата: {row['Дата'].strftime('%d.%m.%Y')}")
        print(f"Температура: {row['Температура']}")
        print(f"Осадки: {row['Осадки']}")
    
    print("\n=== Статистика за период ===\n")
    for key, value in stats.items():
        print(f"{key}: {value}")


def main():
    html = fetch_page(URL)
    data = parse_weather(html)
    df, stats = analyze_data(data)
    save_to_console(df, stats)

if __name__ == "__main__":
    main()
