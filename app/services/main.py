import pathlib
import random
import smtplib
import string
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
import itertools
from collections import OrderedDict
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from dotenv import load_dotenv

from firebase import firebase
from firebase_admin import db  
from firebase_admin import credentials, auth, initialize_app

from app.services.secret_info import secretConstants
server = gunicorn.SERVER
load_dotenv()

class constants():
    FMP_API_KEY = "b0446da02c01a0943a01730dc2343e34"
    FIREBASE_API_KEY = "AIzaSyBnzb5SqamgMcTw99SY8oQebutm2S3bhuw"
    GOOGLE_FINANCE_URL = "https://www.google.com/finance/quote/"
    TRUE  = "true"
    FALSE = "false"


    API_URL          = "https://Foresightapi.herokuapp.com"
    REQ_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}

    FB_DB = 'https://beluga-sturgeon-financial-default-rtdb.firebaseio.com/'

    VALIDATE_TICKER_ENDING= "/isTickerValid/"
    GET_TICKER_INFO_ENDING= "/getInfo/"
    GET_NEWS_ENDING= "/getNews/"
    GET_FINANCIALS_ENDING= "/getFinancials/"
    STATS_FILE_PATH = r'app/services/gbm-drl-quant/res/stats'
    LOG_FILE_PATH = r'app/services/gbm-drl-quant/res/log'
    DIRECTORY_PATH = "app/services/gbm-drl-quant"

    # Define the command you want to execute
    QUANT_COMMAND = "./exec test {} ./models/checkpoint"


firebase = firebase.FirebaseApplication(constants.FB_DB, None)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1" # to allow Http traffic for local dev
initialize_app(secretConstants.FB_CRED)

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
    file_path = constants.STATS_FILE_PATH

    # Read the data from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Split the first line by commas
    data = lines[0].strip().split(',')

    # Create a DataFrame from the data
    df = pd.DataFrame([data], columns=["Ticker", "Annualized Return benchmark", "Stdev of Returns benchmark", "Shape Ratio benchmark", "Maximum Drawdown benchmark", "Annualized Return model", "Stdev of Returns model", "Sharpe Ratio model", "Maximum Drawdown model"])
    return df

def readlog(lastonly=False):
    log_file_path = constants.LOG_FILE_PATH

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


def update_daily(ticker:str, action, price, sd, maxdrawdown, sharpe, e_a_r):
    """Updates the daily log of model ouptuts. eg. If a user goes to ticker AAPL, the counter for times accessed increases by one, and the new actions generated by the model are put in.
    {
        "2023-11-22" : {
            'AAPL': {
            'times_accessed':0,
            'action': action,
            'price':price,
            'sd':sd,
            'maxdrawdown':maxdrawdown,
            'sharpe':sharpe,
            'e_a_r':e_a_r
            },

            'TSLA': {
                ...
            }
        }
    }
    
    
    """

    current_date = datetime.today()
    current_date_string = current_date.strftime('%Y-%m-%d')

    daily_log = firebase.get('/daily/' + current_date_string, None)
    
    # If the current date doesn't exist in the daily log, create it
    print(daily_log)
    if not daily_log:
        daily_log = {}
    
    # If the ticker doesn't exist for the current date, create it
    if ticker not in daily_log:
        daily_log[ticker] = {
            'times_accessed': 0,
            'action': action,
            'price': price,
            'sd': sd,
            'maxdrawdown': maxdrawdown,
            'sharpe': sharpe,
            'e_a_r': e_a_r
        }
    
    # Increment times_accessed for the ticker
    daily_log[ticker]['times_accessed'] += 1
    
    # Sort the dictionary by 'times_accessed' (we assume the sorting will be done locally)
    sorted_daily_log = sorted(daily_log.items(), key=lambda x: x[1]['times_accessed'], reverse=True)
    sorted_daily_log_dict = {ticker: data for ticker, data in sorted_daily_log}
    
    # Update the daily log in the database
    firebase.put('/daily', current_date_string, sorted_daily_log_dict)



def get_daily(Today=False):
    """Returns the daily dictionary of tickers accessed. If `today` is True, will only return those from the current day."""

    res = firebase.get('/daily', None)
    if Today:
        if datetime.today().strftime('%Y-%m-%d') in res.keys():
            return res[datetime.today().strftime('%Y-%m-%d')]
    return None






## -------------------------------------------------------FLASK ROUTING
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
    dailyactions = get_daily(Today=True)
    if dailyactions:
        hotactions = dict(itertools.islice(dailyactions.items(), min(5, len(dailyactions))))
        print(hotactions)
        return render_template("./index.html", hotactions=hotactions, session=session)
    else:
        print("NO DAILY ACTIONS")
        return render_template("./index.html", hotactions={}, session=session)

@app.route("/home")
def home2():
    return render_template("./index.html", session=session)

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

