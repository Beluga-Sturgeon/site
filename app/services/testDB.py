# Import database module.
from firebase import firebase


firebase = firebase.FirebaseApplication('https://beluga-sturgeon-financial-default-rtdb.firebaseio.com/', None)





result = firebase.get('/', None)
print(result)