from app.services.main import *
from app.services.secret_info.secretConstants import secretConstants
from firebase_admin import credentials, auth, initialize_app
from pip._vendor import cachecontrol
from collections import OrderedDict
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol

import random
import string
import google.auth.transport.requests
import os


app.secret_key = secretConstants.SECRET_KEY # make sure this matches with that's in client_secret.json
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
initialize_app(secretConstants.FB_CRED)


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