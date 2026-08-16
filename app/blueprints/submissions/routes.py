import os
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.firebase_service import firebase_service
from config import Config

sub_bp = Blueprint('submissions', __name__)

def count_words(text):
    if not text:
        return 0
    return len(text.strip().split())

@sub_bp.route('/submit', methods=['GET', 'POST'])
def submit():
    subthemes = firebase_service.get_subthemes()
    
    # Pre-fill with user info if logged in
    current_user = None
    if session.get('user_id'):
        current_user = firebase_service.get_user_by_id(session.get('user_id'))

    deadline_passed = False
    deadline_date = datetime.strptime(Config.DEADLINE_ABSTRACT_SUBMISSION, "%Y-%m-%d").date()
    # If today is strictly past deadline (though in dev/staging we still allow submission with a late indicator)
    # deadline_passed = date.today() > deadline_date

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author_name = request.form.get('author_name', '').strip()
        author_email = request.form.get('author_email', '').strip().lower()
        author_phone = request.form.get('author_phone', '').strip()
        author_affiliation = request.form.get('author_affiliation', '').strip()
        co_authors = request.form.get('co_authors', '').strip()
        subtheme = request.form.get('subtheme', '').strip()
        abstract_text = request.form.get('abstract_text', '').strip()
        keywords = request.form.get('keywords', '').strip()
        paper_file = request.files.get('paper_file')

        # Validation
        if not title or not author_name or not author_email or not subtheme or not abstract_text:
            flash('Please fill in all mandatory fields.', 'error')
            return render_template('submissions/submit.html', subthemes=subthemes, user=current_user, config=Config)

        # Word count check
        words = count_words(abstract_text)
        if words > Config.ABSTRACT_MAX_WORDS:
            flash(f'Abstract length exceeds {Config.ABSTRACT_MAX_WORDS} words (Current: {words} words). Please condense your abstract.', 'error')
            return render_template('submissions/submit.html', subthemes=subthemes, user=current_user, config=Config)

        # Keywords check (3 - 5 items)
        keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
        if len(keyword_list) < Config.KEYWORDS_MIN or len(keyword_list) > Config.KEYWORDS_MAX:
            flash(f'Please provide between {Config.KEYWORDS_MIN} and {Config.KEYWORDS_MAX} comma-separated keywords.', 'error')
            return render_template('submissions/submit.html', subthemes=subthemes, user=current_user, config=Config)

        # File validation
        file_url = None
        file_name = None
        if paper_file and paper_file.filename:
            ext = os.path.splitext(paper_file.filename)[1].lower()
            if ext not in ['.pdf', '.doc', '.docx']:
                flash('Please upload your paper in PDF or DOC/DOCX format (PDF strongly recommended).', 'error')
                return render_template('submissions/submit.html', subthemes=subthemes, user=current_user, config=Config)
            
            upload_res = firebase_service.upload_file(paper_file, subfolder='papers')
            if upload_res:
                file_url = upload_res.get('url')
                file_name = upload_res.get('filename')

        submission_data = {
            'title': title,
            'author_name': author_name,
            'author_email': author_email,
            'author_phone': author_phone,
            'author_affiliation': author_affiliation,
            'co_authors': co_authors,
            'subtheme': subtheme,
            'abstract_text': abstract_text,
            'word_count': words,
            'keywords': keyword_list,
            'paper_file_url': file_url,
            'paper_filename': file_name,
            'user_id': session.get('user_id'),
            'status': 'Submitted'
        }

        created_sub = firebase_service.create_submission(submission_data)
        flash(f"Paper submission successful! Your Paper Reference ID is {created_sub['id']}.", 'success')
        return redirect(url_for('submissions.track_paper', paper_id=created_sub['id']))

    return render_template(
        'submissions/submit.html',
        subthemes=subthemes,
        user=current_user,
        config=Config,
        deadline_passed=deadline_passed
    )

@sub_bp.route('/track', methods=['GET', 'POST'])
def track():
    submission = None
    searched = False

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        searched = True
        if query.startswith('ICONFST26-PAP-') or query.startswith('PAP-') or query.startswith('iconfst'):
            return redirect(url_for('submissions.track_paper', paper_id=query.upper()))
        else:
            # Query by author email
            subs = firebase_service.get_user_submissions(query)
            if subs:
                submission = subs[0]

    return render_template('submissions/track.html', submission=submission, searched=searched)

@sub_bp.route('/track/<paper_id>', methods=['GET'])
def track_paper(paper_id):
    submission = firebase_service.get_submission(paper_id)
    return render_template('submissions/track.html', submission=submission, searched=True, paper_id=paper_id)
