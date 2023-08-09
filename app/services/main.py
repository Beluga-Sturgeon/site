from flask import Flask,render_template, request, session, redirect, url_for
import requests
from flask_mail import Mail, Message
from threading import Thread
import gunicorn
import os
from urllib.request import urlopen
import json
import certifi
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
import re
server = gunicorn.SERVER


class constants():
    FMP_API_KEY = "b0446da02c01a0943a01730dc2343e34"
    TRUE  = "true"
    FALSE = "false"


    API_URL          = "https://Foresightapi.herokuapp.com"
    REQ_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}



    VALIDATE_TICKER_ENDING= "/isTickerValid/"
    GET_TICKER_INFO_ENDING= "/getInfo/"
    GET_NEWS_ENDING= "/getNews/"
    GET_FINANCIALS_ENDING= "/getFinancials/"

    EXAMPLE_INFO = {'52WeekChange': -0.08975369,
    'SandP52WeekChange': -0.11385685,
    'address1': 'One Microsoft Way',
    'algorithm': None,
    'annualHoldingsTurnover': None,
    'annualReportExpenseRatio': None,
    'ask': 259.14,
    'askSize': 1200,
    'averageDailyVolume10Day': 24772610,
    'averageVolume': 31688331,
    'averageVolume10days': 24772610,
    'beta': 0.932311,
    'beta3Year': None,
    'bid': 259.12,
    'bidSize': 900,
    'bookValue': 21.773,
    'category': None,
    'circulatingSupply': None,
    'city': 'Redmond',
    'coinMarketCapLink': None,
    'companyOfficers': [],
    'country': 'United States',
    'currency': 'USD',
    'currentPrice': 259.23,
    'currentRatio': 1.988,
    'dateShortInterest': 1656547200,
    'dayHigh': 259.59,
    'dayLow': 253.69,
    'debtToEquity': 47.863,
    'dividendRate': 2.48,
    'dividendYield': 0.0097,
    'earningsGrowth': 0.094,
    'earningsQuarterlyGrowth': 0.082,
    'ebitda': 94982995968,
    'ebitdaMargins': 0.49327,
    'enterpriseToEbitda': 19.933,
    'enterpriseToRevenue': 9.833,
    'enterpriseValue': 1893338447872,
    'exDividendDate': 1660694400,
    'exchange': 'NMS',
    'exchangeTimezoneName': 'America/New_York',
    'exchangeTimezoneShortName': 'EDT',
    'expireDate': None,
    'fiftyDayAverage': 261.1042,
    'fiftyTwoWeekHigh': 349.67,
    'fiftyTwoWeekLow': 241.51,
    'financialCurrency': 'USD',
    'fiveYearAverageReturn': None,
    'fiveYearAvgDividendYield': 1.25,
    'floatShares': 7472077634,
    'forwardEps': 10.73,
    'forwardPE': 24.159369,
    'freeCashflow': 48917000192,
    'fromCurrency': None,
    'fullTimeEmployees': 181000,
    'fundFamily': None,
    'fundInceptionDate': None,
    'gmtOffSetMilliseconds': '-14400000',
    'grossMargins': 0.6873,
    'grossProfits': 115856000000,
    'heldPercentInsiders': 0.00075,
    'heldPercentInstitutions': 0.71946996,
    'impliedSharesOutstanding': 0,
    'industry': 'Software—Infrastructure',
    'isEsgPopulated': False,
    'lastCapGain': None,
    'lastDividendDate': 1652832000,
    'lastDividendValue': 0.62,
    'lastFiscalYearEnd': 1625011200,
    'lastMarket': None,
    'lastSplitDate': 1045526400,
    'lastSplitFactor': '2:1',
    'legalType': None,
    'logo_url': 'https://logo.clearbit.com/microsoft.com',
    'longBusinessSummary': 'Microsoft Corporation develops, licenses, and '
                            'supports software, services, devices, and solutions '
                            'worldwide. Its Productivity and Business Processes '
                            'segment offers Office, Exchange, SharePoint, '
                            'Microsoft Teams, Office 365 Security and Compliance, '
                            'and Skype for Business, as well as related Client '
                            'Access Licenses (CAL); Skype, Outlook.com, OneDrive, '
                            'and LinkedIn; and Dynamics 365, a set of cloud-based '
                            'and on-premises business solutions for organizations '
                            'and enterprise divisions. Its Intelligent Cloud '
                            'segment licenses SQL, Windows Servers, Visual Studio, '
                            'System Center, and related CALs; GitHub that provides '
                            'a collaboration platform and code hosting service for '
                            'developers; and Azure, a cloud platform. It also '
                            'offers support services and Microsoft consulting '
                            'services to assist customers in developing, '
                            'deploying, and managing Microsoft server and desktop '
                            'solutions; and training and certification on '
                            'Microsoft products. Its More Personal Computing '
                            'segment provides Windows original equipment '
                            'manufacturer (OEM) licensing and other non-volume '
                            'licensing of the Windows operating system; Windows '
                            'Commercial, such as volume licensing of the Windows '
                            'operating system, Windows cloud services, and other '
                            'Windows commercial offerings; patent licensing; '
                            'Windows Internet of Things; and MSN advertising. It '
                            'also offers Surface, PC accessories, PCs, tablets, '
                            'gaming and entertainment consoles, and other devices; '
                            'Gaming, including Xbox hardware, and Xbox content and '
                            'services; video games and third-party video game '
                            'royalties; and Search, including Bing and Microsoft '
                            'advertising. It sells its products through OEMs, '
                            'distributors, and resellers; and directly through '
                            'digital marketplaces, online stores, and retail '
                            'stores. It has collaborations with Dynatrace, Inc., '
                            'Morgan Stanley, Micro Focus, WPP plc, ACI Worldwide, '
                            'Inc., and iCIMS, Inc., as well as strategic '
                            'relationships with Avaya Holdings Corp. and wejo '
                            'Limited. Microsoft Corporation was founded in 1975 '
                            'and is based in Redmond, Washington.',
    'longName': 'Microsoft Corporation',
    'market': 'us_market',
    'marketCap': 1938788974592,
    'maxAge': 1,
    'maxSupply': None,
    'messageBoardId': 'finmb_21835',
    'morningStarOverallRating': None,
    'morningStarRiskRating': None,
    'mostRecentQuarter': 1648684800,
    'navPrice': None,
    'netIncomeToCommon': 72456003584,
    'nextFiscalYearEnd': 1688083200,
    'numberOfAnalystOpinions': 46,
    'open': 257.575,
    'openInterest': None,
    'operatingCashflow': 87115997184,
    'operatingMargins': 0.42556,
    'payoutRatio': 0.2463,
    'pegRatio': 1.7,
    'phone': '425 882 8080',
    'preMarketPrice': 258,
    'previousClose': 254.25,
    'priceHint': 2,
    'priceToBook': 11.906031,
    'priceToSalesTrailing12Months': 10.068649,
    'profitMargins': 0.37627998,
    'quickRatio': 1.773,
    'quoteType': 'EQUITY',
    'recommendationKey': 'buy',
    'recommendationMean': 1.7,
    'regularMarketDayHigh': 259.59,
    'regularMarketDayLow': 253.69,
    'regularMarketOpen': 257.575,
    'regularMarketPreviousClose': 254.25,
    'regularMarketPrice': 259.23,
    'regularMarketVolume': 17378178,
    'returnOnAssets': 0.15674,
    'returnOnEquity': 0.48721,
    'revenueGrowth': 0.184,
    'revenuePerShare': 25.642,
    'revenueQuarterlyGrowth': None,
    'sector': 'Technology',
    'sharesOutstanding': 7479029760,
    'sharesPercentSharesOut': 0.0052,
    'sharesShort': 38896339,
    'sharesShortPreviousMonthDate': 1653955200,
    'sharesShortPriorMonth': 46001375,
    'shortName': 'Microsoft Corporation',
    'shortPercentOfFloat': 0.0052,
    'shortRatio': 1.3,
    'startDate': None,
    'state': 'WA',
    'strikePrice': None,
    'symbol': 'MSFT',
    'targetHighPrice': 500,
    'targetLowPrice': 251.76,
    'targetMeanPrice': 351.45,
    'targetMedianPrice': 349.5,
    'threeYearAverageReturn': None,
    'toCurrency': None,
    'totalAssets': None,
    'totalCash': 104660000768,
    'totalCashPerShare': 13.994,
    'totalDebt': 77980999680,
    'totalRevenue': 192557006848,
    'tradeable': False,
    'trailingAnnualDividendRate': 2.42,
    'trailingAnnualDividendYield': 0.009518191,
    'trailingEps': 9.58,
    'trailingPE': 27.0595,
    'trailingPegRatio': 1.7307,
    'twoHundredDayAverage': 296.8598,
    'volume': 17378178,
    'volume24Hr': None,
    'volumeAllCurrencies': None,
    'website': 'https://www.microsoft.com',
    'yield': None,
    'ytdReturn': None,
    'zip': '98052-6399'}

