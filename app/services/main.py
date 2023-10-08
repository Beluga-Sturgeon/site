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
import pandas as pd
import subprocess
from datetime import datetime, timedelta
server = gunicorn.SERVER


class constants():
    FMP_API_KEY = "b0446da02c01a0943a01730dc2343e34"
    GOOGLE_FINANCE_URL = "https://www.google.com/finance/quote/"
    TRUE  = "true"
    FALSE = "false"


    API_URL          = "https://Foresightapi.herokuapp.com"
    REQ_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}



    VALIDATE_TICKER_ENDING= "/isTickerValid/"
    GET_TICKER_INFO_ENDING= "/getInfo/"
    GET_NEWS_ENDING= "/getNews/"
    GET_FINANCIALS_ENDING= "/getFinancials/"
    STATS_FILE_PATH = r'app\services\gbm-drl-quant\res\stats'
    LOG_FILE_PATH = r'app\services\gbm-drl-quant\res\log'
    DIRECTORY_PATH = "app/services/gbm-drl-quant"

    # Define the command you want to execute
    QUANT_COMMAND = ".\\exec test {} .\\models\\checkpoint"


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


def scrapeNews(ticker:str) -> dict:
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
    
    fmp_url = f"https://financialmodelingprep.com/api/v3/stock_news?tickers={ticker}&page=0&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    count = 0
    articles = {}
    articlelist = []
    for i in data:
        if count > 4:
            break
        articlelist.append(
            {
                'date': i["publishedDate"],
                'title':i["title"],
                'publisher':i["site"],
                'link':i["url"]
            }
        )
        count += 1
    
    articles["articles"] = articlelist
    return articles



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

    try:
        latest, older = data[-1], data[-2]
    except:
        latest, older = data[-1], data[-1]
        
    for key in latest.keys():
        new, old = latest[key], older[key]
        try:
            change = (new - old) / old * 100
            if change > 0:
                incomeStatement[key] = {"value":human_format(latest[key]), "change":"+%.2f%%"%(change)}
            else:
                incomeStatement[key] = {"value":human_format(latest[key]), "change":"%.2f%%"%(change)}
        except:
            pass
    return incomeStatement



def scrapeBalanceSheet(ticker:str) ->dict:
    """returns values in {value:xx, change:xx}"""
    balanceSheet = {}
    fmp_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?period=quarter&limit=120&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    try:
        latest, older = data[-1], data[-2]
    except:
        latest, older = data[-1], data[-1]

    for key in latest.keys():
        new, old = latest[key], older[key]
        try:
            change = (new - old) / old * 100 
            if change > 0:
                balanceSheet[key] = {"value":human_format(latest[key]), "change":"+%.2f%%"%(change)}
            else:
                balanceSheet[key] = {"value":human_format(latest[key]), "change":"%.2f%%"%(change)}
        except:
            pass
    return balanceSheet

def scrapeCashFlow(ticker:str) ->dict:
    """returns values in {value:xx, change:xx}"""
    cashflow = {}
    fmp_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?period=quarter&limit=120&apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)

    try:
        latest, older = data[-1], data[-2]
    except:
        latest, older = data[-1], data[-1]

    for key in latest.keys():
        new, old = latest[key], older[key]
        try:
            change = (new - old) / old * 100
            if change > 0:
                cashflow[key] = {"value":human_format(latest[key]), "change":"+%.2f%%"%(change)}
            else:
                cashflow[key] = {"value":human_format(latest[key]), "change":"%.2f%%"%(change)}
        except:
            pass
    return cashflow



def scrapeCompanyLogo(companyWebsite:str):
    "Returns link to company logo given company website url"
    return constants.LOGO_CLEARBIT_URL + companyWebsite


def getPriceChangeStr(ticker:str) ->str:
    """Gves string that shows difference, and percent difference along wth a label.. Example:\n
    >>> getPriceChangeStr(12, 10, 'difference'))\n
    >>> '+2.00 (20.0%) difference'"""
    fmp_url = (f"https://financialmodelingprep.com/api/v3/stock-price-change/{ticker}?apikey={constants.FMP_API_KEY}")
    data = get_jsonparsed_data(fmp_url)
    daychange = data[0]["1D"]

    return str(daychange) + "%"


def readstats():
    file_path = r'app\services\gbm-drl-quant\res\stats'

    # Read the data from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Split the first line by commas
    data = lines[0].strip().split(',')

    # Create a DataFrame from the data
    df = pd.DataFrame([data], columns=["Ticker", "Annualized Return benchmark", "Stdev of Returns benchmark", "Shape Ratio benchmark", "Maximum Drawdown benchmark", "Annualized Return model", "Stdev of Returns model", "Sharpe Ratio model", "Maximum Drawdown model"])
    return df

