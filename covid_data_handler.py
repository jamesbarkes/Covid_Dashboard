"""
This module handles the covid data and displays it on a server using flask.
"""

import csv
import sched
import time
import json
import logging
from datetime import datetime, timedelta
from csv import DictReader
from uk_covid19 import Cov19API
from flask import Flask, render_template, request
from covid_news_handling import delete_news
from covid_news_handling import update_news

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
update = []
update_reference = {}

with open("config.json","r", encoding="utf-8") as information: # reads data from the config file
    config = json.load(information)
    city = config["city"]
    title = config["title"]
    logging_path = config["logging-path"]

FORMAT = '%(levelname)s: %(asctime)s: %(message)s' # format of the logging
logging.basicConfig(filename=logging_path, filemode="w", format=FORMAT, level=logging.DEBUG)

def add_scheduled_event(update_interval: str, update_name: str) -> None:
    """
    Add scheduled event to the update list.

    Arguments:
    update_interval: The time the event will take place.
    update_name: The name of the scheduled update.
    """
    update.append({
        "title": update_name,
        "content": (f"Update at {update_interval}")
    }) # adds the new update to the list of already scheduled updates
    logging.info("Event: %s. Has been scheduled for %s.", update_name, update_interval)

def schedule_covid_updates(update_interval: str, update_name: str, repeat: str,
    updating_covid: str, updating_news:str) -> None:
    """
    Convert the time into a delay and schedule the covid updates.

    Arguments:
    update_interval: The time the event will take place.
    update_name: The name of the scheduled update.
    repeat: Whether the update will repeat.
    updating_covid: Whether the update will update the covid data.
    updating_news: Whether the update will update the news.

    Parameters:
    delay: The time in seconds until the update occurs.
    """
    if updating_covid != "covid-data" and updating_news != "news":
        logging.warning("No data has been requested for an update.")
        return # returns to index if no update data has been requested
    logging.debug("Covid updates are being scheduled.")
    delay = hhmm_to_seconds(update_interval) - hhmm_to_seconds(datetime.now().strftime("%H:%M"))
    if repeat == "repeat":
        update_name += " | Repeating"
    if updating_covid == "covid-data":
        update_name += " | Updating Covid Data"
    if updating_news == "news":
        update_name += " | Updating News"
    update_reference[update_name] = s.enter(int(delay), 1,
    update_data, kwargs = {"update_name": update_name,
    "repeat":repeat,
    "updating_covid":updating_covid,
    "updating_news":updating_news}) # sets a referencable name for the update
    add_scheduled_event(update_interval, update_name)

def update_data(update_name: str, repeat: str,
    updating_covid: str, updating_news: str) -> render_template:
    """
    Updates the data requested by the user.

    Arguments:
    update_interval: The time the event will take place.
    update_name: The name of the scheduled update.
    repeat: Whether the update will repeat.
    updating_covid: Whether the update will update the covid data.
    updating_news: Whether the update will update the news.

    Return:
    A newly rendered template with the updated data.
    """
    if repeat == "repeat":
        update_reference[update_name] = s.enter(86400, 1, update_data,
        kwargs = {"repeat":repeat,
        "updating_covid":updating_covid,
        "updating_news":updating_news}) # repeats the update one day later with the same name
        logging.info("The update will be repeated tomorrow.")
    if updating_news == "news" and updating_covid != "covid-data":
        news = update_news()
        if repeat != "repeat": # doesn't delete the update if it is repeating
            delete_update(update_name, False)
        logging.info("News has been updated.")
        return render_template("index.html",
        news_articles=news)
    elif updating_news != "news" and updating_covid == "covid-data":
        covid_data = covid_API_request()
        (local_last7days_cases,
        national_last7days_cases,
        current_hospital_cases,
        total_deaths) = process_covid_data(covid_data)
        if repeat != "repeat":
            delete_update(update_name, False)
        logging.info("Covid data has been updated.")
        return render_template('index.html',
        local_7day_infections=(local_last7days_cases),
        national_7day_infections=(national_last7days_cases),
        hospital_cases=(f"Hospital Cases: {current_hospital_cases}"),
        deaths_total=(f"Total Deaths: {total_deaths}"))
    elif updating_news == "news" and updating_covid == "covid-data":
        covid_data = covid_API_request()
        (local_last7days_cases,
        national_last7days_cases,
        current_hospital_cases,
        total_deaths) = process_covid_data(covid_data)
        news = update_news()
        if repeat != "repeat":
            delete_update(update_name, False)
        logging.info("Covid data and news have been updated.")
        return render_template('index.html',
        news_articles=news,
        local_7day_infections=(local_last7days_cases),
        national_7day_infections=(national_last7days_cases),
        hospital_cases=(f"Hospital Cases: {current_hospital_cases}"),
        deaths_total=(f"Total Deaths: {total_deaths}"))
    delete_update(update_name, False)

