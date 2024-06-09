from app.services.main import *
from app.services.secret_info.secretConstants import secretConstants
from firebase_admin import credentials, auth, initialize_app
from flask_login import LoginManager, login_user
from flask import jsonify

import json
import os
 
# # # # PAYPAL SANDBOX
PAYPAL_BUSINESS_CLIENT_ID = os.getenv("PAYPAL_SANDBOX_BUSINESS_CLIENT_ID")
PAYPAL_BUSINESS_SECRET = os.getenv("PAYPAL_SANDBOX_BUSINESS_SECRET")
PAYPAL_API_URL = f"https://api-m.sandbox.paypal.com"
 
# # # # PAYPAL LIVE Details
# PAYPAL_BUSINESS_CLIENT_ID = os.getenv("PAYPAL_LIVE_BUSINESS_CLIENT_ID")
# PAYPAL_BUSINESS_SECRET = os.getenv("PAYPAL_LIVE_BUSINESS_SECRET")
# PAYPAL_API_URL = f"https://api-m.paypal.com"
 
# PAYPAL payment price
IB_TAX_APP_PRICE = float(150.00)
IB_TAX_APP_PRICE_CURRENCY = "PLN"
 
@app.route("/portfolio")
def portfolio():
    uid = session["user"].get('uid')
    models = firebase.get('/names', uid).get('models')
    portfolio = []
    for model in models:
        portfolio.append(getModelData(model))
    print(portfolio)
    return render_template("portfolio.html", session=session, data=portfolio)

@app.route("/build-model")
def build_model():
    return render_template("buildModel.html")

@app.route("/build-model/save", methods=['POST'])
def saveModel():
    tickers = request.get_json() 
    addModel(tickers)
    uid = session["user"].get('uid')
    tickerString = str(tickers)
    models = firebase.get('/names', uid).get('models')
    if models is None:
        models = [tickerString]
    else:
        if tickerString in models:
            print("User has model")
            return {"success": True}
        else:
            models.append(tickerString)
    firebase.put(f"/names/{uid}", 'models', models)
    return "success"

def addModel(tickers):
    modelsJson = firebase.get('','models')
    if modelsJson is None:
        firebase.put('/','models', """
[
    {"AMZN": 0.0, "TSLA": 1.0},
    {"AAPL": 0.0, "AMD": 1.0}
]
""")
    models = json.loads(modelsJson)
    for dic in models:
        keys = list(dic.keys())
        if tickers == keys:
            print("Free Money")
            return True
    newModel = {}
    for ticker in tickers:
        newModel[ticker] = 0.0
    models.append(newModel)
    firebase.put('/','models', json.dumps(models))
    return True

def getModelData(tickers):
    models = json.loads(firebase.get('','models'))
    for dic in models:
        keys = str(list(dic.keys()))
        if tickers == keys:
            print('found')
            return dic
    return {}

@app.route("/payment")
def paypallPayment():
    if (session.get('user') != None):
        return render_template("./checkout.html", paypal_business_client_id=PAYPAL_BUSINESS_CLIENT_ID,
                            price=IB_TAX_APP_PRICE, currency=IB_TAX_APP_PRICE_CURRENCY)
    else:
        return redirect(url_for("login"))
 
@app.route("/payment/<order_id>/capture", methods=["POST"])
def capturePayment(order_id):  # Checks and confirms payment
    captured_payment = paypal_capture_function(order_id)
    # print(captured_payment)
    if is_approved_payment(captured_payment):
        uid = session["user"].get('uid')
        data = firebase.get('/names', uid)
        premium_models = data.get('premium_models')
        if premium_models is None:
            firebase.put("/names", uid, {'premium_models': 1})
        else:
            num_models = int(premium_models)
            firebase.put("/names", uid, {'premium_models': num_models + 1})
        return redirect(url_for("account"))

@app.route("/test-payment")
def testPayment():
    uid = session["user"].get('uid')
    data = firebase.get('/names', uid)
    print(uid)
    print(firebase)
    premium_models = data.get('premium_models')
    if premium_models is None:
        data['premium_models'] = 1
    else:
        data['premium_models'] = int(premium_models) + 1
    firebase.put("/names", uid, data)
    return redirect(url_for("account"))
 
 
def paypal_capture_function(order_id):
    post_route = f"/v2/checkout/orders/{order_id}/capture"
    paypal_capture_url = PAYPAL_API_URL + post_route
    basic_auth = HTTPBasicAuth(PAYPAL_BUSINESS_CLIENT_ID, PAYPAL_BUSINESS_SECRET)
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url=paypal_capture_url, headers=headers, auth=basic_auth)
    response.raise_for_status()
    json_data = response.json()
    return json_data
 
def is_approved_payment(captured_payment):
    status = captured_payment.get("status")
    amount = captured_payment.get("purchase_units")[0].get("payments").get("captures")[0].get("amount").get("value")
    currency_code = captured_payment.get("purchase_units")[0].get("payments").get("captures")[0].get("amount").get(
        "currency_code")
    print(f"Payment happened. Details: {status}, {amount}, {currency_code}")
    if status == "COMPLETED":
        return True
    else:
        return False
 
