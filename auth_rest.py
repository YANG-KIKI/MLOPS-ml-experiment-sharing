import requests
import os
from dotenv import load_dotenv

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY") 

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()  
    else:
        return res.json().get("error", {}).get("message", "Unknown error")

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    res = requests.post(url, json=payload)
    if res.status_code == 200:
        return res.json()
    else:
        return res.json().get("error", {}).get("message", "Unknown error")