class emailvars():
    EMAILREGEX            = '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    EMAIL                 = os.getenv("EMAIL")
    SENDTOEMAIL           = os.getenv("SENDTOEMAIL")
    EMAILPASSWORD         = os.getenv("EMAILPASSWORD")
    PORT                  = 465  # For SSL

def createApp():
    app = Flask(
    __name__,
    template_folder=r"templates",
    static_folder=r"static"
    )
    return app


def get_jsonparsed_data(url):

    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

app = createApp()

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = emailvars.EMAIL,
    MAIL_PASSWORD = emailvars.EMAILPASSWORD,
))


mail = Mail(app)



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

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def scrapeMarketStatus(soup:BeautifulSoup) ->str:
    "Scrapes google finance page for the close and open date."
    return re.sub("Disclaimer$", "", soup.find('div', {"class":"ygUjEc","jsname":"Vebqub"}).text)

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


def scrapeNews(soup:BeautifulSoup) -> dict:
    """Scrapes the news articles off of {constants.GOOGLE_FINANCE_URL}{ticker} in the form of a dictionary
    EXAPMLE:
    {'articles': [{'date': '18 hours ago',
               'link': 'https://www.cnbc.com/2022/07/20/microsoft-eases-up-on-hiring-as-economic-concerns-hit-more-of-the-tech-industry.html',
               'publisher': 'CNBC',
               'title': 'Microsoft eases up on hiring as economic concerns hit '
                        'more of the tech \n'
                        'industry'},
              {'date': '2 days ago',
               'link': 'https://www.barrons.com/articles/microsoft-stock-recession-analyst-price-target-51658230843',
               'publisher': "Barron's",
               'title': "Microsoft Stock Is a 'Good Place to Hide.' This "
                        'Analyst CutsPrice Target \n'
                        'Anyway.'},
              {'date': '18 hours ago',
               'link': 'https://www.bloomberg.com/news/articles/2022-07-20/microsoft-cuts-many-open-job-listings-in-weakening-economy',
               'publisher': 'Bloomberg.com',
               'title': 'Microsoft Cuts Many Open Job Listings in Weakening '
                        'Economy'},
              {'date': '16 hours ago',
               'link': 'https://money.usnews.com/investing/news/articles/2022-07-20/microsoft-teams-down-for-thousands-of-users-downdetector',
               'publisher': 'US News Money',
               'title': 'Microsoft Teams Back up for Most Users After Global '
                        'Outage'},
              {'date': '1 week ago',
               'link': 'https://seekingalpha.com/article/4523194-microsoft-buy-before-q4-earnings',
               'publisher': 'Seeking Alpha',
               'title': 'Microsoft Stock: A Buy Before Q4 Earnings '
                        '(NASDAQ:MSFT)'},
              {'date': '20 hours ago',
               'link': 'https://www.tipranks.com/news/article/microsoft-stock-fx-headwinds-likely-to-persist-says-analyst/',
               'publisher': 'TipRanks',
               'title': 'Microsoft Stock: FX Headwinds Likely to Persist, Says '
                        'Analyst'},
              {'date': '1 day ago',
               'link': 'https://finbold.com/citi-analyst-views-microsoft-as-a-solid-recession-proof-stock/',
               'publisher': 'Finbold',
               'title': 'Citi analyst views Microsoft as a solid '
                        'recession-proof stock'}]}"""
    newsBoxes = soup.find_all("div", {"class":["zLrlHb EA7tRd"]})
    articles = []
    if newsBoxes:
        for element in newsBoxes:
            article = {}
            article["link"] = element.find("a")["href"]
            article["publisher"] = element.find("div", {"class":"AYBNIb"}).text
            article["date"] = re.sub("\n","",element.find("div", {"class":"HzW5e"}).text)
            article["title"] = element.find("div", {"class":"F2KAFc"}).text
            articles.append(article)
        return {"articles":articles}
    else:
        newsBoxes = soup.find_all("div", {"class":"yY3Lee"})
        for element in newsBoxes:
            article = {}
            article["link"] = element.find("a")["href"]
            article["publisher"] = element.find("div", {"class":"sfyJob"}).text
            article["date"] = re.sub("\n","",element.find("div", {"class":"Adak"}).text)
            article["title"] = element.find("div", {"class":"Yfwt5"}).text
            articles.append(article)
        return {"articles":articles}


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

