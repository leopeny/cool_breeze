from flask import Flask, render_template, jsonify

import requests
import json
import os
from datetime import datetime
import time
from pprint import pprint
app = Flask(__name__)

__author__ = "Kathryn Bertrand <kaytebertrand@gmail.com>"

if __name__ == "__main__":
    app.run()

# #TODO
# get hourly data
#   problems here involve the fact that a normal REST call doesn't necessarily include the data for the current hour
#   or it does and we just don't know because it's UTC instead of timezone sensitive. Who knows
#   further, the timezone may not be the most accurate
# try to only get json for one place at a time.
# get json data into d3jsplus generating script 
# how do we handle the whole checking late at night thing? auto-flip to tomorrow? maybe display both if we're interested?


API_KEY = "5785946ee5df072203082b14c701dff9"  # lolsecure

# Houston, TX
LONG = "29.7605"
LAT = "-95.3698"

PLACES = {}
PLACES['HOU'] = {"Lat": "29.7605", "Long": "-95.3698"}
PLACES['OAK'] = {"Lat": "37.8051", "Long": "-122.2731"}

GET_JSON = True

FILE_DIRECTORY = os.path.join('./static/data/Houston070716.json')

# index for today
TODAY = 0


def get_info_time_day(time, data=['temp', 'humidity'], json_data="", date=""):

    # working off of today's data
    if json_data:
        # hourly_data = json_data['hourly']['data']
        pass
    # get data from forecast's timemachine for specific date
    elif date:
        # construct a call
        pass
    # ya done messed up, son
    else:
        # raise NeedData("You have to provide data or a date")
        pass


def find_weekly_apparent_min(json_data):
    pass

def find_reasonable_apparent_min_for_today(json_data):
    hourly_data = json_data['hourly']['data']

    # timestamps are all UTC, so we can figure out offset from the json data 
    # normal working hours M-F 8-5 normal sleeping hours 12-6
    seconds_in_a_min = 60
    min_in_an_hour = 60
    print(json_data['offset'])
    hour_offset = json_data['offset'] * seconds_in_a_min * min_in_an_hour
    print(hour_offset)
    print(json_data['latitude'])
    print(json_data['longitude'])

    apparent_min = hourly_data[0]['apparentTemperature']
    for data in hourly_data:
        # pprint(data)
        cur_apparent_min = data['apparentTemperature']
        time = data['time'] + hour_offset
        print(datetime.utcfromtimestamp(time).strftime('%m/%d/%y %H:%M'))
        hour = datetime.utcfromtimestamp(time).strftime('%H')
        print(hour)
        if cur_apparent_min < apparent_min:
            apparent_min = cur_apparent_min


@app.route("/")
def index():

    # we only get the JSON once for a day to save on API calls (which aren't free after 1000)
    if GET_JSON:
        response = requests.get("https://api.forecast.io/forecast/" + API_KEY \
            + "/" + PLACES['HOU']['Lat'] + "," + PLACES['HOU']['Long'])
        json_data = response.json()
    else:
        file_string = open(FILE_DIRECTORY).read()
        json_data = json.loads(file_string)
        now = datetime.now()
        timestamp = int(time.time())
        # midnight = datetime(now.year, now.month, now.day, 12, 0, json_data['timezone'])
        # time = datetime.utcfromtimestamp(datetime.now()).strftime('%m/%d/%y %H:%M')
        print(now)
        print(timestamp)
        # print(midnight)
        # print(midnight.timestamp())

    pretty_json = json.dumps(json_data, sort_keys=True, indent=4)

    daily_apparent_min_unix_time = json_data["daily"]["data"][TODAY]["apparentTemperatureMinTime"]

    daily_apparent_min = {}
    daily_apparent_min['time'] = datetime.utcfromtimestamp(daily_apparent_min_unix_time).strftime("%H:%M")
    daily_apparent_min['apparent_temp'] = json_data["daily"]["data"][TODAY]["apparentTemperatureMin"]
    daily_apparent_min['temp'] = get_info_time_day(datetime.utcfromtimestamp(daily_apparent_min_unix_time).strftime('%H'), json_data)

    weekly_apparent_min = find_weekly_apparent_min(json_data)

    find_reasonable_apparent_min_for_today(json_data)

    return render_template("index.html",
                           json=pretty_json,
                           daily_apparent_min=daily_apparent_min,
                           weekly_apparent_min=weekly_apparent_min)


@app.route("/_daily_json")
def daily_json():
    # latitude = request.args.get('lat', 0, type=string)
    # longitude = request.args.get('long', 0, type=string)
    # time = request.args.get('time', 0, type=int)

    file_string = open(FILE_DIRECTORY).read()
    json_data = json.loads(file_string)

    return jsonify(json_data['hourly']['data'])


@app.route("/_weekly_json")
def weekly_json():
    file_string = open(FILE_DIRECTORY).read()
    json_data = json.loads(file_string)

    return jsonify(json_data['daily']['data'])
