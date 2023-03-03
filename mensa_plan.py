#!/usr/bin/env python3

# pip install beautifulsoup4
# pip install requests
from argparse import ArgumentParser
import datetime
from bs4 import BeautifulSoup
import requests

# from optparse import OptionParser


def find_meals_and_prices(html):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.find_all("tbody")  # table bodies
    rows = [row for body in rows for row in body.find_all("tr")]
    rows = [
        (
            entry.find("td", "meals__column-title"),
            entry.find_all("td", "meals__column-price"),
        )
        for entry in rows
    ]
    rows = [
        (entry[0].get_text(strip=True), [e.get_text(strip=True) for e in entry[1]])
        for entry in rows
        if entry[0] is not None
    ]

    return rows


def find_date(html):
    soup = BeautifulSoup(html, "html.parser")
    dateFound = soup.find("option", selected="selected")
    return dateFound.get_text(strip=True)


# def print_meals_and_prices(meals_and_prices):
#     for row in meals_and_prices:
#         print(row[1][0], row[1][1], row[1][2], row[0])


def print_plan(plan_list):
    for row in plan_list:
        print(row[0], row[1])


def target_id(target):
    translate = {"mensa": "341", "ff": "474", "galerie": "451"}
    return translate[target]


def get_request(dateIn, target):
    """date in format: 2021-08-26"""
    url = f"https://mobil.itmc.tu-dortmund.de/canteen-menu/v3/canteens/{target_id(target)}/{dateIn}"
    response = requests.request("GET", url, timeout=3)
    return response.json()


def beautify_mensa_plan(plan_dict):
    """Beautify mensa plan from the dictionary."""
    complete_list = []
    for entry in plan_dict:
        prices = entry["price"]
        complete_list.append(
            [
                f"S: {prices['student']} B: {prices['staff']} G: {prices['guest']}",
                entry["title"]["de"],
            ]
        )
    return complete_list


def beautify_mensa_plan_no_pork(plan_dict):
    """Beautify mensa plan from the dictionary, wihout pork."""
    complete_list = []
    for entry in plan_dict:
        if "S" not in entry["type"]:
            prices = entry["price"]
            complete_list.append(
                [
                    f"S: {prices['student']} B: {prices['staff']} G: {prices['guest']}",
                    entry["title"]["de"],
                ]
            )
    return complete_list


def beautify_mensa_plan_vegie(plan_dict):
    """Beautify mensa plan from the dictionary, vegetarian only."""  # V
    complete_list = []
    for entry in plan_dict:
        if (not bool(entry["type"])) or (
            ("V" in entry["type"]) or (("N" in entry["type"]))
        ):
            prices = entry["price"]
            complete_list.append(
                [
                    f"S: {prices['student']} B: {prices['staff']} G: {prices['guest']}",
                    entry["title"]["de"],
                ]
            )
    return complete_list


def beautify_mensa_plan_vegan(plan_dict):
    """Beautify mensa plan from the dictionary, vegan only."""  # N
    complete_list = []
    for entry in plan_dict:
        if (not bool(entry["type"])) or (("N" in entry["type"])):
            prices = entry["price"]
            complete_list.append(
                [
                    f"S: {prices['student']} B: {prices['staff']} G: {prices['guest']}",
                    entry["title"]["de"],
                ]
            )
    return complete_list


def plan_for_date(dateIn: datetime.date, target: str):
    date_str = dateIn.isoformat()
    date_weekday = dateIn.strftime("%a")
    try:
        # Get mensa plan as list of dictionaries
        plan_dict = get_request(date_str, target)

        # Beautify mensa plan
        plan_list = []
        check = int(args["!schwein"]) + int(args["vegi"]) + int(args["vegan"])
        if check > 1:
            print("Please select only one dietary restriction!")
            quit()
        if args["!schwein"]:
            plan_list = beautify_mensa_plan_no_pork(plan_dict)
        elif args["vegi"]:
            plan_list = beautify_mensa_plan_vegie(plan_dict)
        elif args["vegan"]:
            plan_list = beautify_mensa_plan_vegan(plan_dict)
        else:
            plan_list = beautify_mensa_plan(plan_dict)

        # Print output
        print(f"--Target plan for {date_weekday} {date_str}--")
        print_plan(plan_list)
    except:
        print("Target date for {date_weekday} {date_str} could not be printed.")


if __name__ == "__main__":
    dates_to_check = []  # dates to be checked
    # options
    parser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--date",
        dest="date",
        help="get mensa plan for ATE in the form yyyy-mm-dd",
        metavar="DATE",
    )
    parser.add_argument(
        "-p",
        "--plus",
        dest="plus",
        type=int,
        help="get mensa plan for today plus X days",
        metavar="X",
    )
    parser.add_argument(
        "-n",
        "--next",
        dest="next",
        type=int,
        help="get mensa lan for next X days including today",
        metavar="X",
    )
    parser.add_argument(
        "-w",
        "--week",
        dest="week",
        action="store_true",
        default=False,
        help="Show plan for whole week.",
    )
    parser.add_argument(
        "-!s",
        "--!schwein",
        default=False,
        help="only show meals not containing pork.",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--vegi",
        default=False,
        help="Only show vegetarian menus.",
        action="store_true",
    )
    parser.add_argument(
        "-v+",
        "--vegan",
        default=False,
        help="only show vegan menus",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--target",
        default="mensa",
        type=str,
        help="Choose your target. (mensa,ff,galerie)",
    )
    args = vars(parser.parse_args())

    if args["date"] is not None:
        main_date = datetime.date.fromisoformat(args["date"])
    else:
        main_date = datetime.date.today()

    if args["plus"] is not None:
        main_date = main_date + datetime.timedelta(days=args["plus"])

    if args["next"] is not None:
        next_var = args["next"]
        for idx in range(0, next_var + 1):
            dates_to_check.append(main_date + datetime.timedelta(days=idx))
    else:
        dates_to_check.append(main_date)

    if args["week"]:
        for dat in dates_to_check[:]:
            # find first day of the week
            weekday = dat.weekday()  # integer from 0 to 6
            mon = dat - datetime.timedelta(days=weekday)
            for idx in range(0, 5):
                dates_to_check.append(mon + datetime.timedelta(days=idx))
        dates_to_check = list(set(dates_to_check))
        dates_to_check.sort()

    for date in dates_to_check:
        plan_for_date(date, args["target"])