def scrapeIncomeStatement(ticker:str) ->dict:
    """returns values in {value:xx, change:xx}"""
    incomeStatement = {}
    fmp_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&limit=120&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    latest, older = data[-1], data[-2]

    for key in latest.keys():
        new, old = latest[key], older[key]
        change = (new - old) / old
        incomeStatement[key] = {"value":latest[key], "change":change}
    return incomeStatement



def scrapeBalanceSheet(ticker:str) ->dict:
    """returns values in {value:xx, change:xx}"""
    balanceSheet = {}
    fmp_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period=quarter&limit=120&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    latest, older = data[-1], data[-2]

    for key in latest.keys():
        new, old = latest[key], older[key]
        change = (new - old) / old
        balanceSheet[key] = {"value":latest[key], "change":change}
    return balanceSheet

def scrapeCashFlow(soup:BeautifulSoup) ->dict:
    """returns values in {value:xx, change:xx}"""
    cashflow = {}
    fmp_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period=quarter&limit=120&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    latest, older = data[-1], data[-2]

    for key in latest.keys():
        new, old = latest[key], older[key]
        change = (new - old) / old
        cashflow[key] = {"value":latest[key], "change":change}
    return cashflow

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


def getPriceChangeStr(current, open, label:str) ->str:
    """Gves string that shows difference, and percent difference along wth a label.. Example:\n
    >>> getPriceChangeStr(12, 10, 'difference'))\n
    >>> '+2.00 (20.0%) difference'"""
    diff = "+%.3g"%(current-open) if (current-open) >= 0 else "%.3g"%(current-open)
    return diff + " (" + getPercentChange(current, open) + ") "+label