def delete_update(update_to_delete: str, delete_s: bool) -> None:
    """
    Deletes the update from the template and removes it from the scheduled queue.

    Arguments:
    update_to_delete: The title of the update that is to be deleted.
    delete_s: Shows whether the event has been done or if it's being cancelled before.
    """
    for all_update in update:
        if all_update["title"] == update_to_delete: # checks for ipdate matching an update title
            update.remove(all_update)
            logging.debug("The update has been removed")
            if delete_s: # checks if the event hasn't occurred and has just been cancelled
                s.cancel(update_reference[update_to_delete])
                return
            return



@app.route('/index')
def index() -> render_template:
    """
    The main part of the code that is ran when the user visits the address.

    Parameters:
    covid_data: This is a dictionary of the data returned from the API request.
    local_last7days_cases: The number of local cases in the last 7 days.
    national_last7days_cases: The number of national cases in the last 7 days.
    current_hospital_cases: The number of current hospital cases.
    total_deaths: The number of total deaths in The UK.
    news: A list of all the news.
    update_name: The name of the scheduled update.
    update_interval: The time the event will take place.
    repeat: Whether the update will repeat.
    updating_covid: Whether the update will update the covid data.
    updating_news: Whether the update will update the news.
    news_to_delete: The title of the news that is to be deleted.
    update_to_delete: The title of the update that is to be deleted.

    Returns:
    A rendered template with the data.
    """
    s.run(blocking=False) # stops the scheduler from blocking the server from running
    covid_data = covid_API_request()
    (local_last7days_cases,
    national_last7days_cases,
    current_hospital_cases,
    total_deaths) = process_covid_data(covid_data)
    news = update_news()
    update_name = request.args.get("two")
    if update_name: # checks if an update has been scheduled
        update_interval = request.args.get("update")
        repeat = request.args.get("repeat")
        updating_covid = request.args.get("covid-data")
        updating_news = request.args.get("news")
        schedule_covid_updates(update_interval, update_name, repeat, updating_covid, updating_news)
    if request.args.get("notif"): # checks if news has been deleted
        news_to_delete = request.args.get("notif")
        delete_news(news_to_delete)
    if request.args.get("update_item"): # checks if an update has been deleted
        update_to_delete = request.args.get("update_item")
        delete_update(update_to_delete, True)
    return render_template('index.html',
    title=(title),
    news_articles=news,
    updates=update,
    location=(city),
    local_7day_infections=(local_last7days_cases),
    nation_location=("United Kingdom"),
    national_7day_infections=(national_last7days_cases),
    hospital_cases=(f"Hospital Cases: {current_hospital_cases}"),
    deaths_total=(f"Total Deaths: {total_deaths}"))

def covid_API_request() -> dict:
    """
    Retrieves the data from the covid API using location and location type.

    Parameters:
    data: A dictionary including all the data that is retrieved from the API.
    covid_location: The templates for the filter of the API.
    cases_and_deaths: The structures that are used for the API.
    api: The data the API returns.

    Returns:
    A dictionary of the data retrieved from the API.
    """
    logging.debug("Data is being requested from the API")
    data = {}
    covid_location = (f'areaName={city}','areaType=ltla') # first checks for local cases
    cases_and_deaths = {"date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate"}
    api = Cov19API(filters=covid_location, structure=cases_and_deaths)
    data["local"] = api.get_json()
    covid_location = ('areaName=United Kingdom','areaType=overview') # then checks national cases
    cases_and_deaths = {"date": "date",
    "areaName": "areaName",
    "newCasesBySpecimenDate": "newCasesBySpecimenDate",
    "cumDailyNsoDeathsByDeathDate": "cumDailyNsoDeathsByDeathDate",
    "hospitalCases": "hospitalCases"}
    api = Cov19API(filters=covid_location, structure=cases_and_deaths)
    data["national"] = api.get_json()
    logging.debug("The api has returned the data.")
    return data

