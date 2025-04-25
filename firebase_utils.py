import firebase_admin
from config import get_firestore_client 
from datetime import datetime
from google.cloud.firestore_v1 import SERVER_TIMESTAMP, Increment

db = get_firestore_client()

def save_submission(email, data):

    clean_email = email.replace(".", "_").replace("@", "_at_")
    user_doc_ref = db.collection("submissions").document(clean_email)
    user_doc_data = {
        'email': email, 
        'last_submission_at': SERVER_TIMESTAMP, 
    }
    user_doc_ref.set(user_doc_data, merge=True)
    user_doc_ref.collection("entries").add(data)


def has_valid_submission(email):
    clean_email = email.replace(".", "_").replace("@", "_at_")
    user_doc_ref = db.collection("submissions").document(clean_email)
    entries = user_doc_ref.collection("entries").limit(1).get()
    return len(entries) > 0


def get_all_submissions():
    all_entries = []
    users_stream = db.collection("submissions").stream()

    for user in users_stream:
        user_data = user.to_dict()
        submitter_email = user_data.get('email', user.id.replace("_at_", "@").replace("_", "."))
        entries_stream = db.collection("submissions").document(user.id).collection("entries").stream()
        for entry in entries_stream:
            entry_data = entry.to_dict()
            entry_data["submitted_by"] = submitter_email
            all_entries.append(entry_data)

    return all_entries

