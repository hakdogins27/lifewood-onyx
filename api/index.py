# ====================================================================
# FINAL, DEPLOYMENT-READY api/index.py
# This version is modified to run on Vercel as a Serverless Function.
# It securely loads all credentials from environment variables.
# ====================================================================

import os
import json
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore, storage
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# --- Vercel Deployment Changes START ---

# Initialize Flask app at the top level for Vercel
app = Flask(__name__)
# Replace this:
# CORS(app, resources={r"/api/*": {"origins": "https://lifewood-onyx.vercel.app"}})

# With this:
CORS(app, resources={r"/api/*": {
    "origins": "https://lifewood-onyx.vercel.app",
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

@app.route('/api/some_endpoint')
def some_endpoint():
    return jsonify({"message": "Success"})
# Securely load Firebase credentials from Vercel environment variable
cred_json_str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if not cred_json_str:
    raise ValueError("The GOOGLE_APPLICATION_CREDENTIALS_JSON environment variable is not set.")

try:
    cred_json = json.loads(cred_json_str)
    cred = credentials.Certificate(cred_json)
    
    # Initialize Firebase Admin SDK
    # The try/except block prevents crashing if the app is already initialized in the serverless environment
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'lifewood-applicants-aa9bc.firebasestorage.app'
        })
except json.JSONDecodeError:
    raise ValueError("Failed to decode GOOGLE_APPLICATION_CREDENTIALS_JSON. Ensure it's a valid JSON string.")


# NEW CORRECT CODE
# NEW, CORRECT CODE
db = firestore.client()
bucket = storage.bucket()

# --- Vercel Deployment Changes END ---

@app.route('/api/<path:path>', methods=['OPTIONS'])
def catch_all_options(path):
    # This route's purpose is to respond to all OPTIONS preflight requests
    # The CORS extension will handle adding the correct headers.
    return jsonify(success=True), 200

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'message': 'Authentication Token is missing or malformed!'}), 401
        token = auth_header.split(' ')[1]
        try:
            # This will use the initialized Firebase app
            auth.verify_id_token(token)
        except Exception as e:
            return jsonify({'message': 'Invalid or expired token!', 'error': str(e)}), 403
        return f(*args, **kwargs)
    return decorated_function

