from flask import Flask, request, make_response
import os, json
import pyowm
import os
from flask_cors import CORS,cross_origin

app = Flask(__name__)
# owmapikey=os.environ.get('119242c426975bc98ee4f259b9551823') #or provide your key here
owmapikey = '9b79f04154b779055060e091b869dab4'
owm = pyowm.OWM(owmapikey)


# getting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
@cross_origin()
def webhook():
    req = request.get_json(silent=True, force=True)

    #print("Request:")
    #print(json.dumps(req))

    res = processRequest(req)

    res = json.dumps(res)
    #print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


# processing the request from dialogflow
def processRequest(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    city = parameters.get("city_name")
    observation = owm.weather_at_place(city)
    w = observation.get_weather()
    latlon_res = observation.get_location()
    #print(latlon_res)
    lat = str(latlon_res.get_lat())
    lon = str(latlon_res.get_lon())
    #check https://pyowm.readthedocs.io/en/latest/ for more pyowm commands
    wind_res = w.get_wind()
    #print(wind_res)
    wind_speed = str(wind_res.get('speed'))

    humidity = str(w.get_humidity())

    celsius_result = w.get_temperature('celsius')
    #this is a dict {'temp': 26.45, 'temp_max': 29.44, 'temp_min': 24.0, 'temp_kf': None}
    current_temp_celsius = celsius_result.get('temp')
    current_temperature = str(celsius_result.get('temp'))
    temp_min_celsius = str(celsius_result.get('temp_min'))
    temp_max_celsius = str(celsius_result.get('temp_max'))

    fahrenheit_result = w.get_temperature('fahrenheit')
    temp_min_fahrenheit = str(fahrenheit_result.get('temp_min'))
    temp_max_fahrenheit = str(fahrenheit_result.get('temp_max'))
    #speech = "Today the weather of " + city + ": \n" + "Humidity :" + humidity + ".\nWind Speed :" + wind_speed

    #print(celsius_result)
    if current_temp_celsius < 10:
        weather_type = "Very Cold"
    elif current_temp_celsius >= 10 and current_temp_celsius <=20:
        weather_type = "Cold"
    elif current_temp_celsius > 20 and current_temp_celsius <=30:
        weather_type = "Pleasant"
    elif current_temp_celsius >30 and current_temp_celsius <=40:
        weather_type = "Hot"
    else:
        weather_type = "Very Hot"

    temp_details = "Current temperature: " + current_temperature + " °C"+"\n (min,max):(" + temp_min_celsius + "," + temp_max_celsius +")"
    speech = "Today the weather of " + city + " is " + weather_type + ". \n" + temp_details + "\n\nHumidity :" + humidity + " g.kg-1"+".\n\nWind Speed: " + wind_speed + " km/hr"

    return {
        "fulfillmentText": speech,
        "displayText": speech
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 6000))
    #print("Starting app on port %d" % port)
    app.run(debug=True, port=port)
