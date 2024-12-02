import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
from flask import Blueprint, Flask, render_template, render_template_string
from flask_cors import CORS

import logging


logger = logging.getLogger('aoch')
logger.setLevel(logging.INFO)
bp = Blueprint('aoch', __name__)

data = {}
# the two below variables are used to keep track of when was last pulled, so we do not overload the Advent of Code servers
# as per the specifications provided in [the wiki](https://www.reddit.com/r/adventofcode/wiki/faqs/automation)
last_pull = datetime.now() - timedelta(hours=6)
assignment = {"puzzle": "", "last_pulled": last_pull}
current_working_directory = os.getcwd()

# required per [community wiki](https://www.reddit.com/r/adventofcode/wiki/faqs/automation)
user_agent = (
    "https://github.com/WISVCH/AoCH, beheer@ch.tudelft.nl"
)
session = os.environ.get("session")
cookie = f"session={session}"
headers = {"cookie": cookie, "User-Agent": user_agent}
leaderboard_id = os.environ.get("leaderboard_id")

authors = {
    "larsvantol": "Lars van Tol 🎅",
    "KasperVaessen": "Kasper Vaessen 🎄",
    "Thom Breugelmans": "Thom Breugelmans 🎁",
}


def create_app():
    cur_folder = os.path.dirname(os.path.realpath(__file__))
    app = Flask(__name__, 
                static_url_path='', 
                static_folder=os.path.join(cur_folder, '../static'), 
                template_folder=os.path.join(cur_folder, '../templates'))
    CORS(app)

    app.register_blueprint(bp)
    app.add_url_rule('/', endpoint='index')

    return app


def current_time() -> tuple[int, int, int]:
    """
    Returns the current day, month, and year in a tuple of strings.
    If the current day is past Christmas, it will return 25 as the day.
    """
    # Get current day
    current_time = datetime.now(tz=ZoneInfo('Europe/Amsterdam')) - timedelta(hours=6)
    this_day = current_time.day
    if this_day > 25:
        this_day = 25
    this_month = current_time.month
    this_year = current_time.year
    if this_month != 12:
        this_day = 25
        this_year = this_year - 1

    return this_day, this_month, this_year


def get_data(today: tuple[int, int, int]):
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

    logger.info("Pulling new data from Advent of Code!")

    url = f"https://adventofcode.com/{this_year}/leaderboard/private/view/{leaderboard_id}.json"
    response = requests.get(url, headers=headers, timeout=5)
    logger.info(f'Getting data for {this_year}, response: {response.status_code}')
    data = response.json()
    last_pull = now
    return data


def get_day_assignment(today: tuple[int, int, int]):
    """
    Pulls the data from Advent of Code and returns.
    This method will make a request to the advent of code website
    only once every first 25 days of December.
    """
    global assignment

    this_day, this_month, this_year = today

    # only request the puzzle input if we do not have a puzzle already and the day has changed
    if (
        assignment["puzzle"] != ""
        and this_day == assignment["last_pulled"].day
        and this_month == assignment["last_pulled"].month
        and this_year == assignment["last_pulled"].year
    ):
        return assignment["puzzle"]

    url = f"https://adventofcode.com/{this_year}/day/{this_day}"
    response = requests.get(url, headers=headers, timeout=5)
    logger.info(f'Getting challenge for {this_day}-{this_month}-{this_year}, response: {response.status_code}')
    assignment["puzzle"] = response.text
    assignment["last_pulled"] = datetime(year=this_year, month=this_month, day=this_day)
    return response.text


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
        if str(this_day) in value["completion_day_level"]:
            # Today +6 hours
            time_started = datetime(year=this_year, month=12, day=this_day, hour=6, tzinfo=ZoneInfo('Europe/Amsterdam'))

            person = {
                "name": value["name"],
                "score": 0,
            }

            for star in ["1", "2"]:
                if star in value["completion_day_level"][str(this_day)]:
                    if star == "1":
                        star_time = (
                            datetime.fromtimestamp(
                                value["completion_day_level"][str(this_day)][star]["get_star_ts"]
                            , tz=ZoneInfo('Europe/Amsterdam'))
                            - time_started
                        )
                    else:
                        star_time = datetime.fromtimestamp(
                            value["completion_day_level"][str(this_day)][star]["get_star_ts"]
                        ) - datetime.fromtimestamp(
                            value["completion_day_level"][str(this_day)]["1"]["get_star_ts"]
                        )
                    star_time_string = ""
                    if star == "2":
                        star_time_string += "+ "
                    if star_time.days > 0:
                        star_time_string += f"{star_time.days} days "
                    if star_time.seconds // 3600 > 0:
                        star_time_string += f"{star_time.seconds//3600} hours "
                    if star_time.seconds // 60 % 60 > 0:
                        star_time_string += f"{star_time.seconds//60%60} minutes"
                    person["star" + star] = star_time_string

                    person["star_index" + star] = value["completion_day_level"][str(this_day)][
                        star
                    ]["star_index"]

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
        assignment_html = assignment_html.replace('<article class="day-desc">', "")
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
        for i in range(1, 26):
            if str(i) in value["completion_day_level"]:
                if "2" in value["completion_day_level"][str(i)]:
                    person["stars"].append(2)
                else:
                    person["stars"].append(1)
            else:
                person["stars"].append(0)

        global_data.append(person)
    global_data.sort(key=lambda x: x["score"], reverse=True)
    return global_data


@bp.route("/data")
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


@bp.route("/challenge")
def return_challenge():
    return render_template("challenge.html")

@bp.route("/leaderboard")
def return_leaderboard():
    return render_template("leaderboard.html")

@bp.route("/leaderboard/today")
def return_leaderboard_today():
    return render_template("leaderboard_today.html")


@bp.route("/")
def return_index():
    """
    Endpoint for the frontend.
    """
    return render_template("index.html")


if __name__ == "__main__":
    app = create_app()
    app.run()
