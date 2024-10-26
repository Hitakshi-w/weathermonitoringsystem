import sqlite3
import requests
import time
import pandas as pd
import streamlit as st
import threading
import sys

ALERT_THRESHOLD = 35  # User-configurable threshold
CONSECUTIVE_ALERTS = 2  # Number of consecutive updates to trigger an alert
INTERVAL = 300  # 300 seconds or 5 minutes

DB_NAME = 'weather_data.db'
API_KEY = 'your_api_key'
CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']

alert_counter = {city: 0 for city in CITIES}

def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
                        city TEXT, main TEXT, temp REAL, feels_like REAL, dt INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS daily_summary (
                        city TEXT, 
                        date TEXT, 
                        avg_temp REAL, 
                        max_temp REAL, 
                        min_temp REAL, 
                        dominant_weather TEXT,
                        PRIMARY KEY (city, date))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS alerts (
                        city TEXT, 
                        temp REAL, 
                        dt INTEGER)''')
    conn.commit()
    conn.close()
    print('Database created successfully')
    sys.stdout.flush()

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def fetch_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return {
        'city': city,
        'main': data['weather'][0]['main'],
        'temp': kelvin_to_celsius(data['main']['temp']),
        'feels_like': kelvin_to_celsius(data['main']['feels_like']),
        'dt': data['dt']
    }

def store_weather_data(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO weather VALUES (?, ?, ?, ?, ?)', 
                   (data['city'], data['main'], data['temp'], data['feels_like'], data['dt']))
    conn.commit()
    conn.close()

def calculate_daily_summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Calculate daily summaries
    cursor.execute('''
        SELECT city, date(dt, 'unixepoch') as date, 
               AVG(temp) as avg_temp, 
               MAX(temp) as max_temp, 
               MIN(temp) as min_temp, 
               (SELECT main 
                FROM weather w2 
                WHERE w2.city = w1.city AND w2.dt = (SELECT MAX(w3.dt) FROM weather w3 WHERE w3.city = w1.city AND date(w3.dt, 'unixepoch') = date(w1.dt, 'unixepoch'))) as dominant_weather
        FROM weather w1
        GROUP BY city, date
    ''')
    summaries = cursor.fetchall()
    
    # Insert or update daily summaries
    for summary in summaries:
        cursor.execute('''
            INSERT INTO daily_summary (city, date, avg_temp, max_temp, min_temp, dominant_weather)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(city, date) DO UPDATE SET
                avg_temp=excluded.avg_temp,
                max_temp=excluded.max_temp,
                min_temp=excluded.min_temp,
                dominant_weather=excluded.dominant_weather
        ''', summary)
    
    conn.commit()
    conn.close()

def check_alerts(data):
    global alert_counter
    if data['temp'] > ALERT_THRESHOLD:
        alert_counter[data['city']] += 1
        if alert_counter[data['city']] >= CONSECUTIVE_ALERTS:
            print_alert(data)
            store_alert(data)
            alert_counter[data['city']] = 0  # Reset counter after alert
    else:
        alert_counter[data['city']] = 0  # Reset counter if condition is not met

def print_alert(data):
    print(f"Alert! Temperature in {data['city']} is {data['temp']}°C")

def store_alert(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO alerts VALUES (?, ?, ?)', 
                   (data['city'], data['temp'], data['dt']))
    conn.commit()
    conn.close()

def visualize_data():
    conn = sqlite3.connect(DB_NAME)
    
    # Fetch weather data
    weather_df = pd.read_sql_query('SELECT * FROM weather', conn)
    
    # Fetch daily summary data
    daily_summary_df = pd.read_sql_query('SELECT * FROM daily_summary', conn)
    
    # Fetch alerts data
    alert_df = pd.read_sql_query('SELECT * FROM alerts', conn)
    
    conn.close()
    
    # Convert date columns to datetime
    weather_df['dt'] = pd.to_datetime(weather_df['dt'], unit='s')
    daily_summary_df['date'] = pd.to_datetime(daily_summary_df['date'])
    alert_df['dt'] = pd.to_datetime(alert_df['dt'], unit='s')
    
    st.title('Weather Data and Summary')
    
    # Display raw weather data
    st.subheader('Raw Weather Data')
    st.dataframe(weather_df)
    
    # Display daily summary data
    st.subheader('Daily Summary Data')
    st.dataframe(daily_summary_df)
    
    # Visualize daily summary data
    for city in CITIES:
        city_data = daily_summary_df[daily_summary_df['city'] == city]
        st.subheader(f'Weather Summary for {city}')
        st.line_chart(city_data.set_index('date')[['avg_temp', 'max_temp', 'min_temp']])
    
    # Display alerts
    st.subheader('Alerts')
    st.dataframe(alert_df)

def fetch_and_store_data():
    while True:
        for city in CITIES:
            data = fetch_weather_data(city)
            print(data)
            store_weather_data(data)
            check_alerts(data)
        calculate_daily_summary()
        time.sleep(INTERVAL)

def main():
    print("Starting main function")
    create_database()
    print("Database creation function called")
    
    # Start the data fetching and storing in a separate thread
    data_thread = threading.Thread(target=fetch_and_store_data)
    data_thread.daemon = True
    data_thread.start()
    
    # Run the Streamlit app
    while True:
        visualize_data()
        time.sleep(INTERVAL)
        st.experimental_rerun()

if __name__ == '__main__':
    main()
