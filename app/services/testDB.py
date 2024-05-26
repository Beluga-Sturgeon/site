from firebase_admin import credentials, auth, initialize_app


cred = credentials.Certificate('/Users/benjaminbeer/Downloads/beluga-sturgeon-financial-firebase-adminsdk-8lplv-9aa94af3ad.json')
initialize_app(cred)
auth_service = auth

auth_service = Flow.from_client_secrets_file()

email = "jane@gmail.com"
password = "doedoe"
try:
    user = auth_service.create_user(email=email, password=password)
    print("Successfully created user:", user.uid)
except ValueError as e:
    print("Error creating user:", e)

