import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import toml

load_dotenv()

def init_firebase():
    if not firebase_admin._apps:
        tom_file = ".streamlit/secrets.toml" 
        with open(tom_file, "r") as f:
            secrets_dict = toml.load(f)
            cred_dict = secrets_dict['FIREBASE']
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)

def get_firestore_client():
    return firestore.client()