def create_html_template(applicant_name, position, status, interview_start_time=None, interview_end_time=None):
    subject, header_text, body_html, button_link, button_text = "", "", "", "", ""
    closing_text = "Sincerely,"
    team_name = "The Lifewood Recruitment Team"

    if status == 'Received':
        subject = "Your Lifewood Application Has Been Received"
        header_text = "Application Received!"
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">This is to confirm that we have successfully received your application for the <strong>{position}</strong> role at Lifewood.</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">Our hiring team is now reviewing applications and will be in touch with the next steps as soon as possible. Thank you for your interest in joining our team!</p>"""
        button_link = "https://lifewood-ony.vercel.app/"
        button_text = "Visit Our Website"

    elif status == 'Under Review':
        subject = "Update on Your Lifewood Application"
        header_text = "Your Application is Under Review"
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">This is a quick confirmation that we have received your application for the <strong>{position}</strong> role at Lifewood, and it is now under review by our hiring team.</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">We appreciate your patience during this process and will be in touch with the next steps as soon as we have an update. Thank you for your interest in joining our team!</p>"""
        button_link = "https://lifewood-ony.vercel.app/"
        button_text = "Visit Our Website"

    elif status == 'Interview Scheduled':
        subject = "Invitation to Interview with Lifewood"
        header_text = "Invitation to Interview"
        schedule_details = "Our team will reach out to you shortly to coordinate a time."
        if interview_start_time and interview_end_time:
            try:
                start_dt = datetime.fromisoformat(interview_start_time)
                end_dt = datetime.fromisoformat(interview_end_time)
                date_str = start_dt.strftime('%A, %B %d, %Y')
                start_time_str = start_dt.strftime('%I:%M %p')
                end_time_str = end_dt.strftime('%I:%M %p')
                schedule_details = f"We have scheduled your interview on <strong>{date_str} from {start_time_str} to {end_time_str}</strong>."
            except (ValueError, TypeError):
                schedule_details = f"We have scheduled your interview from {interview_start_time} to {interview_end_time}."
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">Congratulations! We were very impressed with your application for the <strong>{position}</strong> role and would like to invite you for an interview.</p><p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">{schedule_details} Please confirm if this time works for you. If you need to reschedule, please reply to this email as soon as possible.</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">We look forward to speaking with you!</p>"""
        button_link = f"mailto:hr@lifewood.com?subject=Regarding Interview for {position}"
        button_text = "Confirm or Reschedule"
        closing_text = "Best regards,"
    
    elif status == 'Offer Extended':
        subject = "Exciting News: An Offer of Employment from Lifewood"
        header_text = "A Job Offer from Lifewood"
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">Following your recent interviews for the <strong>{position}</strong> position, we are absolutely delighted to formally extend to you an offer of employment with Lifewood!</p><p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">The entire team was thoroughly impressed with your skills and experience. Our Human Resources department will be sending a separate, detailed offer letter for your review, which will include information on compensation, benefits, and your proposed start date.</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">We are incredibly excited about the possibility of you joining us.</p>"""
        button_link = f"mailto:hr@lifewood.com?subject=Regarding My Offer for the {position} Position"
        button_text = "Contact HR to Discuss"
        closing_text = "We look forward to hearing from you,"

    elif status == 'Hired':
        subject = "An Exciting Update on Your Application with Lifewood"
        header_text = "Welcome to the Lifewood Team!"
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">We are absolutely thrilled to inform you that your application for the <strong>{position}</strong> position at Lifewood has been <strong>successful</strong>!</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">Our Human Resources department will be reaching out to you within the next two business days to provide the full offer details, discuss your potential start date, and guide you through our comprehensive onboarding process.</p>"""
        button_link = "mailto:hr@lifewood.com?subject=Regarding My Job Offer"
        button_text = "Contact HR"
        closing_text = "Best regards,"

    elif status == 'Rejected':
        subject = "An Update on Your Application with Lifewood"
        header_text = "Thank You For Your Interest"
        body_html = f"""<p style="margin:0 0 25px 0;font-size:16px;line-height:1.7;color:#333333;">Thank you again for your interest in the <strong>{position}</strong> position and for taking the time to interview with our team at Lifewood.</p><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">The selection process was exceptionally competitive, and after careful consideration, we have decided to move forward with another applicant. We will keep your application on file for future opportunities and wish you the very best in your job search.</p>"""
        button_link = "https://lifewood-ony.vercel.app/services.html"
        button_text = "Explore Other Roles"

    html_content = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&display=swap');body{{font-family:'Manrope',Arial,sans-serif;}}</style></head><body style="margin:0;padding:0;background-color:#f5eedb;"><table border="0" cellpadding="0" cellspacing="0" width="100%"><tr><td style="padding:40px 20px;"><table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="border-collapse:collapse;background-color:#ffffff;border-radius:8px;box-shadow:0 4px 15px rgba(0,0,0,0.1);"><td align="center" style="padding: 30px 20px 20px 20px;"><a href="https://lifewood-ony.vercel.app/" target="_blank" style="text-decoration: none; display: inline-block;"><svg width="24" height="32" viewBox="0 0 24 42" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; margin-right: 8px; height: 32px; width: auto;"><path d="M12 0L23.5962 10.5V31.5L12 42L0.403847 31.5V10.5L12 0Z" fill="#FFB347"/></svg><span style="font-family: 'Manrope', Arial, sans-serif; font-size: 30px; font-weight: 800; letter-spacing: -0.5px; color: #133020; vertical-align: middle;">lifewood</span></a></td></tr><tr><td style="padding:20px 40px;"><h1 style="font-size:28px;font-weight:700;color:#046241;margin:0 0 25px 0;text-align:center;">{header_text}</h1><p style="margin:0 0 15px 0;font-size:16px;line-height:1.7;color:#333333;">Dear {applicant_name},</p>{body_html}</td></tr><tr><td align="center" style="padding:10px 40px 30px 40px;"><a href="{button_link}" target="_blank" style="display:inline-block;padding:14px 35px;background-color:#FFB347;color:#133020;text-decoration:none;font-weight:700;border-radius:5px;font-size:16px;">{button_text}</a></td></tr><tr><td style="padding:0px 40px 40px 40px;"><p style="margin:0;font-size:16px;line-height:1.7;color:#333333;">{closing_text},</p><p style="margin:5px 0 0 0;font-size:16px;line-height:1.7;color:#333333;">{team_name}</p></td></tr></table></td></tr></table></body></html>"""
    return subject, html_content

