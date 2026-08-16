import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, make_response, g, jsonify
from app.blueprints.auth.routes import admin_required
from app.firebase_service import firebase_service
from config import Config

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    analytics = firebase_service.get_analytics()
    recent_registrations = firebase_service.get_all_registrations()[:5]
    recent_submissions = firebase_service.get_all_submissions()[:5]
    
    return render_template(
        'admin/dashboard.html',
        analytics=analytics,
        recent_registrations=recent_registrations,
        recent_submissions=recent_submissions,
        config=Config
    )

# -------------------------------------------------------------
# ADMINISTRATORS & STAFF MANAGEMENT
# -------------------------------------------------------------
@admin_bp.route('/administrators')
@admin_required
def administrators():
    all_admins = firebase_service.get_all_admins()
    return render_template('admin/administrators.html', administrators=all_admins)

@admin_bp.route('/administrators/add', methods=['POST'])
@admin_required
def add_administrator():
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '').strip()
    title = request.form.get('title', 'Administrator').strip()
    phone = request.form.get('phone', '').strip()
    affiliation = request.form.get('affiliation', 'The Gateway (ICT) Polytechnic, Saapade').strip()

    if not full_name or not email or not password:
        flash('Full Name, Email, and Password are required to create an administrator account.', 'error')
        return redirect(url_for('admin.administrators'))

    existing = firebase_service.get_user_by_email(email)
    if existing:
        flash(f"An account with email '{email}' already exists in Firestore.", 'error')
        return redirect(url_for('admin.administrators'))

    try:
        firebase_service.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role='admin',
            title=title,
            affiliation=affiliation,
            phone=phone
        )
        flash(f"Administrator '{full_name}' ({email}) created successfully in Firestore!", 'success')
    except Exception as e:
        flash(f"Failed to create administrator: {e}", 'error')

    return redirect(url_for('admin.administrators'))

