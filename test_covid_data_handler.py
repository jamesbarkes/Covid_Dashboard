import logging
from covid_data_handler import parse_csv_data
from covid_data_handler import process_covid_csv_data
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from covid_data_handler import add_scheduled_event
from covid_data_handler import process_covid_data
from covid_data_handler import hhmm_to_seconds

LOGGER = logging.getLogger(__name__)

def test_parse_csv_data():
    data = parse_csv_data('nation_2021-10-28.csv')
    assert len(data) == 639

def test_process_covid_csv_data():
    last7days_cases , current_hospital_cases , total_deaths = \
        process_covid_csv_data ( parse_csv_data (
            'nation_2021-10-28.csv' ) )
    assert last7days_cases == 240_299
    assert current_hospital_cases == 7_019
    assert total_deaths == 141_544

def test_covid_API_request():
    data = covid_API_request()
    assert isinstance(data, dict)

def test_schedule_covid_updates():
    schedule_covid_updates(update_interval=10, update_name='update test', repeat='', updating_covid='',updating_news='')

def test_add_scheduled_event(caplog):
    caplog.set_level(logging.DEBUG)
    add_scheduled_event("00:00","Scheduled Update")
    assert "Event: Scheduled Update. Has been scheduled for 00:00." in caplog.text

def test_process_covid_data():
    api_data = covid_API_request()
    (local_last7days_cases,
    national_last7days_cases,
    current_hospital_cases,
    total_deaths) = process_covid_data(api_data)
    assert local_last7days_cases > 0
    assert national_last7days_cases > 0
    assert current_hospital_cases > 0
    assert total_deaths > 0

def test_hhmm_to_seconds():
    data = hhmm_to_seconds("01:30")
    assert data == 5400
