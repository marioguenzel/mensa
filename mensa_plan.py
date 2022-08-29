#!/usr/bin/env python3

# pip install beautifulsoup4
# pip install requests
import requests
from bs4 import BeautifulSoup
from optparse import OptionParser
import datetime


def find_meals_and_prices(html):
    soup = BeautifulSoup(html, 'html.parser')

    rows = soup.find_all('tbody')  # table bodies
    rows = [row for body in rows for row in body.find_all('tr')]
    rows = [(entry.find('td', 'meals__column-title'), entry.find_all('td', 'meals__column-price')) for entry in rows]
    rows = [(entry[0].get_text(strip=True), [e.get_text(strip=True) for e in entry[1]]) for entry in rows
            if entry[0] is not None]

    return rows


def find_date(html):
    soup = BeautifulSoup(html, 'html.parser')
    date = soup.find('option', selected='selected')
    return date.get_text(strip=True)


# def print_meals_and_prices(meals_and_prices):
#     for row in meals_and_prices:
#         print(row[1][0], row[1][1], row[1][2], row[0])

def print_plan(plan_list):
    for row in plan_list:
        print(row[0], row[1])


def get_request(date):
    """date in format: 2021-08-26"""
    url = f"https://mobil.itmc.tu-dortmund.de/canteen-menu/v3/canteens/341/{date}"
    response = requests.request("GET", url)
    return response.json()


def beautify_mensa_plan(plan_dict):
    """Beautify mensa plan from the dictionary."""
    complete_list = []
    for entry in plan_dict:
        prices = entry['price']
        complete_list.append(
            [f"S: {prices['student']} B: {prices['staff']} G: {prices['guest']}", entry['title']['de']])

    return complete_list


def plan_for_date(date):
    try:
        # Get mensa plan as list of dictionaries
        plan_dict = get_request(date)

        # Beautify mensa plan
        plan_list = beautify_mensa_plan(plan_dict)

        # Print output
        print(f'--Mensa plan for {date}--')
        print_plan(plan_list)
    except:
        print(f'Mensa date for {date} could not be printed.')


if __name__ == '__main__':
    date = str(datetime.date.today())
    # options
    parser = OptionParser()
    parser.add_option("-d", "--date", dest="date", help="get mensa plan for DATE in the form yyyy-mm-dd",
                      metavar="DATE")
    parser.add_option("-p", "--plus", dest="plus", type='int', help="get mensa plan for today plus X days", metavar="X")
    parser.add_option("-n", "--next", dest="next", type='int', help="get mensa plan for next X days including today",
                      metavar="X")

    (options, args) = parser.parse_args()

    if options.date is not None:
        date = options.date

    if options.plus is not None:
        date = str(datetime.date.today() + datetime.timedelta(days=options.plus))

    if options.next is not None:
        next_var = options.next
        for idx in range(0, next_var + 1):
            date = str(datetime.date.today() + datetime.timedelta(idx))
            plan_for_date(date)
        quit()

    plan_for_date(date)
