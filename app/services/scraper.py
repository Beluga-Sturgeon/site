
from app.services.cnst import *
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup, Tag
import re

from app.services.cnst import constants
from app.services.fmpRequester import get_jsonparsed_data


"""SCRAPES OFF GFINANCE"""
def getPercentChange(current, previous) ->str:
    """percent difference. Example:\n
    >>> getPriceChangeStr(12, 10))\n
    >>> '20.0%'"""
    return "%.3g"%((current - previous)/previous * 100) + "%"


def getPriceChangeStr(current, open, label:str) ->str:
    """Gves string that shows difference, and percent difference along wth a label.. Example:\n
    >>> getPriceChangeStr(12, 10, 'difference'))\n
    >>> '+2.00 (20.0%) difference'"""
    diff = "+%.3g"%(current-open) if (current-open) >= 0 else "%.3g"%(current-open)
    return diff + " (" + getPercentChange(current, open) + ") "+label

def getPriceChangeStr(ticker:str) ->str:
    """Gves string that shows difference, and percent difference along wth a label.. Example:\n
    >>> getPriceChangeStr(12, 10, 'difference'))\n
    >>> '+2.00 (20.0%) difference'"""
    fmp_url = (f"https://financialmodelingprep.com/api/v3/stock-price-change/{ticker}?apikey={constants.FMP_API_KEY}")
    data = get_jsonparsed_data(fmp_url)
    daychange = data[0]["1D"]

    return str(daychange) + "%"

def scrapeTickerFromUrl(url:str) ->str:
    """Scrapes the ticker part from the Url. For example:\n
    >>> scrapeTickerFromUrl('https://www.google.com/finance/quote/GOOGL:NASDAQ')\n
    >>> 'GOOGL'"""

def human_format(num):
    """Gives numbers human format. Example:\n
    >>> human_format(272900238)\n
    >>> '273M'"""
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def scrapeMarketStatus(soup:BeautifulSoup) ->str:
    "Scrapes google finance page for the close and open date."
    try:
        return re.sub("Disclaimer$", "", soup.find('div', {"class":"ygUjEc","jsname":"Vebqub"}).text)
    except:
        return ""

def scrapeCompanyName(soup:BeautifulSoup) ->str:
    "Scrapes google finance page for the close and open date."
    return re.sub("Disclaimer$", "", soup.find('div', {"class":"zzDege"}).text)
  

def getScrapingURL(ticker:str)->str:
    """Finds exchanger ending for scraping on google finance. Example:\n 
    >>> getScrapingURL('MSFT')
    >>> https://www.google.com/finance/quote/MSFT:NASDAQ"""
    data = requests.get(f'{constants.GOOGLE_FINANCE_URL}{ticker}', headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, 'lxml')
    parentList = soup.find("ul", {"class":["sbnBtf xJvDsc ANokyb"]})
    url = parentList.find("a")["href"] ##finds the first option link, and retuns it.
    exchanger = url[url.index(":") + 1:]
    return f"{constants.GOOGLE_FINANCE_URL}{ticker}:{exchanger}"

def scrapeCompanyDesc(soup:BeautifulSoup) ->str:
    try:
        return re.sub("\. Wikipedia$","",soup.find("div", {"class":"bLLb2d"}).text)
    except:
        return "No Description available"

def getFloat(num:str) ->float:
    """Returns the float of a number containing symbols
    >>> getFloat('$262.27')
    >>> 262.27"""
    return float(re.sub("[$,]", "", num))

def scrapePrice(soup:BeautifulSoup):
    return soup.find("div", {"class":["YMlKec fxKbKc"]}).text

def scrapePrevClose(soup:BeautifulSoup):
    return soup.find("div", {"class":"P6K39c"}).text

def scrapeIncomeStatement(soup:BeautifulSoup) ->dict:
    """current keys:\n
Revenue\n
Operating expense\n
Net income\n
Net profit margin\n
Earnings per share\n
EBITDA\n
Effective tax rate"""
    incomeStatement = {}
    incomeStatementTable = soup.find_all("table", {"class":"slpEwd"})[0] # Replace with actual index for deployment
    rows = incomeStatementTable.find_all("tr", {"class":"roXhBd"})[1:]
    for row in rows:
        label = row.find("div", {"class":"rsPbEe"}).text
        value = row.find("td", {"class":"QXDnM"}).text
        try:
            yearChange = row.find("span",{"class":["JwB6zf", "CnzlGc"]}).text
        except:
            yearChange = row.find("td",{"class":"gEUVJe"}).text
        if yearChange[0] not in ["—", "-"]:
            yearChange = "+" + yearChange
        incomeStatement[label] = {"value":value, "change":yearChange}
    return incomeStatement

def scrapeBalanceSheet(soup:BeautifulSoup) ->dict:
    """current keys:\n
Cash and short-term investments\n
Total assets\n
Total liabilities\n
Total equity\n
Shares outstanding\n
Price to book\n
Return on assets\n
Return on capital"""
    balanceSheet = {}
    balanceSheetTable = soup.find_all("table", {"class":"slpEwd"})[0] # Replace with actual index for deployment
    rows = balanceSheetTable.find_all("tr", {"class":"roXhBd"})[1:]
    for row in rows:
        label = row.find("div", {"class":"rsPbEe"}).text
        value = row.find("td", {"class":"QXDnM"}).text
        try:
            yearChange = row.find("span",{"class":["JwB6zf", "CnzlGc"]}).text
        except:
            yearChange = row.find("td",{"class":"gEUVJe"}).text
        if yearChange[0] not in ["—", "-"]:
            yearChange = "+" + yearChange
        balanceSheet[label] = {"value":value, "change":yearChange}
    return balanceSheet

def scrapeCashFlow(soup:BeautifulSoup) ->dict:
    """current keys:\n
Net income\n
Cash from operations\n
Cash from investing\n
Cash from financing\n
Net change in cash\n
Free cash flow"""
    CashFlow = {}
    CashFlowTable = soup.find_all("table", {"class":"slpEwd"})[0] # Replace with actual index for deployment
    rows = CashFlowTable.find_all("tr", {"class":"roXhBd"})[1:]
    for row in rows:
        label = row.find("div", {"class":"rsPbEe"}).text
        value = row.find("td", {"class":"QXDnM"}).text
        try:
            yearChange = row.find("span",{"class":["JwB6zf", "CnzlGc"]}).text
        except:
            yearChange = row.find("td",{"class":"gEUVJe"}).text
        if yearChange[0] not in ["—", "-"]:
            yearChange = "+" + yearChange
        CashFlow[label] = {"value":value, "change":yearChange}
    return CashFlow

def scrapeCompanyWebsite(soup:BeautifulSoup) ->str:
    "Returns the URL for the company website"
    container = soup.find("div", {"class":"v5gaBd Yickn"})
    rows = container.find_all("div", {"class":"gyFHrc"})
    for row in rows:
        try:
            if row.find("div", {"class":"mfs7Fc"}).text == "Website":
                return row.find("a", {"class":"tBHE4e"})["href"]
        except:
            pass
    return "NO URL"

def scrapeCompanyLogo(companyWebsite:str):
    "Returns link to company logo given company website url"
    return constants.LOGO_CLEARBIT_URL + companyWebsite



def main():
    print(getScrapingURL("msft"))
    print("We out")
    data = requests.get(getScrapingURL("msft"), headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")
    print(scrapeIncomeStatement(soup))
    # pprint.pprint(scrapeCompanyLogo(scrapeCompanyWebsite(soup)))

if __name__ == "__main__":
    main()