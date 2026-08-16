import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from app.blueprints.auth.routes import login_required
from app.firebase_service import firebase_service
from config import Config

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    user = g.user
    registrations = firebase_service.get_user_registrations(user['email'])
    submissions = firebase_service.get_user_submissions(user['email'])
    
    return render_template(
        'user/dashboard.html',
        user=user,
        registrations=registrations,
        submissions=submissions,
        config=Config
    )

@user_bp.route('/registrations')
@login_required
def my_registrations():
    user = g.user
    registrations = firebase_service.get_user_registrations(user['email'])
    return render_template('user/my_registrations.html', registrations=registrations, user=user)

@user_bp.route('/submissions')
@login_required
def my_submissions():
    user = g.user
    submissions = firebase_service.get_user_submissions(user['email'])
    return render_template('user/my_submissions.html', submissions=submissions, user=user)

@user_bp.route('/submissions/<paper_id>/reupload', methods=['POST'])
@login_required
def reupload_paper(paper_id):
    user = g.user
    sub = firebase_service.get_submission(paper_id)
    if not sub or sub.get('author_email') != user['email']:
        flash('Submission not found or unauthorized access.', 'error')
        return redirect(url_for('user.my_submissions'))

    is_camera_ready = request.form.get('is_camera_ready') == 'true'
    paper_file = request.files.get('paper_file')

    if paper_file and paper_file.filename:
        upload_res = firebase_service.upload_file(paper_file, subfolder='papers')
        if upload_res:
            file_url = upload_res.get('url')
            firebase_service.update_submission_file(paper_id, file_url, is_camera_ready=is_camera_ready)
            label = "Camera-ready manuscript" if is_camera_ready else "Revised paper"
            flash(f'{label} uploaded successfully!', 'success')
        else:
            flash('File upload failed. Please try again.', 'error')
    else:
        flash('Please select a valid PDF file.', 'error')

    return redirect(url_for('user.my_submissions'))

@user_bp.route('/acceptance-letter/<paper_id>')
@login_required
def acceptance_letter(paper_id):
    user = g.user
    sub = firebase_service.get_submission(paper_id)
    if not sub or (sub.get('author_email') != user['email'] and user.get('role') != 'admin'):
        flash('Paper record not found or unauthorized.', 'error')
        return redirect(url_for('user.dashboard'))

    if sub.get('status') not in ['Accepted', 'Camera-ready']:
        flash('Acceptance letter is only generated for papers with status "Accepted".', 'warning')
        return redirect(url_for('user.my_submissions'))

    return render_template('user/acceptance_letter.html', sub=sub, user=user, config=Config)

@user_bp.route('/certificate/<reg_id>')
@login_required
def certificate(reg_id):
    user = g.user
    reg = firebase_service.get_registration(reg_id)
    if not reg or (reg.get('email') != user['email'] and user.get('role') != 'admin'):
        flash('Registration record not found or unauthorized.', 'error')
        return redirect(url_for('user.dashboard'))

    return render_template('user/certificate.html', reg=reg, user=user, config=Config)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = g.user
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        title = request.form.get('title', 'Mr.')
        affiliation = request.form.get('affiliation', '').strip()

        updated = {
            'full_name': full_name,
            'phone': phone,
            'title': title,
            'affiliation': affiliation
        }
        firebase_service.set_document('users', user['id'], updated, merge=True)
        session['user_name'] = full_name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', user=user)
