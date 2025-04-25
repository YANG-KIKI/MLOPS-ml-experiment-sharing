from config import init_firebase, get_firestore_client

# First initialize Firebase
init_firebase()

# Then get Firestore client
db = get_firestore_client()

# Manually test retrieving entries for the user 'roykaushnav@gmail_com'
doc_ref = db.collection("submissions").document("roykaushnav@gmail_com")
entries = doc_ref.collection("entries").stream()

if entries:
    print(f"[DEBUG] Entries for 'roykaushnav@gmail_com':")
    for entry in entries:
        print(entry.to_dict())
else:
    print("[DEBUG] No entries found for 'roykaushnav@gmail_com'.")



