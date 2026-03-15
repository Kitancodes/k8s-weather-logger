import os
import requests
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Config
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITIES = os.getenv("CITIES", "Lagos,Abuja,Tokyo,London").split(",")

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# Create table if it doesn't exist
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_log (
            id SERIAL PRIMARY KEY,
            city VARCHAR(100),
            temperature FLOAT,
            humidity INT,
            wind_speed FLOAT,
            fetched_at TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()

# Fetch weather data from OpenWeatherMap
def fetch_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "fetched_at": datetime.utcnow()
    }

# Save weather data to database
def save_weather(conn, data):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO weather_log 
        (city, temperature, humidity, wind_speed, fetched_at)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data["city"],
        data["temperature"],
        data["humidity"],
        data["wind_speed"],
        data["fetched_at"]
    ))
    conn.commit()
    cursor.close()

# Main function
def main():
    conn = get_db_connection()
    create_table(conn)

    for city in CITIES:
        try:
            print(f"Fetching weather for {city}...")
            data = fetch_weather(city)
            save_weather(conn, data)
            print(f"Saved: {city} | {data['temperature']}°C | {data['humidity']}% | {data['wind_speed']} m/s")
        except Exception as e:
            print(f"Error fetching {city}: {e}")

    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
