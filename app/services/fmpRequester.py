import json
from urllib.request import urlopen
import certifi
import requests
from app.services.cnst import constants

def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

def isTickerValid(ticker:str) -> bool:
    fmp_url = f"https://financialmodelingprep.com/api/v3/financial-statement-symbol-lists?apikey={constants.FMP_API_KEY}"
    alltickers = get_jsonparsed_data(fmp_url)
    return ticker in alltickers

def getInfo(ticker:str) -> dict:
    data = requests.get(constants.API_URL + constants.GET_TICKER_INFO_ENDING + ticker, headers=constants.REQ_HEADER).json()
    return data

def getFinancials(ticker:str) -> dict:
    data = requests.get(constants.API_URL + constants.GET_FINANCIALS_ENDING + ticker, headers=constants.REQ_HEADER).json()
    return data

def getNews(ticker:str) ->list[dict]:
    data = requests.get(constants.API_URL + constants.GET_NEWS_ENDING + ticker, headers=constants.REQ_HEADER).json()
    return data

def search(ticker):
    fmp_url = (f"https://financialmodelingprep.com/api/v3/search?query={ticker}&limit=10&exchange=NASDAQ&apikey={constants.FMP_API_KEY}")
    data = get_jsonparsed_data(fmp_url)
    return data

def get_profile(ticker):
    fmp_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)
    data = data[0]
    return data

def get_value(ticker):
    return get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/quote-short/{ticker}?apikey={constants.FMP_API_KEY}")[0]["price"]