def send_email(recipient_email, applicant_name, position, status, interview_start_time=None, interview_end_time=None):
    # Load email credentials from Vercel environment variables
    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("EMAIL_SENDER")
    
    if not api_key or not sender_email:
        print("Email credentials (BREVO_API_KEY or EMAIL_SENDER) are not set in environment variables.")
        return False, "Server is not configured for sending emails."

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    subject, html_content = create_html_template(applicant_name, position, status, interview_start_time, interview_end_time)
    
    sender = {"name": "The Lifewood Team", "email": sender_email}
    to = [{"email": recipient_email, "name": applicant_name}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, sender=sender, subject=subject, html_content=html_content)
    
    try:
        api_instance.send_transac_email(send_smtp_email)
        return True, f"Status updated to '{status}' and email sent."
    except ApiException as e:
        print(f"Brevo API Error: {e}")
        return False, f"Status updated, but email failed. Brevo error: {e.reason}"

# --- PUBLIC ROUTES ---

@app.route('/api/apply', methods=['POST'])
def apply():
    try:
        data = request.form.to_dict()
        data['submittedAt'] = firestore.SERVER_TIMESTAMP
        data['viewed'] = False  # Mark as unread for notification feature
        required_fields = ['firstName', 'lastName', 'email', 'position', 'age', 'degree']
        if any(field not in data or not data[field] for field in required_fields):
            return jsonify({"message": "Missing required fields."}), 400
        
        if 'resumeFile' in request.files:
            file = request.files['resumeFile']
            if file.filename != '':
                blob = bucket.blob(f"resumes/{data['lastName']}_{data['firstName']}_{datetime.now().timestamp()}_{file.filename}")
                blob.upload_from_file(file)
                blob.make_public()
                data['uploadedResumeUrl'] = blob.public_url

        db.collection('applications').add(data)
        send_email(data.get('email'), data.get('firstName'), data.get('position'), 'Received')
        return jsonify({"message": "Application submitted successfully."}), 201
    except Exception as e:
        print(f"Error in /api/apply: {e}")
        return jsonify({"message": "Could not submit application due to a server error."}), 500

@app.route('/api/positions', methods=['GET'])
def get_public_positions():
    try:
        positions_ref = db.collection('positions').order_by('title').stream()
        return jsonify([dict(doc.to_dict(), id=doc.id) for doc in positions_ref]), 200
    except Exception as e:
        return jsonify({"message": "Could not retrieve positions."}), 500

@app.route('/api/inquiries', methods=['POST'])
def submit_inquiry():
    try:
        data = request.get_json()
        if not all(k in data for k in ('name', 'email', 'message')):
            return jsonify({'message': 'Missing required fields.'}), 400
        
        data['submittedAt'] = firestore.SERVER_TIMESTAMP
        data['viewed'] = False # Mark as unread for notification feature
        db.collection('inquiries').add(data)
        return jsonify({'message': 'Inquiry submitted successfully!'}), 201
    except Exception as e:
        return jsonify({'message': 'Could not submit inquiry.'}), 500

# --- ADMIN ROUTES ---

