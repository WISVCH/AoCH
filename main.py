from datetime import datetime

import requests


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


def return_today_data(members):
    # today = [{
    #     name: "string",
    #     score: int,
    #     star1: {
    #         gotten: bool,
    #         timestamp: "DD:hh:mm"
    #     }
    #     start2: {
    #         gotten: bool,
    #         timestamp: "DD:HH:mm"
    #     }
    # }]
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

            stars = {}
            person = {
                "name": value["name"],
                "score": value["local_score"],
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

            today_data.append(person)
    return today_data


if __name__ == "__main__":
    data = get_data()
    active_members = filter_non_active_members(data)

    for person in return_today_data(active_members):
        print(person)
