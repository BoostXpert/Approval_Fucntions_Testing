from flask import Flask, render_template, redirect, url_for
from flask_caching import Cache
import pyrebase
import time
import uuid

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDzQSE0-7oI7WfSak1xsnPEXdFxZJt_Bnc",
    "authDomain": "your-auth-domain",
    "databaseURL": "https://boostxpert-default-rtdb.firebaseio.com/",
    "storageBucket": "your-storage-bucket",
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# In-memory store for tracking link usage
link_store = {}

@app.route('/pdf/<token>')
def pdf_view(token):
    if token in link_store:
        # Check if the link has already been used or expired
        link_info = link_store[token]
        if link_info['used'] or time.time() - link_info['created_at'] > 180:
            return "Link has expired or already used.", 403

        return render_template('pdf_view.html', token=token)

    return "Invalid link.", 404

@app.route('/approve/<token>')
def approve(token):
    return update_status(token, "approved")

@app.route('/reject/<token>')
def reject(token):
    return update_status(token, "rejected")

def update_status(token, status):
    if token in link_store:
        link_info = link_store[token]
        if link_info['used'] or time.time() - link_info['created_at'] > 180:
            return "Link has expired or already used.", 403

        # Update the status in Firebase
        db.child("approvals").child(token).update({"status": status})

        # Mark the link as used
        link_info['used'] = True
        return f"Status updated to {status}.", 200

    return "Invalid link.", 404

def generate_link():
    token = str(uuid.uuid4())
    link_store[token] = {"used": False, "created_at": time.time()}
    return f"/pdf/{token}"

# Example route to create a new PDF link
@app.route('/create_link')
def create_link():
    pdf_link = generate_link()
    # You would normally return this link in a more secure way
    return f"Generated link: {pdf_link}"

if __name__ == '__main__':
    app.run(debug=True)