@app.route("/login")
def login():
    return render_template("./login.html")

@app.route("/login/create")
def create_account():
    return render_template("./createAccount.html")

@app.route("/account")
def account():
    return render_template("./account.html", session=session)

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

    #runs the model
    runtest(ticker=companyTicker)
    
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

    
    #STATS
    price = get_jsonparsed_data(f"https://financialmodelingprep.com/api/v3/quote-short/{companyTicker}?apikey={constants.FMP_API_KEY}")[0]["price"]
    e_a_r = round(float(stats.iloc[0]["Annualized Return model"]), 4)
    std = round(float(stats.iloc[0]["Stdev of Returns model"]),4)
    sharperatio=round(float(stats.iloc[0]["Sharpe Ratio model"]),4)
    maxdrawdown=round(float(stats.iloc[0]["Maximum Drawdown model"]), 4)


    update_daily(
        ticker=companyTicker,
        action=action,
        price=price,
        sd=std,
        maxdrawdown=maxdrawdown,
        sharpe=sharperatio,
        e_a_r=e_a_r
    )

    return render_template(
        "data.html", 
        info = {
            "companyName" : data["companyName"],
            "currentValue" : {
                "value" : price,
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
        e_a_r = str(e_a_r * 100) + "%",
        std = str(std* 100 ) + "%",
        sharperatio=sharperatio,
        maxdrawdown=maxdrawdown,
    )


app.secret_key = secretConstants.SECRET_KEY # make sure this matches with that's in client_secret.json

# Helper method to change firebase_auth user object to dict
def userToDict(user):
    return {
        'uid': user.uid,
        'email': user.email,
        'email_verified': user.email_verified,
        'name': user.email.split("@")[0],
    }
# Redirect user to google login
@app.route("/login/google")
def googleLogin():
    authorization_url, state = secretConstants.flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

# Process information from google login
@app.route("/google-callback")
def callback():
    secretConstants.flow.fetch_token(authorization_response=request.url)

    credentials = secretConstants.flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=secretConstants.GOOGLE_CLIENT_ID
    )

    email = id_info.get("email")

    user = None
    try: 
        user = auth.get_user_by_email(email)
    except:
        user = auth.create_user(email=email, password=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
    if user:
        session["user"] = userToDict(user)
        return redirect(url_for("home"))
# Clears session
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# Create account from account creation page & send verification email
@app.route("/login/create/submitted", methods=["GET", "POST"])
def createAccount():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        password_repeat = request.form['password_repeat']
        if password != password_repeat:
            return render_template("./createAccount.html", err="Passwords Don't Match!")
        try:
            user = auth.create_user(email=email, password=password)
            session["user"] = userToDict(user)
            # Generate email verification 
            link = auth.generate_email_verification_link(email, action_code_settings=None)
            msg = Message(
                subject="No Reply",
                recipients=[email],
                body=f"{link}"
            )
            msg.sender = emailvars.EMAIL
            mail.send(msg)
            return redirect(url_for("home"))
        except Exception as e:
            return render_template("./createAccount.html", err=str(e))
# Log user in based on email and password
@app.route("/login/submitted", methods=["GET", "POST"])
def signIn():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
        })
        # Create request to verify firebase user
        rest_api_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        r = requests.post(rest_api_url,
                        params={"key": constants.FIREBASE_API_KEY},
                        data=payload)
        reponse = r.json()
        print(reponse)
        if ('error' in reponse):
            return render_template("./login.html", err=reponse['error']['message'])
        else:
            user = auth.get_user_by_email(email)
            session["user"] = userToDict(user)
            return redirect(url_for("home"))
# Resends verification email when link on account page is clicked
@app.route("/send-verification", methods=["GET", "POST"])
def sendVerification():
    email = session["user"].get("email")
    # Generate email verification 
    link = auth.generate_email_verification_link(email, action_code_settings=None)
    msg = Message(
        subject="No Reply",
        recipients=[email],
        body=f"Please verify your email following this link: {link}"
    )
    msg.sender = emailvars.EMAIL
    mail.send(msg)
    session["user"] = userToDict(auth.get_user_by_email(email))
    return render_template("./account.html", session=session, message="Verification Sent!")
# Sends reset password email when clicked (TODO: add to login screen with seperate page for entering the email)
@app.route("/reset-password", methods=["GET", "POST"])
def resetPassword():
    email = session["user"].get("email")
    # Generate email verification 
    link = auth.generate_password_reset_link(email, action_code_settings=None)
    msg = Message(
        subject="No Reply",
        recipients=[email],
        body=f"Reset password here: {link}"
    )
    msg.sender = emailvars.EMAIL
    mail.send(msg)
    session["user"] = userToDict(auth.get_user_by_email(email))
    return render_template("./account.html", session=session, message="Check Your Email!")

if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0',port=8080)

    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()

