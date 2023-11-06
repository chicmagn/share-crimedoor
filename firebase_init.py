import google.cloud
from firebase_admin import credentials, firestore, storage, auth as fAuth
from google.cloud import firestore as fs
from __main__ import app
from auth import FirebaseAuth

auth = FirebaseAuth()
store = firestore.client()
bucket = storage.bucket()
firebase_app = None



def initializeFirebase():
  import firebase_admin
  from firebase_admin import credentials, firestore, storage, auth as fAuth
  from google.cloud import firestore as fs
  cred = credentials.Certificate("crime-central-firebase-adminsdk-3hd1r-a45c86bf9c.json")
  firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'crime-central.appspot.com'
  })
  return firebase_app
  