@admin_bp.route('/administrators/<user_id>/edit', methods=['POST'])
@admin_required
def edit_administrator(user_id):
    full_name = request.form.get('full_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    title = request.form.get('title', 'Administrator').strip()
    phone = request.form.get('phone', '').strip()
    affiliation = request.form.get('affiliation', '').strip()
    new_password = request.form.get('new_password', '').strip()

    if not full_name or not email:
        flash('Full Name and Email cannot be empty.', 'error')
        return redirect(url_for('admin.administrators'))

    update_data = {
        'full_name': full_name,
        'email': email,
        'title': title,
        'phone': phone,
        'affiliation': affiliation,
        'role': 'admin'
    }

    try:
        firebase_service.update_user(user_id, update_data, new_password=new_password if new_password else None)
        flash(f"Administrator profile '{full_name}' updated successfully in Firestore.", 'success')
    except Exception as e:
        flash(f"Error updating administrator: {e}", 'error')

    return redirect(url_for('admin.administrators'))

@admin_bp.route('/administrators/<user_id>/delete', methods=['POST'])
@admin_required
def delete_administrator(user_id):
    current_uid = session.get('user_id')
    if current_uid == user_id:
        flash("Action prohibited: You cannot delete your own active administrator account.", 'error')
        return redirect(url_for('admin.administrators'))

    try:
        firebase_service.delete_user(user_id)
        flash("Administrator account removed from Firestore.", 'success')
    except Exception as e:
        flash(f"Failed to delete administrator: {e}", 'error')

    return redirect(url_for('admin.administrators'))

# -------------------------------------------------------------
# REGISTRATIONS MANAGEMENT
# -------------------------------------------------------------
@admin_bp.route('/registrations')
@admin_required
def registrations():
    category = request.args.get('category')
    payment_status = request.args.get('payment_status')
    mode = request.args.get('mode')

    all_regs = firebase_service.get_all_registrations(
        category=category,
        payment_status=payment_status,
        mode=mode
    )

    return render_template(
        'admin/registrations.html',
        registrations=all_regs,
        category=category,
        payment_status=payment_status,
        mode=mode,
        fees=Config.FEES
    )

@admin_bp.route('/registrations/<reg_id>/update-payment', methods=['POST'])
@admin_required
def update_registration_payment(reg_id):
    payment_status = request.form.get('payment_status', 'Confirmed')
    admin_notes = request.form.get('admin_notes', '')

    firebase_service.update_registration_payment(
        reg_id=reg_id,
        payment_status=payment_status,
        admin_notes=admin_notes
    )
    flash(f"Registration {reg_id} payment status updated to '{payment_status}'.", 'success')
    return redirect(url_for('admin.registrations'))

# -------------------------------------------------------------
# SUBMISSIONS MANAGEMENT
# -------------------------------------------------------------
@admin_bp.route('/submissions')
@admin_required
def submissions():
    status = request.args.get('status')
    subtheme = request.args.get('subtheme')

    all_subs = firebase_service.get_all_submissions(status=status, subtheme=subtheme)
    all_subthemes = firebase_service.get_subthemes()

    return render_template(
        'admin/submissions.html',
        submissions=all_subs,
        status=status,
        subtheme=subtheme,
        subthemes=all_subthemes
    )

@admin_bp.route('/submissions/<paper_id>/review', methods=['GET', 'POST'])
@admin_required
def review_submission(paper_id):
    sub = firebase_service.get_submission(paper_id)
    if not sub:
        flash('Paper submission not found.', 'error')
        return redirect(url_for('admin.submissions'))

    if request.method == 'POST':
        new_status = request.form.get('status', sub.get('status'))
        review_notes = request.form.get('review_notes', '')
        reviewer_score = request.form.get('reviewer_score')
        if reviewer_score:
            try:
                reviewer_score = int(reviewer_score)
            except ValueError:
                reviewer_score = None

        firebase_service.update_submission_status(
            paper_id=paper_id,
            status=new_status,
            review_notes=review_notes,
            reviewer_score=reviewer_score
        )
        flash(f"Submission {paper_id} status updated to '{new_status}' successfully!", 'success')
        return redirect(url_for('admin.submissions'))

    return render_template('admin/submission_review.html', sub=sub)

# -------------------------------------------------------------
# DYNAMIC CMS: SPEAKERS, SUBTHEMES, SCHEDULE, ANNOUNCEMENTS
# -------------------------------------------------------------
@admin_bp.route('/speakers', methods=['GET', 'POST'])
@admin_required
def speakers():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        title = request.form.get('title', '').strip()
        designation = request.form.get('designation', '').strip()
        institution = request.form.get('institution', '').strip()
        category = request.form.get('category', 'keynote')
        bio = request.form.get('bio', '').strip()
        order = int(request.form.get('order', 10))
        image_url = request.form.get('image_url', '').strip()

        # Handle image file upload if provided
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            upload_res = firebase_service.upload_file(image_file, subfolder='speakers')
            if upload_res:
                image_url = upload_res.get('url')

        if not image_url:
            image_url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80"

        speaker_doc = {
            'name': name,
            'title': title,
            'designation': designation,
            'institution': institution,
            'category': category,
            'bio': bio,
            'order': order,
            'image_url': image_url
        }

        speaker_id = request.form.get('speaker_id')
        firebase_service.save_speaker(speaker_doc, speaker_id=speaker_id if speaker_id else None)
        flash('Speaker saved successfully!', 'success')
        return redirect(url_for('admin.speakers'))

    all_speakers = firebase_service.get_speakers()
    return render_template('admin/speakers.html', speakers=all_speakers)

@admin_bp.route('/speakers/<speaker_id>/delete', methods=['POST'])
@admin_required
def delete_speaker(speaker_id):
    firebase_service.delete_speaker(speaker_id)
    flash('Speaker deleted successfully.', 'success')
    return redirect(url_for('admin.speakers'))

@admin_bp.route('/subthemes', methods=['GET', 'POST'])
@admin_required
def subthemes():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        track = request.form.get('track', '').strip()
        track_slug = request.form.get('track_slug', 'general')
        description = request.form.get('description', '').strip()
        order = int(request.form.get('order', 99))

        subtheme_doc = {
            'title': title,
            'track': track,
            'track_slug': track_slug,
            'description': description,
            'order': order
        }
        subtheme_id = request.form.get('subtheme_id')
        firebase_service.save_subtheme(subtheme_doc, subtheme_id=subtheme_id if subtheme_id else None)
        flash('Sub-theme saved successfully!', 'success')
        return redirect(url_for('admin.subthemes'))

    all_subthemes = firebase_service.get_subthemes()
    return render_template('admin/subthemes.html', subthemes=all_subthemes)

@admin_bp.route('/subthemes/<subtheme_id>/delete', methods=['POST'])
@admin_required
def delete_subtheme(subtheme_id):
    firebase_service.delete_subtheme(subtheme_id)
    flash('Sub-theme removed successfully.', 'success')
    return redirect(url_for('admin.subthemes'))

@admin_bp.route('/announcements', methods=['GET', 'POST'])
@admin_required
def announcements():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        category = request.form.get('category', 'General')
        is_pinned = request.form.get('is_pinned') == 'on'
        date = request.form.get('date', '')

        ann_doc = {
            'title': title,
            'content': content,
            'category': category,
            'is_pinned': is_pinned,
            'date': date
        }
        firebase_service.save_announcement(ann_doc)
        flash('Announcement published successfully!', 'success')
        return redirect(url_for('admin.announcements'))

    all_announcements = firebase_service.get_announcements()
    return render_template('admin/announcements.html', announcements=all_announcements)

@admin_bp.route('/announcements/<ann_id>/delete', methods=['POST'])
@admin_required
def delete_announcement(ann_id):
    firebase_service.delete_announcement(ann_id)
    flash('Announcement deleted.', 'success')
    return redirect(url_for('admin.announcements'))

@admin_bp.route('/schedule', methods=['GET', 'POST'])
@admin_required
def schedule_cms():
    if request.method == 'POST':
        day_number = int(request.form.get('day_number', 1))
        day_label = request.form.get('day_label', '').strip()
        date_str = request.form.get('date', '').strip()
        
        event_time = request.form.get('event_time', '').strip()
        event_title = request.form.get('event_title', '').strip()
        event_location = request.form.get('event_location', '').strip()
        event_type = request.form.get('event_type', 'Parallel')

        existing_days = firebase_service.get_schedule()
        target_day = next((d for d in existing_days if d.get('day_number') == day_number), None)

        new_event = {
            'time': event_time,
            'title': event_title,
            'location': event_location,
            'type': event_type
        }

        if target_day:
            events = target_day.get('events', [])
            events.append(new_event)
            target_day['events'] = events
            if day_label: target_day['day_label'] = day_label
            if date_str: target_day['date'] = date_str
            firebase_service.save_schedule_item(target_day, item_id=target_day['id'])
        else:
            new_day_doc = {
                'day_number': day_number,
                'day_label': day_label or f"Day {day_number}",
                'date': date_str,
                'events': [new_event]
            }
            firebase_service.save_schedule_item(new_day_doc)

        flash('Schedule session updated successfully!', 'success')
        return redirect(url_for('admin.schedule_cms'))

    schedule_data = firebase_service.get_schedule()
    return render_template('admin/schedule.html', schedule=schedule_data)

@admin_bp.route('/schedule/<item_id>/delete', methods=['POST'])
@admin_required
def delete_schedule(item_id):
    firebase_service.delete_schedule_item(item_id)
    flash('Schedule day removed.', 'success')
    return redirect(url_for('admin.schedule_cms'))

@admin_bp.route('/messages')
@admin_required
def messages():
    all_msgs = firebase_service.query_collection('contact_messages', order_by='created_at', reverse=True)
    return render_template('admin/messages.html', messages=all_msgs)

# -------------------------------------------------------------
# CSV EXPORT
# -------------------------------------------------------------
@admin_bp.route('/export/<data_type>')
@admin_required
def export_csv(data_type):
    output = io.StringIO()
    writer = csv.writer(output)

    if data_type == 'registrations':
        regs = firebase_service.get_all_registrations()
        writer.writerow([
            'Registration ID', 'Full Name', 'Title', 'Email', 'Phone',
            'Affiliation', 'Department', 'Country', 'Mode', 'Category',
            'Fee Amount', 'Currency', 'Payment Status', 'Transaction Ref', 'Date'
        ])
        for r in regs:
            writer.writerow([
                r.get('id'), r.get('full_name'), r.get('title'), r.get('email'), r.get('phone'),
                r.get('affiliation'), r.get('department'), r.get('country'), r.get('mode'),
                r.get('category_name'), r.get('fee_amount'), r.get('currency'),
                r.get('payment_status'), r.get('transaction_ref'), r.get('created_at')
            ])
        filename = "ICONFST26_Registrations_Export.csv"

    elif data_type == 'submissions':
        subs = firebase_service.get_all_submissions()
        writer.writerow([
            'Paper ID', 'Title', 'Corresponding Author', 'Author Email', 'Phone',
            'Affiliation', 'Co-Authors', 'Sub-theme', 'Keywords', 'Status',
            'Reviewer Score', 'Review Notes', 'Submission Date'
        ])
        for s in subs:
            writer.writerow([
                s.get('id'), s.get('title'), s.get('author_name'), s.get('author_email'), s.get('author_phone'),
                s.get('author_affiliation'), s.get('co_authors'), s.get('subtheme'),
                ', '.join(s.get('keywords', [])) if isinstance(s.get('keywords'), list) else str(s.get('keywords')),
                s.get('status'), s.get('reviewer_score'), s.get('review_notes'), s.get('created_at')
            ])
        filename = "ICONFST26_Submissions_Export.csv"
    else:
        flash('Invalid export type requested.', 'error')
        return redirect(url_for('admin.dashboard'))

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv; charset=utf-8"
    return response
