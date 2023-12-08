from datetime import datetime
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_data():
    url = "https://adventofcode.com/2023/leaderboard/private/view/954860.json"
    cookie = "session=53616c7465645f5f1c43c14b203359c399a1c7373e63dd4884a54869a787103f3b76a8df0dbcfcab49920c81cd573200b657ea0016db75fb023f35c8ed37264e"
    headers = {"cookie": cookie}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    return data


def filter_non_active_members(data):
    active_members = {}
    for key, value in data["members"].items():
        if value["local_score"] > 0:
            active_members[key] = value
    return active_members


def return_today_data(members, total_members):
    today_data = []


    # Get current day
    current_time = datetime.now()
    today = str(
        int(current_time.strftime("%d"))
    )  # We weten dat dit gebeund is, maar Robert blijft zeuren of het al af is

    for key, value in members.items():
        if today in value["completion_day_level"]:
            # Today +5 hours
            time_started = datetime.now().strptime(
                "2023-12-" + today + " 05:00:00", "%Y-%m-%d %H:%M:%S"
            )

            person = {
                "name": value["name"],
                "score": 0,
            }

            for star in ["1", "2"]:
                if star in value["completion_day_level"][today]:
                    star_time = (
                        datetime.fromtimestamp(
                            value["completion_day_level"][today][star]["get_star_ts"]
                        )
                        - time_started
                    )
                    person[
                        "star" + star
                    ] = f"{star_time.days} days {star_time.seconds//3600} hours {star_time.seconds//60%60} minutes"

                    person["star_index" + star] = value["completion_day_level"][today][star]["star_index"]

            today_data.append(person)
    today_data.sort(key=lambda x: x["star_index1"])
    for index, person in enumerate(today_data):
        person["score"] = total_members - index

    day2_data = [person for person in today_data if "star2" in person]
    day2_data.sort(key=lambda x: x["star_index2"])
    for index, person in enumerate(day2_data):
        person["score"] += total_members - index

    for person in today_data:
        person.pop("star_index1")
        if "star_index2" in person:
            person.pop("star_index2")
    today_data.sort(key=lambda x: x["score"], reverse=True)
        
    return today_data

def return_global_data(members):
    global_data = []
    for key, value in members.items():
        person = {
            "name": value["name"],
            "score": value["local_score"],
            "stars": []
        }
        for int in range(1, 26):
            if str(int) in value["completion_day_level"]:
                if "2" in value["completion_day_level"][str(int)]:
                    person["stars"].append(2)
                else:
                    person["stars"].append(1)
            else:
                person["stars"].append(0)
        

        global_data.append(person)
    global_data.sort(key=lambda x: x["score"], reverse=True)
    return global_data
    
@app.route('/')
def return_data():
    data = get_data()
    active_members = filter_non_active_members(data)
    today_data = return_today_data(active_members, len(data['members']))
    total_data = return_global_data(active_members)

    data = {
        "total": total_data,
        "today": today_data
    }
    
    return data
