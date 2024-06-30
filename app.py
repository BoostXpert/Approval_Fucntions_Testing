from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, db
import time
import json
import os

app = Flask(__name__)

# Firebase configuration
firebase_config = {
  "type": "service_account",
  "project_id": "boostxpert",
  "private_key_id": "a41c18d97e8f8d110232a25c08b6f84df6bb6b41",
  "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
  "client_email": "firebase-adminsdk-qfovh@boostxpert.iam.gserviceaccount.com",
  "client_id": "111744002932529453456",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-qfovh%40boostxpert.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://boostxpert-default-rtdb.firebaseio.com/'
})

approve_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Approval</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 800px;
            padding: 20px;
            text-align: center.
        }
        h1 {
            margin-bottom: 20px.
        }
        embed {
            width: 100%;
            height: 500px;
            border: none;
            margin-bottom: 20px.
        }
        .buttons {
            display: flex;
            justify-content: space-between.
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s.
        }
        .approve {
            background-color: #4CAF50;
            color: white.
        }
        .approve:hover {
            background-color: #45a049.
        }
        .reject {
            background-color: #f44336;
            color: white.
        }
        .reject:hover {
            background-color: #e53935.
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Job Details for {{ job_name }}</h1>
        <embed src="{{ pdf_url }}" type="application/pdf" />
        <div class="buttons">
            <form action="/process_approval" method="post" style="display: inline;">
                <input type="hidden" name="unique_id" value="{{ unique_id }}">
                <button type="submit" name="action" value="approve" class="approve">Approve</button>
            </form>
            <form action="/process_approval" method="post" style="display: inline;">
                <input type="hidden" name="unique_id" value="{{ unique_id }}">
                <button type="submit" name="action" value="reject" class="reject">Reject</button>
            </form>
        </div>
    </div>
</body>
</html>
'''

@app.route('/approve')
def approve():
    unique_id = request.args.get('unique_id')
    ref = db.reference(f'firebase-testing1/{unique_id}')
    job_data = ref.get()

    if not job_data:
        return "Invalid or expired link."

    if job_data.get('is_used', False):
        return "This link has already been used."

    current_timestamp = int(time.time() * 1000)
    link_timestamp = job_data.get('timestamp', 0)
    expiration_time = 3 * 60 * 1000

    if current_timestamp - link_timestamp > expiration_time:
        return "This link has expired."

    ref.update({'is_used': True})

    return render_template_string(approve_html, job_name=job_data['job_name'], pdf_url='https://drive.google.com/uc?export=download&id=0B6fdYjTkgBWWc3RhcnRlcl9maWxl', unique_id=unique_id)

@app.route('/process_approval', methods=['POST'])
def process_approval():
    unique_id = request.form['unique_id']
    action = request.form['action']
    update_document_status(unique_id, action)
    return "Thank you! Your response has been recorded."

def update_document_status(unique_id, action):
    ref = db.reference(f'firebase-testing1/{unique_id}')
    if action == 'approve':
        ref.update({'approval_status': True})
    elif action == 'reject':
        ref.update({'approval_status': False})
    ref.update({'is_used': True})

if __name__ == '__main__':
    app.run(debug=True)
