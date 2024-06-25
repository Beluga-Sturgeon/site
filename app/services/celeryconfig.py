from celery import Celery
import requests
from app.services.main import *
import subprocess
import app.services.cnst as constants
from firebase_admin import credentials, auth, initialize_app
from flask_login import LoginManager, login_user


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@celery.task
def daily_update_gbm():
    response = requests.get(f'https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={constants.FMP_API_KEY}')
    if response.status_code == 200:
        sp500_data = response.json()
        sp500_tickers = " ".join([company['symbol'] for company in sp500_data])
    else:
        print("Failed to retrieve S&P 500 tickers.")
        return
    subprocess.run(f'cd {constants.DIRECTORY_PATH} && {constants.QUANT_COMMAND.format(sp500_tickers)}', shell=True, check=True)


def daily_update_portfolio():
    response = requests.get(f'https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={constants.FMP_API_KEY}')
    if response.status_code == 200:
        sp500_data = response.json()
        sp500_tickers = " ".join([company['symbol'] for company in sp500_data])
    else:
        print("Failed to retrieve S&P 500 tickers.")
        return
    subprocess.run(f'cd {constants.PORTFOLIO_DIRECTORY} && {constants.PORTFOLIO_COMMAND.format('build', sp500_tickers)}', shell=True, check=True)

def update_database_portfolios():
    modelsJson = firebase.get('','models')
    models = json.loads(modelsJson)
    for dic in models:
        tickers = " ".join(dic.keys())
        subprocess.run(f"cd {constants.PORTFOLIO_DIRECTORY} && '{constants.PORTFOLIO_COMMAND.format({tickers})}'", shell=True, check=True)
        action = read_portfolio(True)
        for item in tickers:
            dic[item] = action[item].iloc[-1]
    firebase.put('/','models', json.dumps(models))    

celery.conf.beat_schedule = {
    'daily-get-daily': {
        'task': 'tasks.get_daily',
        'schedule': crontab(hour=9, minute=0),
    },
}    