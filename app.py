import os
import re
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

data = {}
assignment = ""
last_pull = datetime.now() - timedelta(hours=1)
current_working_directory = os.getcwd()

session = "53616c7465645f5f1c43c14b203359c399a1c7373e63dd4884a54869a787103f3b76a8df0dbcfcab49920c81cd573200b657ea0016db75fb023f35c8ed37264e"
cookie = f"session={session}"
leaderboard_id = "954860"

authors = {
    "larsvantol": "Lars van Tol 🎅",
    "KasperVaessen": "Kasper Vaessen 🎄",
    "Thom Breugelmans": "Thom Breugelmans 🎁",
}


def current_time() -> tuple[str, str, str]:
    """
    Returns the current day, month, and year in a tuple of strings.
    If the current day is past Christmas, it will return 25 as the day.
    """
    # Get current day
    current_time = datetime.now() - timedelta(hours=6)
    this_day = "{dt.day}".format(dt=current_time)
    if int(this_day) > 25:
        this_day = "25"
    this_month = "{dt.month}".format(dt=current_time)
    this_year = "{dt.year}".format(dt=current_time)
    if this_month != "12":
        this_day = "25"
        this_year = str(int(this_year) - 1)

    return this_day, this_month, this_year


def get_data(today: tuple[str, str, str]):
    """
    Pulls the data from Advent of Code and returns.
    If the data has been pulled in the last 15 minutes, it will return the
    previously pulled data.
    """
    global data
    global last_pull

    _, _, this_year = today

    # Advent of Code requests to only be called once every 15 minutes
    now = datetime.now()
    if (now - last_pull) < timedelta(minutes=15):
        return data

    app.logger.info("Pulling new data from Advent of Code!")

    url = "https://adventofcode.com/" + this_year + f"/leaderboard/private/view/{leaderboard_id}.json"
    headers = {"cookie": cookie}
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    last_pull = now
    return data

def get_day_assignment(today: tuple[str, str, str]):
    """
    Pulls the data from Advent of Code and returns.
    If the data has been pulled in the last 15 minutes, it will return the
    previously pulled data.
    """
    global assignment

    this_day, this_month, this_year = today

    if assignment != "":
        return assignment
    url = "https://adventofcode.com/" + this_year + "/day/" + this_day
    # headers = {"cookie": cookie}
    response = requests.get(url, timeout=5)
    assignment = response.text
    return assignment

def filter_non_active_members(members):
    """
    Filters out members who have not earned any points. They are considered inactive.
    """
    active_members = {}

    for key, value in members.items():
        if value["name"] in authors:
            value["name"] = authors[value["name"]]
        if value["local_score"] > 0:
            active_members[key] = value

    return active_members


def return_day_data(members, total_members, today):
    """
    Returns the data for the current day.
    """
    this_day, this_month, this_year = today
    today_data = []

    for key, value in members.items():
        if this_day in value["completion_day_level"]:
            # Today +5 hours
            time_started = datetime.now().strptime(
                this_year + "-12-" + this_day + " 06:00:00", "%Y-%m-%d %H:%M:%S"
            )

            person = {
                "name": value["name"],
                "score": 0,
            }

            for star in ["1", "2"]:
                if star in value["completion_day_level"][this_day]:
                    star_time = (
                        datetime.fromtimestamp(
                            value["completion_day_level"][this_day][star]["get_star_ts"]
                        )
                        - time_started
                    )
                    star_time_string = ""
                    if star_time.days > 0:
                        star_time_string += f"{star_time.days} days "
                    if star_time.seconds // 3600 > 0:
                        star_time_string += f"{star_time.seconds//3600} hours "
                    if star_time.seconds // 60 % 60 > 0:
                        star_time_string += f"{star_time.seconds//60%60} minutes"
                    person[
                        "star" + star
                    ] = star_time_string

                    person["star_index" + star] = value["completion_day_level"][this_day][star][
                        "star_index"
                    ]

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


def return_day_assignment(html):
    assignment_html = re.search(r"<article class=\"day-desc\">(.|\n)*?<\/article>", html)
    if assignment_html:
        assignment_html = assignment_html.group()
        assignment_html = assignment_html.replace("<article class=\"day-desc\">", "")
        assignment_html = assignment_html.replace("</article>", "")
        return assignment_html
    return html



def return_global_data(members):
    """
    Returns the global data for the leaderboard.
    """
    global_data = []
    for key, value in members.items():
        person = {"name": value["name"], "score": value["local_score"], "stars": []}
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


@app.route("/data")
def return_data():
    """
    Endpoint for the frontend.
    """
    today = current_time()
    data = get_data(today)
    assignment_html = get_day_assignment(today)
    active_members = filter_non_active_members(data["members"])
    today_data = return_day_data(active_members, len(data["members"]), today)
    total_data = return_global_data(active_members)
    assignment_data = return_day_assignment(assignment_html)


    data = {"total": total_data, "today": today_data, "assignment": assignment_data}

    return data

@app.route("/")
def return_index():
    """
    Endpoint for the frontend.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
