import firebase_admin
from firebase_admin import auth
from config import init_firebase

init_firebase()

def create_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        return str(e)

def get_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        return user.uid
    except Exception as e:
        return str(e)

def verify_token(id_token):
    try:
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None
    
def check_session(id_token):
    return verify_token(id_token)