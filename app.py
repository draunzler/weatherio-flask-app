from flask import Flask, render_template, request
import requests
import json
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from geoip2.database import Reader

load_dotenv()

app = Flask(__name__)

reader = Reader('GeoLite2-City.mmdb')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
    else:
        user_ip = request.remote_addr
        try:
            response = reader.city(user_ip)
            city = response.city.name if response.city else None
        except Exception as e:
            print("Error fetching user location:", e)
            city = None
    
    if city is None:
        # Handle the case where city is None
        return render_template('error.html', message='City not found')
    
    api_key = os.getenv('OPENWEATHER_API')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response = requests.get(url)
    data = json.loads(response.text)
    
    # Check if the API request was successful
    if response.status_code != 200:
        error_message = data['message'] if 'message' in data else 'An error occurred'
        return render_template('error.html', message=error_message)
    
    # Extract weather information if available
    if 'main' not in data:
        return render_template('error.html', message='No weather information found')
    
    temperature = round(data['main']['temp'] - 273.15) # Temperature in Celsius
    pressure = data['main']['pressure'] # Atmospheric pressure
    humidity = data['main']['humidity'] # Humidity
    visibility = data.get('visibility', 'N/A') # Visibility in meters
    wind_speed = data['wind']['speed'] # Wind speed in m/s
    wind_direction = data['wind'].get('deg', 'N/A') # Wind direction in degrees
    description = data['weather'][0]['description'] # Weather description
    icon = data['weather'][0]['icon'] # Weather icon code
    
    # Get current date and time of the city
    timezone = data['timezone']
    city_time = datetime.now(pytz.utc).astimezone(pytz.timezone(pytz.country_timezones[data['sys']['country']][0]))
    city_date = city_time.strftime('%A, %d %b \'%y')
    city_time = city_time.strftime('%H:%M')
    
    return render_template('index.html', 
                           city=city.title(),
                           temperature=temperature, 
                           pressure=pressure, 
                           humidity=humidity, 
                           visibility=visibility, 
                           wind_speed=wind_speed, 
                           wind_direction=wind_direction, 
                           description=description, 
                           icon=icon,
                           city_time=city_time,
                           city_date=city_date)

if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)
