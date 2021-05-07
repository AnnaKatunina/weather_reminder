import requests
from decouple import config

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def get_weather(city_name):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={config("weather_api_key")}'
    data = requests.get(url).json()
    weather_data = {
        'city': data['name'],
        'temperature': f"{data['main']['temp']}°C",
        'feels like': f"{data['main']['feels_like']}°C",
        'description': data['weather'][0]['description'],
        'wind speed': f'{data["wind"]["speed"]} m/s',
    }
    return weather_data


def send_email(email, cities):
    html_content = ''
    for city in cities:
        weather = get_weather(city)
        html_content += f'''<p>
                                <strong>{weather["city"]}</strong><br>
                                Temperature {weather["temperature"]}<br>
                                Feels like {weather["feels like"]}<br>
                                {weather["description"]}<br>
                                Wind speed {weather["wind speed"]}<br>
                            </p>'''
    sg = SendGridAPIClient(config('sendgrid_api_key'))
    message = Mail(
        from_email=config('from_email'),
        to_emails=email,
        subject='Weather notification',
        html_content=html_content
    )
    sg.send(message)