def getPercentChange(current, previous) ->str:
    """percent difference. Example:\n
    >>> getPriceChangeStr(12, 10))\n
    >>> '20.0%'"""
    return "%.3g"%((current - previous)/previous * 100) + "%"











@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "./error.html",
        code = 404,
        msg = f"page not found. Make sure you typed it in correctly.",
        desc = f"{e}"
    )

@app.errorhandler(500)
def InternalError(e):
    return render_template(
        "./error.html",
        code = 500,
        msg = f"Internal server error. Contact me about this. ",
        desc = f"{e}"
    )

@app.errorhandler(403)
def forbidden(e):
    return render_template(
        "./error.html",
        code = 403,
        msg = f"Forbidden. We tried to fetch some data. You said no. Thats ok. Consent is great.",
        desc = f"{e}"
    )

@app.route("/")
def home():
    hotactions = [{"ticker":"NVDA"}, {"ticker":"NVDA"}, {"ticker":"NVDA"}, {"ticker":"NVDA"}, {"ticker":"NVDA"}]
    return render_template("./index.html", hotactions=hotactions)

@app.route("/home")
def home2():
    return render_template("./index.html")

@app.route("/index")
def home1():
    return render_template("./index.html")

@app.route("/team")
def team():
    return render_template("./team.html")

