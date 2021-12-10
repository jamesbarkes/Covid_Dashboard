import logging
from covid_news_handling import add_news_article
from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import add_news_to_list

LOGGER = logging.getLogger(__name__)

def test_news_API_request():
    data = news_API_request()
    assert isinstance(data, dict)

def test_update_news():
    data = update_news()
    assert isinstance(data, list)

def test_add_news_to_list(caplog):
    caplog.set_level(logging.DEBUG)
    dictionary = ({"title": "News Title"})
    add_news_to_list(dictionary)
    assert "News has been added to the list." in caplog.text

def test_add_news_article(caplog):
    caplog.set_level(logging.DEBUG)
    dictionary = ({"title": "News Title",
        "description": "News Content"
    })
    add_news_article(dictionary)
    assert "News has been added to the server." in caplog.text
