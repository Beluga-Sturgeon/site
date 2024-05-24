import os
from dotenv import load_dotenv
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


class emailvars():
    EMAILREGEX            = '\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    EMAIL                 = os.getenv("EMAIL")
    SENDTOEMAIL           = os.getenv("SENDTOEMAIL")
    EMAILPASSWORD         = os.getenv("EMAILPASSWORD")
    PORT                  = 465  # For SSL