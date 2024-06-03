from app.services.main import *
from app.services.secret_info.secretConstants import secretConstants
from firebase_admin import credentials, auth, initialize_app
from flask_login import LoginManager, login_user
from flask import jsonify

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
 
@app.route("/payment")
def paypal_payment():
    if (session.get('user') != None):
        return render_template("./checkout.html", paypal_business_client_id=PAYPAL_BUSINESS_CLIENT_ID,
                            price=IB_TAX_APP_PRICE, currency=IB_TAX_APP_PRICE_CURRENCY)
    else:
        return redirect(url_for("login"))
 
@app.route("/payment/<order_id>/capture", methods=["POST"])
def capture_payment(order_id):  # Checks and confirms payment
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
 
