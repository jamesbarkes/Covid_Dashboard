"""
This module handles the news and the news API.
"""
import json
import logging
from newsapi.newsapi_client import NewsApiClient

news = []
list_of_news = []

with open("config.json","r", encoding="utf-8") as information:
    config = json.load(information)
    api_key = config["API-key"]
    covid_terms = config["covid-terms"]

def add_news_to_list(headlines: dict) -> None:
    """
    Adds the news to the list of all news, so that we can see all the news, even the deleted ones.
    This is to make sure no news is repeated during an update.

    Arguments:
    headlines: All of the headlines in a dictionary.
    """
    list_of_news.append({
        "title": headlines["title"]
    }) # adds the new news to the list of news already received
    logging.debug("News has been added to the list.")

def add_news_article(headlines: dict) -> None:
    """
    Add the news to the articles which is used to show on the server.

    Arguments:
    headlines: All of the headlines in a dictionary.
    """
    news.append({
        "title": headlines["title"],
        "content": headlines["description"],
    }) # adds the news to the list of news to go on the server
    logging.debug("News has been added to the server.")

def delete_news(news_to_delete: str) -> None:
    """
    Delete the news from the displayed news.

    Arguments:
    news_to_delete: The title of the news to be deleted.
    """
    for all_news in news:
        if all_news["title"] == news_to_delete: # checks the news title against all news titles
            news.remove(all_news)
            logging.debug("News has been deleted.")
            return
    logging.warning("Could not delete the news.")

def update_news() -> list:
    """
    Updates the list of news to all the top headlines.

    Parameters:
    top_headlines: A dictionary of a ll the top headlines.
    articles: All of the articles in the top_headlines dictionary.
    in_list: A boolean that tells you whether the news has been displayed before.

    Returns:
    A list of all the news that is to be displayed.
    """
    top_headlines = news_API_request()
    articles = top_headlines["articles"]
    for headlines in articles:
        in_list = False # list is deafult not in list but checks whether to display it
        for all_news in list_of_news:
            if all_news["title"] == headlines["title"]:
                in_list = True
                logging.debug("News that has already been posted is in the list.")
        if in_list is not True:
            add_news_to_list(headlines)
            add_news_article(headlines)
    return news

def news_API_request() -> dict:
    """
    Makes a request from the API.

    Parameters:
    newsapi: Stores what the API returns.
    top_headlines: A dictionary of all the top headlines.

    Returns:
    The top headlines in dictionary format.
    """
    newsapi = NewsApiClient(api_key) # uses the client to recieve the api
    top_headlines = (newsapi.get_top_headlines(q=covid_terms)) # checks the top headlines for news
    logging.debug("News has been succesfully retrieved.")
    return top_headlines
