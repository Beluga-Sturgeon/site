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
from colorthief import ColorThief
import urllib

from firebase import firebase
from firebase_admin import db  
from celery import Celery
from celery.schedules import crontab


#FILE IMPORTS
from app.services.cnst import constants, emailvars
from app.services.scraper import *
from app.services.helperfunctions import *
from app.services.fmpRequester import *
from app.services.readlog import *


server = gunicorn.SERVER

firebase = firebase.FirebaseApplication(constants.FB_DB, None)

def createApp():
    app = Flask(
    __name__,
    template_folder=r"templates",
    static_folder=r"static"
    )
    return app

app = createApp()

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = emailvars.EMAIL,
    MAIL_PASSWORD = emailvars.EMAILPASSWORD,
    CELERY_BROKER_URL = 'redis://localhost:6379/0',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
))




mail = Mail(app)


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
    print(sorted_daily_log_dict)
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
        return render_template("./index.html", hotactions=hotactions)
    else:
        print("NO DAILY ACTIONS")
        return render_template("./index.html", hotactions={})

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

@app.route("/login")
def login():
    return render_template("./login.html")

@app.route("/login/create")
def create_account():
    return render_template("./createAccount.html")

@app.route("/account")
def account():
    return render_template("./account.html", session=session)

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



@app.route('/search', methods=["GET"])
@app.route("/searchticker", methods=["GET"])
def searchticker():
    args = request.args
    ticker = args.get("searchedTicker")
    return search(ticker)

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

    company_profile = get_profile(ticker)


    info_we_need = {
        "companyName" : company_profile["companyName"],
        "currentValue" : {
            "value" : get_value(ticker),
            "change" : getPriceChangeStr(ticker)
        },
        "marketStatus" : scrapeMarketStatus(soup),
        "companyDesc" : company_profile["description"],
        "companyLogoUrl" : company_profile["image"],
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
    
    log = readlog(companyTicker)
    if log.iloc[0]["action"] == 0:
        action = "SHORT"
    elif log.iloc[0]["action"] == 1:
        action = "HOLD"
    else:
        action = "LONG"
    stats = readstats(companyTicker)
    scrapingURL = getScrapingURL(companyTicker)
    data = requests.get(scrapingURL, headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(data, "lxml")

    data = get_profile(companyTicker)

    #STATS
    price = get_value(companyTicker)
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

    soup_data = requests.get(getScrapingURL(companyTicker), headers=constants.REQ_HEADER).text
    soup = BeautifulSoup(soup_data, "lxml")
    try:
        print(data["image"])
        urllib.request.urlretrieve(data["image"], "tmp.png")
        color_thief = ColorThief("tmp.png")
        dominant_color = color_thief.get_color(quality=1)
        os.remove("tmp.png")
    except:
        dominant_color = "(00,00,00)"

    print("dominantColor" + str(dominant_color))
    print("NEWS", getNews(companyTicker))
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
            "companyLogoUrl" : data["image"],
            "dominantColor": dominant_color
        },
        newsList = getNews(companyTicker),
        action= action,
        e_a_r = str(e_a_r * 100) + "%",
        std = str(std* 100 ) + "%",
        sharperatio=sharperatio,
        maxdrawdown=maxdrawdown,
        session=session
    )

"""
This is the loading page
It uses the loading.html in templates
It seems to be giving an error :/
"""
# @app.route("/loading", methods=["POST"])
# def loading():
#     if request.method == "POST":
#         return render_template("loading.html")
    

from app.services.accounts import *
from app.services.premium import *

if __name__ == '__main__':
    def run():
        app.run(host='0.0.0.0',port=8080)

    def keep_alive():
        t = Thread(target=run)
        t.start()
    keep_alive()

