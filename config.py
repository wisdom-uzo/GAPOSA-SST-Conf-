import os
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def _safe_int_env(key, default):
    val = os.environ.get(key)
    if not val or not str(val).strip().isdigit():
        return default
    return int(val)

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'iconfst26-super-secret-key-gaposa-2026-prod') or 'iconfst26-super-secret-key-gaposa-2026-prod'
    DEBUG = (os.environ.get('FLASK_DEBUG') or 'False').lower() in ('true', '1', 't')
    PORT = _safe_int_env('PORT', 5000)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    UPLOAD_EXTENSIONS = ['.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg']

    # Conference Metadata
    CONFERENCE_NAME = "International Conference on Science and Technology"
    CONFERENCE_TAG = "ICONFST’26"
    CONFERENCE_TAGLINE = "TAGGED: ICONFST'26"
    CONFERENCE_THEME = "Sustainable Research from Gown to Town: Bridging the Academia and Industry Divide"
    CONFERENCE_ORGANIZER = "The School of Science and Technology, The Gateway (ICT) Polytechnic Saapade, Ogun State, Nigeria."
    CONFERENCE_VENUE = "Prince Dapo Abiodun CON Leadership Hall, The Gateway (ICT) Polytechnic, Saapade"
    CONFERENCE_START_DATE = "2026-08-23"
    CONFERENCE_END_DATE = "2026-08-26"
    CONFERENCE_MODE = "Virtual & Physical"
    
    # Official Contact Info
    CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'gaposastconf@gmail.com')
    CONTACT_PHONES = [
        '+23480-6261-8986',
        '+23480-3849-9893',
        '+23470-3888-9578',
        '+23480-6918-1102'
    ]
    OFFICIAL_WEBSITE = "https://www.gaposastconf.org/"

    # Payment / Bank Details
    BANK_NAME = "Zenith Bank PLC"
    BANK_ACCOUNT_NAME = "Gaposa SS&T Conference and Journal"
    BANK_ACCOUNT_NUMBER = "1226078857"

    # Deadlines (Year 2026)
    DEADLINE_ABSTRACT_SUBMISSION = "2026-07-31"
    DEADLINE_EARLY_BIRD = "2026-07-31"
    DEADLINE_MID_REGISTRATION = "2026-08-15"
    DEADLINE_LATE_REGISTRATION = "2026-08-27"
    CONFERENCE_START = "2026-08-23"

    # Paper Submission Guidelines
    PAPER_MAX_PAGES = 12
    PAPER_SPACING = "1.5"
    PAPER_FONT = "12pt Times New Roman"
    PAPER_REF_STYLE = "APA 7th Edition"
    ABSTRACT_MAX_WORDS = 200
    KEYWORDS_MIN = 3
    KEYWORDS_MAX = 5

    # Fee Structure
    FEES = {
        'student': {
            'name': 'Students (Undergraduate / Postgraduate)',
            'amount_ngn': 5000,
            'amount_usd': None,
            'currency': 'NGN',
            'symbol': '₦',
            'description': 'Valid student ID required upon check-in'
        },
        'local_scholar_early': {
            'name': 'Scholars / Local (Early Bird)',
            'amount_ngn': 20000,
            'amount_usd': None,
            'currency': 'NGN',
            'symbol': '₦',
            'valid_until': '2026-07-31',
            'description': 'Valid from 15th to 31st July, 2026'
        },
        'local_scholar_mid': {
            'name': 'Scholars / Local (Mid Registration)',
            'amount_ngn': 25000,
            'amount_usd': None,
            'currency': 'NGN',
            'symbol': '₦',
            'valid_until': '2026-08-15',
            'description': 'Valid from 1st to 15th August, 2026'
        },
        'local_scholar_late': {
            'name': 'Scholars / Local (Late Registration)',
            'amount_ngn': 30000,
            'amount_usd': None,
            'currency': 'NGN',
            'symbol': '₦',
            'valid_until': '2026-08-27',
            'description': 'Valid from 16th to 27th August, 2026'
        },
        'international_scholar': {
            'name': 'International Scholars / Attendees',
            'amount_ngn': None,
            'amount_usd': 20,
            'currency': 'USD',
            'symbol': '$',
            'description': 'For international participants ($20 flat)'
        },
        'virtual_local': {
            'name': 'Virtual Participation (Local)',
            'amount_ngn': 20000,
            'amount_usd': None,
            'currency': 'NGN',
            'symbol': '₦',
            'description': 'Online attendance with full session access & digital certificate'
        }
    }

    # Firebase Settings
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', 'gaposa-sst-conf-and-journal')
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-service-account.json')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET', 'gaposa-sst-conf-and-journal.firebasestorage.app')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', 'AIzaSyBE_4r1CQUjTR1bvWSS1xYbMmt_cv7XjgY')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', 'gaposa-sst-conf-and-journal.firebaseapp.com')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID', '776095698979')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID', '1:776095698979:web:1b0df4c6f54bda0d456196')
    FIREBASE_DATABASE_URL = os.environ.get('FIREBASE_DATABASE_URL', '')
    
    # Fallback / Local Storage directory for local uploads when Firebase Storage is not active
    LOCAL_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')

    @classmethod
    def get_current_local_fee_tier(cls, check_date=None):
        """Returns the active fee category key for local scholars based on date."""
        if check_date is None:
            check_date = date.today()
        elif isinstance(check_date, str):
            check_date = datetime.strptime(check_date, "%Y-%m-%d").date()

        early_cutoff = datetime.strptime(cls.DEADLINE_EARLY_BIRD, "%Y-%m-%d").date()
        mid_cutoff = datetime.strptime(cls.DEADLINE_MID_REGISTRATION, "%Y-%m-%d").date()

        if check_date <= early_cutoff:
            return 'local_scholar_early'
        elif check_date <= mid_cutoff:
            return 'local_scholar_mid'
        else:
            return 'local_scholar_late'
