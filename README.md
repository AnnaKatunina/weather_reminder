# Weather Reminder project

A web application using Django REST framework is a service of weather notifications.

The Weather Reminder app provides API for getting information about the weather. 

This app has the following features:

- after registration clients receive API key for further access to the application
- after login clients receive JWT token
- users can subscribe to weather notifications, choose cities and period of notification(1, 3, 6 or 12 hours) via rest api
- users can add/update/delete cities in their subscription, update period of notification and cancel the subscription via rest api
- for getting actual weather data the Weather Reminder app uses OpenWeather api service https://openweathermap.org/api
- users get notifications every period specified in the subscription via email (redis, celery beat, asynchronous periodic task and SendGrid were used to implement this functionality)
- users can request the current weather in cities from their subscription anytime and get response in json format via rest api


The app has been wrapped to a docker container.

The application has been covered with unit tests.

____
## Requirements

- Python 3.7+
- Django 3.1
- Docker

## Installing

1\. Clone the repository
```
git clone https://github.com/AnnaKatunina/weather_reminder.git
```
2\. Install docker


## Usage

Run the application by using docker containers
```
docker-compose up
```