@app.route('/api/analytics/application-trends', methods=['GET'])
@token_required
def get_application_trends():
    try:
        today = datetime.utcnow().date()
        seven_days_ago = today - timedelta(days=6)
        apps_ref = db.collection('applications').where('submittedAt', '>=', datetime.combine(seven_days_ago, datetime.min.time())).stream()
        
        labels = [(seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        status_keys = ['Hired', 'Rejected', 'Interview Scheduled', 'Other']
        counts_by_day = {day: {status: 0 for status in status_keys} for day in labels}

        for app in apps_ref:
            app_data = app.to_dict()
            if app_data.get('submittedAt'):
                submitted_date_str = app_data['submittedAt'].date().strftime('%Y-%m-%d')
                if submitted_date_str in counts_by_day:
                    status = app_data.get('status', 'Received')
                    status_key = status if status in status_keys else 'Other'
                    counts_by_day[submitted_date_str][status_key] += 1
        
        datasets = [{"label": status, "data": [counts_by_day[day][status] for day in labels]} for status in status_keys]
        return jsonify({'labels': labels, 'datasets': datasets}), 200
    except Exception as e:
        return jsonify({"message": "Could not retrieve application trends."}), 500

@app.route('/api/application/<app_id>', methods=['GET'])
@token_required
def get_application(app_id):
    try:
        doc = db.collection('applications').document(app_id).get()
        if not doc.exists: return jsonify({"message": "Application not found."}), 404
        return jsonify(dict(doc.to_dict(), id=doc.id)), 200
    except Exception as e: return jsonify({"message": f"An error occurred: {e}"}), 500

@app.route('/api/application/<app_id>', methods=['PUT'])
@token_required
def update_application(app_id):
    try:
        data = request.get_json()
        valid_fields = ['status', 'notes', 'rating', 'interviewStartTime', 'interviewEndTime']
        data_to_update = {k: v for k, v in data.items() if k in valid_fields}

        if not data_to_update: return jsonify({"message": "No valid fields provided."}), 400
        
        app_ref = db.collection('applications').document(app_id)
        app_ref.update(data_to_update)

        if 'status' in data_to_update:
            new_status = data_to_update['status']
            app_data = app_ref.get().to_dict()
            if new_status in ['Hired', 'Rejected', 'Offer Extended', 'Interview Scheduled', 'Under Review']:
                success, message = send_email(
                    app_data.get('email'), app_data.get('firstName'), app_data.get('position'), 
                    new_status, data.get('interviewStartTime'), data.get('interviewEndTime')
                )
                return jsonify({"message": message}), 200 if success else 500
            return jsonify({"message": f"Status updated to '{new_status}'."}), 200
        
        return jsonify({"message": "Application updated successfully."}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred during update: {e}"}), 500

@app.route('/api/application/<app_id>', methods=['DELETE'])
@token_required
def delete_application(app_id):
    try:
        db.collection('applications').document(app_id).delete()
        return jsonify({"message": "Application deleted."}), 200
    except Exception as e: return jsonify({"message": f"Could not delete application: {e}"}), 500

@app.route('/api/applications', methods=['GET'])
@token_required
def get_applications():
    try:
        apps_ref = db.collection('applications').order_by('submittedAt', direction=firestore.Query.DESCENDING).stream()
        return jsonify([dict(doc.to_dict(), id=doc.id) for doc in apps_ref]), 200
    except Exception as e: return jsonify({"message": f"Could not retrieve applications: {e}"}), 500

@app.route('/api/applications/mark-as-read', methods=['POST'])
@token_required
def mark_applications_as_read():
    try:
        apps_ref = db.collection('applications').where('viewed', '==', False).stream()
        for app in apps_ref:
            app.reference.update({'viewed': True})
        return jsonify({"message": "All new applications marked as read."}), 200
    except Exception as e:
        return jsonify({"message": "Could not mark applications as read."}), 500

@app.route('/api/positions', methods=['POST'])
@token_required
def add_position():
    try:
        data = request.get_json()
        db.collection('positions').add(data)
        return jsonify({"message": "Position added."}), 201
    except Exception as e: return jsonify({"message": "Could not add position."}), 500

@app.route('/api/positions/<position_id>', methods=['DELETE'])
@token_required
def delete_position(position_id):
    try:
        db.collection('positions').document(position_id).delete()
        return jsonify({"message": "Position deleted."}), 200
    except Exception as e: return jsonify({"message": "Could not delete position."}), 500
    
@app.route('/api/inquiries', methods=['GET'])
@token_required
def get_inquiries():
    try:
        inquiries_ref = db.collection('inquiries').order_by('submittedAt', direction=firestore.Query.DESCENDING).stream()
        return jsonify([dict(doc.to_dict(), id=doc.id) for doc in inquiries_ref]), 200
    except Exception as e: return jsonify({"message": f"Could not retrieve inquiries: {e}"}), 500

@app.route('/api/inquiries/mark-as-read', methods=['POST'])
@token_required
def mark_inquiries_as_read():
    try:
        inquiries_ref = db.collection('inquiries').where('viewed', '==', False).stream()
        for inquiry in inquiries_ref:
            inquiry.reference.update({'viewed': True})
        return jsonify({"message": "All new inquiries marked as read."}), 200
    except Exception as e:
        return jsonify({"message": "Could not mark inquiries as read."}), 500

@app.route('/api/inquiries/<inquiry_id>', methods=['DELETE'])
@token_required
def delete_inquiry(inquiry_id):
    try:
        print(f"Attempting to delete inquiry with ID: {inquiry_id}")
        db.collection('inquiries').document(inquiry_id).delete()
        return jsonify({"message": "Inquiry deleted."}), 200
    except Exception as e:
        print(f"Error deleting inquiry: {e}")
        return jsonify({"message": f"Could not delete inquiry: {e}"}), 500

# The if __name__ == '__main__': block is removed because Vercel handles the server execution.