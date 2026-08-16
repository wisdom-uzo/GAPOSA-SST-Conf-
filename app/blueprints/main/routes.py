from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.firebase_service import firebase_service
from config import Config

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    speakers = firebase_service.get_speakers()
    subthemes = firebase_service.get_subthemes()
    announcements = firebase_service.get_announcements()
    schedule = firebase_service.get_schedule()
    active_tier = Config.get_current_local_fee_tier()

    # Group subthemes by track for display
    tracks = {}
    for st in subthemes:
        track_name = st.get('track', 'General Sciences')
        if track_name not in tracks:
            tracks[track_name] = []
        tracks[track_name].append(st)

    return render_template(
        'main/index.html',
        speakers=speakers,
        tracks=tracks,
        subthemes=subthemes,
        announcements=announcements,
        schedule=schedule,
        active_tier=active_tier,
        fees=Config.FEES
    )

@main_bp.route('/about')
def about():
    speakers = firebase_service.get_speakers()
    return render_template('main/about.html', speakers=speakers)

@main_bp.route('/speakers')
def speakers():
    all_speakers = firebase_service.get_speakers()
    return render_template('main/speakers.html', speakers=all_speakers)

@main_bp.route('/subthemes')
def subthemes():
    all_subthemes = firebase_service.get_subthemes()
    
    # Group subthemes by track
    tracks = {}
    for st in all_subthemes:
        track_name = st.get('track', 'General Sciences')
        if track_name not in tracks:
            tracks[track_name] = []
        tracks[track_name].append(st)

    return render_template('main/subthemes.html', tracks=tracks, subthemes=all_subthemes)

@main_bp.route('/call-for-papers')
def call_for_papers():
    subthemes = firebase_service.get_subthemes()
    return render_template('main/call_for_papers.html', subthemes=subthemes)

@main_bp.route('/schedule')
def schedule():
    schedule_data = firebase_service.get_schedule()
    return render_template('main/schedule.html', schedule=schedule_data)

@main_bp.route('/venue')
def venue():
    return render_template('main/venue.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not message:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('main.contact'))

        # Store contact query in firestore
        contact_doc = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'status': 'Unread'
        }
        firebase_service.set_document('contact_messages', f"msg_{firebase_service.generate_registration_id()}", contact_doc)

        flash('Thank you! Your message has been sent to the ICONFST’26 Secretariat. We will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))

    return render_template('main/contact.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('main/privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('main/terms.html')
