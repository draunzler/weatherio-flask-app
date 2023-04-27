from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        api_key = 'a75eed3712abd05ea47237419c17a123'
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
        
        temperature = round(data['main']['temp'] - 273.15, 2) # Temperature in Celsius
        pressure = data['main']['pressure'] # Atmospheric pressure
        humidity = data['main']['humidity'] # Humidity
        visibility = data.get('visibility', 'N/A') # Visibility in meters
        wind_speed = data['wind']['speed'] # Wind speed in m/s
        wind_direction = data['wind'].get('deg', 'N/A') # Wind direction in degrees
        description = data['weather'][0]['description'] # Weather description
        icon = data['weather'][0]['icon'] # Weather icon code
        
        return render_template('index.html', 
                               city=city,
                               temperature=temperature, 
                               pressure=pressure, 
                               humidity=humidity, 
                               visibility=visibility, 
                               wind_speed=wind_speed, 
                               wind_direction=wind_direction, 
                               description=description, 
                               icon=icon)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)