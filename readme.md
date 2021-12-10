# COVID Dashboard

This COVID Dashboard displays local and national statistics about the virus while also displaying the top headlines. The user may also schedule updates for when they would like either the statistics or news to be updated.

## Prerequisites
Python Version: 3.9.9

## Installation

Download and install this package.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the packages stored in the requirements file:
```bash
pip -r requirements.txt
```

You will need to get your own API key at [NewsAPI](https://newsapi.org/). And enter it into, along with the other relevant data, the ```config.json``` file.

**The program will not work if the values in the config file are not filled!**
## Getting Started
### Starting the Program
* Go into the folder with the program in.
* Enter ```python -m covid_data_handler``` into your terminal.
* Go to your web browser and visit the website ```http://127.0.0.1:5000/index```.
### Scheduling Updates
There is an option to schedule an update with a few different selections, you can:

* Set a time to update. (**Required**)
* Set a name for the update. (**Required**)
* Select whether to repeat the update, the same time, the next day.
* Select whether you'd like to update the covid data.
* Select whether you'd like to update the news articles.

### Deleting Updates
You can press the [x] at the top of the update to cancel and remove it.

### Deleting News
You can press the [x] at the top of the news to cancel and remove it and stop it from returning after an update.

## Testing
Testing is done via the ```pytest``` package. It can be installed by running:
```bash
pip install pytest
```
Then find the directory you are currently in and type:
```bash 
cd <file location>
```
Before typing:
```bash
pytest
```
## Developer Documentation
This can be found by navigating to:
```Docs``` -> ```_build``` -> ```html``` -> ```index.html```
## Details
### License: [MIT](https://choosealicense.com/licenses/mit/)
### Author: James Barkes
### Acknowledgements: Hugo Barbosa & Matt Collison
### Github Link: [https://github.com/jamesbarkes/covid_dashboard](https://github.com/jamesbarkes/covid_dashboard)