@app.route("/apps")
def apps():
    return render_template("./apps.html")

@app.route("/about")
def about():
    return render_template("./aboutUs.html")

@app.route("/legal")
def legal():
    return render_template("./legal.html")

@app.route("/ContactMe/<int:sent>")
def ContactMe(sent):
    bool = False
    if sent == 1:
        bool = True
    return render_template("./index.html", sent=bool)


@app.route("/ContactMe/HandleData", methods=['POST'])
def HandleData():
    projectpath = request.form    
    sendingEmail = projectpath.get("email")
    name = projectpath.get("name")
    subject = projectpath.get("subject")
    message = projectpath.get("content")
    msg = Message(
        subject = subject,
        recipients= [emailvars.SENDTOEMAIL],
        body = f"FROM: {name}, EMAIL: {sendingEmail}, \n {message}"
    )
    msg.sender = emailvars.EMAIL
    mail.send(msg)
    return redirect(url_for("home"))


@app.route("/search", methods=["GET"])
def search():
    args = request.args
    ticker = args.get("searchedTicker")
    fmp_url = (f"https://financialmodelingprep.com/api/v3/search?query={ticker}&limit=10&exchange=NASDAQ&apikey={constants.FMP_API_KEY}")
    data = get_jsonparsed_data(fmp_url)
    return data

@app.route("/searchticker", methods=["GET"])
def searchticker():
    args = request.args
    ticker = args.get("searchedTicker")
    fmp_url = (f"https://financialmodelingprep.com/api/v3/search?query={ticker}&limit=10&exchange=NASDAQ&apikey={constants.FMP_API_KEY}")
    data = get_jsonparsed_data(fmp_url)
    return data

@app.route("/isTickerValidPage/<string:ticker>")
@cross_origin()
def isTickerValidPage(ticker:str) -> str:
    """Checks if ticker is valid."""
    if isTickerValid(ticker):
        return constants.TRUE
    else:
        return constants.FALSE
    

@app.route("/getInfo/<string:ticker>")
@cross_origin()
def getInfo(ticker:str) -> dict:
    """Prerequisite is that ticker must be valid. Use isTickerValid for this."""
    scrapingURL = getScrapingURL(ticker)
    data = requests.get(scrapingURL, headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")
    info_we_need = {
        "companyName" : scrapeCompanyName(soup),
        "currentValue" : {
            "value" : scrapePrice(soup),
            "change" : getPriceChangeStr(getFloat(scrapePrice(soup)), getFloat(scrapePrevClose(soup)), "Today")
        },
        "marketStatus" : scrapeMarketStatus(soup),
        "companyDesc" : scrapeCompanyDesc(soup),
        "companyLogoUrl" : scrapeCompanyLogo(scrapeCompanyWebsite(soup))
    }
    return info_we_need

@app.route("/getFinancials/<string:ticker>")
@cross_origin()
def getFinancials(ticker:str) -> dict:
    scrapingURL = getScrapingURL(ticker)
    data = requests.get(scrapingURL, headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")
    financials = {
        "incomeStatement": scrapeIncomeStatement(ticker),
        "balanceSheet":scrapeBalanceSheet(soup),
        "cashFlow":scrapeCashFlow(soup)
    }
    return financials

@app.route("/tickerNotFound/<string:InvalidTicker>", methods=["GET"])
def tickerNotFound(InvalidTicker):
    args = request.args
    return render_template("./TickerNotFound.html", InvalidTicker = InvalidTicker)

@app.route("/data/<string:companyTicker>")
def data(companyTicker:str):
    return render_template(
        "data.html", 
        info = getInfo(companyTicker),
        financials = getFinancials(companyTicker),
        newsList = getNews(companyTicker)
    )


if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0',port=8080)

    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()