def readlog(lastonly=False):
    log_file_path = r'app\services\gbm-drl-quant\res\log'

    # Read the last line of the log file when lastonly is True
    if lastonly:
        with open(log_file_path, 'r') as file:
            lines = file.readlines()
            columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
            data = [lines[-1].split(',')]
            data[0][-1] = data[0][-1].rstrip()  # Remove newline character from the last element
            df = pd.DataFrame(data, columns=columns)
            return df

    # Read the entire log file when lastonly is False
    with open(log_file_path, 'r') as file:
        lines = file.readlines()
        columns = ["X", "SPY", "IEF", "GSG", "EUR=X", "action", "benchmark", "model"]
        data = [l.strip().split(',') for l in lines[1:]]  # Skip the first line if not lastonly
        df = pd.DataFrame(data, columns=columns)
        df['model'] = df['model'].str.rstrip()  # Remove newline characters from the 'model' column
        return df

def runtest(ticker:str):
    #subprocess.run(f'ls', shell=True, check=True)
    # Define the directory you want to change to

    try:
        # Change the current directory to the specified path
        subprocess.run(f'cd {constants.DIRECTORY_PATH} && {constants.QUANT_COMMAND.format(ticker)}', shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")








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

    fmp_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)
    data = data[0]


    info_we_need = {
        "companyName" : data["companyName"],
        "currentValue" : {
            "value" : get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/quote-short/{ticker}?apikey={constants.FMP_API_KEY}")[0]["price"],
            "change" : getPriceChangeStr(ticker)
        },
        "marketStatus" : scrapeMarketStatus(soup),
        "companyDesc" : data["description"],
        "companyLogoUrl" : data["image"]
    }
    return info_we_need




@app.route("/getFinancials/<string:ticker>")
@cross_origin()
def getFinancials(ticker:str) -> dict:
    financials = {
        "incomeStatement": scrapeIncomeStatement(ticker),
        "balanceSheet":scrapeBalanceSheet(ticker),
        "cashFlow":scrapeCashFlow(ticker)
    }
    return financials

@app.route("/tickerNotFound/<string:InvalidTicker>", methods=["GET"])
def tickerNotFound(InvalidTicker):
    args = request.args
    return render_template("./TickerNotFound.html", InvalidTicker = InvalidTicker)

@app.route("/getChangestr/<string:companyTicker>")
def getChangestr(companyTicker:str):
    scrapingURL = getScrapingURL(companyTicker)
    data = requests.get(scrapingURL, headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")
    return scrapeMarketStatus(soup)


@app.route("/getLog/<string:companyTicker>")
def getLog(companyTicker:str):
    log = readlog()  # Assuming readlog() returns a DataFrame

    # Calculate the current date
    current_date = datetime.now()

    log = log.iloc[::-1]
    # Calculate the date for each row, going back a day for each row
    log['Date'] = [current_date - timedelta(days=i) for i in range(len(log))]
    log['Date'] = log['Date'].dt.date
    # Assuming you have a DataFrame named 'log' with 'Date' and other columns

    print(log)

    # Convert the DataFrame to a list of dictionaries
    log_list_of_dicts = log.to_dict(orient='records')

    return log_list_of_dicts

@app.route("/getStats/<string:companyTicker>")
def getStats(companyTicker:str):
    return readstats().to_csv()

@app.route("/data/<string:companyTicker>")
def data(companyTicker:str):
    # runtest(ticker=companyTicker)
    log = readlog(lastonly=True)
    if log.iloc[0]["action"] == 0:
        action = "SHORT"
    elif log.iloc[0]["action"] == 1:
        action = "HOLD"
    else:
        action = "LONG"
    stats = readstats()
    scrapingURL = getScrapingURL(companyTicker)
    data = requests.get(scrapingURL, headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")

    fmp_url = f"https://financialmodelingprep.com/api/v3/profile/{companyTicker}?apikey={constants.FMP_API_KEY}"
    data = get_jsonparsed_data(fmp_url)
    data = data[0]

    return render_template(
        "data.html", 
        info = {
            "companyName" : data["companyName"],
            "currentValue" : {
                "value" : get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/quote-short/{companyTicker}?apikey={constants.FMP_API_KEY}")[0]["price"],
                "change" : getPriceChangeStr(companyTicker)
            },
            "marketStatus" : scrapeMarketStatus(soup),
            "companyDesc" : data["description"],
            "companyLogoUrl" : data["image"]
        },
        financials = {
            "incomeStatement": scrapeIncomeStatement(companyTicker),
            "balanceSheet":scrapeBalanceSheet(companyTicker),
            "cashFlow":scrapeCashFlow(companyTicker)
        },
        newsList = scrapeNews(companyTicker),
        action= action,
        e_a_r = round(float(stats.iloc[0]["Annualized Return model"]), 4),
        std = round(float(stats.iloc[0]["Stdev of Returns model"]),4),
        sharperatio=round(float(stats.iloc[0]["Sharpe Ratio model"]),4),
        maxdrawdown=round(float(stats.iloc[0]["Maximum Drawdown model"]), 4),
    )




if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0',port=8080)

    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()