def process_covid_data(covid_data: dict) -> tuple[int, int, int, int]:
    """
    Processes the covid data and performs the calculations to return the data needed.

    Arguments:
    covid_data: A dictionary of all the covid data.

    Parameters:
    covid_data: This is a dictionary of the data returned from the API request.
    local_last7days_cases: The number of local cases in the last 7 days.
    national_last7days_cases: The number of national cases in the last 7 days.
    current_hospital_cases: The number of current hospital cases.
    total_deaths: The number of total deaths in The UK.

    Returns:
    4 integers of the data wanted from the API
    """
    local_last7days_cases = 0
    national_last7days_cases = 0
    local_covid_data = covid_data["local"]
    national_covid_data = covid_data["national"]
    for i in range(7):
        for data in local_covid_data["data"]:
            if data['date'] == (datetime.now() - timedelta(i+4)).strftime("%Y-%m-%d"):
                local_last7days_cases += int(data['newCasesBySpecimenDate'])
        for data in national_covid_data["data"]:
            if data['date'] == (datetime.now() - timedelta(i+4)).strftime("%Y-%m-%d"):
                national_last7days_cases += int(data['newCasesBySpecimenDate'])
    for data in national_covid_data["data"]:
        if data['date'] == (datetime.now() - timedelta(2)).strftime("%Y-%m-%d"):
            current_hospital_cases = int(data['hospitalCases'])
        if data['date'] == (datetime.now() - timedelta(14)).strftime("%Y-%m-%d"):
            total_deaths = int(data['cumDailyNsoDeathsByDeathDate'])
    logging.info("The data has been processed.")
    return local_last7days_cases, national_last7days_cases, current_hospital_cases, total_deaths

def process_covid_csv_data(covid_csv_data: csv) -> tuple[int, int, int]:
    """
    (For Test) Processes covid data from a csv file.

    Arguments:
    covid_csv_data: A csv file of all the data.

    Parameters:
    last7days_cases: The number of cases in the last 7 days with a default value of 0.
    dict_reader: The csv file converted into a dictionary.
    list_of_dict: The dictionary converted into a list.
    date: The date used for the test.

    Returns:
    3 integers of the data wanted from the CSV file.
    """
    last7days_cases = 0
    dict_reader = DictReader(covid_csv_data) # converts csv file into a dictionary
    list_of_dict = list(dict_reader) # then a list of llists in the dictionary
    date = ("2021-10-28")
    date = datetime.strptime(date, '%Y-%m-%d')
    for i in range(7):
        for each_line in list_of_dict:
            if each_line['current_date'] == (date - timedelta(i+2)).strftime("%Y-%m-%d"):
                last7days_cases += int(each_line['newCasesBySpecimenDate'])
    for each_line in list_of_dict:
        if each_line['current_date'] == date.strftime("%Y-%m-%d"):
            current_hospital_cases = int(each_line['hospitalCases'])
        if each_line['current_date'] == (date - timedelta(13)).strftime("%Y-%m-%d"):
            total_deaths = int(each_line['cumDailyNsoDeathsByDeathDate'])
    return last7days_cases, current_hospital_cases, total_deaths

def parse_csv_data (csv_filename: str) -> list[str]:
    """
    (For Test) Parses the csv data from filename into list of strings.

    Arguments:
    csv_filename: The name of the csv file to be opened.

    Parameters:
    data_list: List of csv data.

    Returns:
    The list of data.
    """
    data_list = open(csv_filename, encoding="utf-8").readlines()
    return data_list

def minutes_to_seconds(minutes: str) -> int:
    """
    Converts minutes to seconds

    Arguments:
    minutes: The number of minutes to be converted to seconds.

    Returns:
    The number of seconds.
    """
    return int(minutes)*60

def hours_to_minutes(hours: str) -> int:
    """
    Converts hours to minutes

    Arguments:
    hours: The number of hours to be converted to minutes.

    Returns:
    The number of minutes.
    """
    return int(hours)*60

def hhmm_to_seconds(hhmm: str) -> int:
    """
    Converts hours and minutes into seconds.

    Arguments:
    hhmm: The time in hh:mm format.

    Returns:
    If the argument is a valid format it returns the time in seconds.
    """
    if len(hhmm.split(':')) != 2:
        print('Incorrect format. Argument must be formatted as HH:MM')
        return None
    return minutes_to_seconds(hours_to_minutes(hhmm.split(':')[0])) + \
        minutes_to_seconds(hhmm.split(':')[1])

if __name__ == "__main__":
    app.run()
