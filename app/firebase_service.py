import os
import json
import uuid
import time
import shutil
import requests
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# Try importing Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class CloudFirestoreRESTClient:
    """
    Direct Cloud Firestore REST API Client for Google Cloud Firestore.
    Uses the project's Web API Key to perform live Firestore CRUD operations.
    """
    def __init__(self, project_id, api_key):
        self.project_id = project_id
        self.api_key = api_key
        self.base_url = f"https://firestore.googleapis.com/v1/projects/{self.project_id}/databases/(default)/documents"

    @staticmethod
    def _to_firestore_value(val):
        if val is None:
            return {'nullValue': None}
        elif isinstance(val, bool):
            return {'booleanValue': val}
        elif isinstance(val, int):
            return {'integerValue': str(val)}
        elif isinstance(val, float):
            return {'doubleValue': val}
        elif isinstance(val, str):
            return {'stringValue': val}
        elif isinstance(val, list):
            return {'arrayValue': {'values': [CloudFirestoreRESTClient._to_firestore_value(v) for v in val]}}
        elif isinstance(val, dict):
            return {'mapValue': {'fields': {k: CloudFirestoreRESTClient._to_firestore_value(v) for k, v in val.items()}}}
        return {'stringValue': str(val)}

    @staticmethod
    def _from_firestore_value(val_obj):
        if not isinstance(val_obj, dict):
            return val_obj
        if 'nullValue' in val_obj:
            return None
        elif 'booleanValue' in val_obj:
            return val_obj['booleanValue']
        elif 'integerValue' in val_obj:
            try:
                return int(val_obj['integerValue'])
            except (ValueError, TypeError):
                return val_obj['integerValue']
        elif 'doubleValue' in val_obj:
            return float(val_obj['doubleValue'])
        elif 'stringValue' in val_obj:
            return val_obj['stringValue']
        elif 'arrayValue' in val_obj:
            values = val_obj.get('arrayValue', {}).get('values', [])
            return [CloudFirestoreRESTClient._from_firestore_value(v) for v in values]
        elif 'mapValue' in val_obj:
            fields = val_obj.get('mapValue', {}).get('fields', {})
            return {k: CloudFirestoreRESTClient._from_firestore_value(v) for k, v in fields.items()}
        return None

    @staticmethod
    def _from_firestore_doc(doc_obj):
        if not doc_obj or 'fields' not in doc_obj:
            return None
        data = {}
        for k, v in doc_obj.get('fields', {}).items():
            data[k] = CloudFirestoreRESTClient._from_firestore_value(v)
        
        # Extract doc ID from full path
        name = doc_obj.get('name', '')
        if name:
            doc_id = name.split('/')[-1]
            data['id'] = doc_id
        return data

    def get_document(self, collection_name, doc_id):
        url = f"{self.base_url}/{collection_name}/{doc_id}?key={self.api_key}"
        try:
            res = requests.get(url, timeout=20)
            if res.status_code == 200:
                return self._from_firestore_doc(res.json())
            return None
        except Exception as e:
            print(f"[ERROR] Firestore get_document failed for {collection_name}/{doc_id}: {e}", flush=True)
            return None

    def set_document(self, collection_name, doc_id, data, merge=True):
        if merge:
            existing = self.get_document(collection_name, doc_id)
            if existing:
                merged = dict(existing)
                merged.update(data)
                data = merged

        url = f"{self.base_url}/{collection_name}/{doc_id}?key={self.api_key}"
        fields = {k: self._to_firestore_value(v) for k, v in data.items()}
        payload = {'fields': fields}
        try:
            res = requests.patch(url, json=payload, timeout=20)
            if res.status_code == 200:
                return self._from_firestore_doc(res.json())
            return data
        except Exception as e:
            print(f"[ERROR] Firestore set_document failed for {collection_name}/{doc_id}: {e}", flush=True)
            return data

    def delete_document(self, collection_name, doc_id):
        url = f"{self.base_url}/{collection_name}/{doc_id}?key={self.api_key}"
        try:
            res = requests.delete(url, timeout=20)
            return res.status_code == 200
        except Exception as e:
            print(f"[ERROR] Firestore delete_document failed for {collection_name}/{doc_id}: {e}", flush=True)
            return False

    def query_collection(self, collection_name, filters=None, order_by=None, reverse=False, limit=None):
        url = f"{self.base_url}/{collection_name}?key={self.api_key}&pageSize=300"
        try:
            res = requests.get(url, timeout=20)
            if res.status_code != 200:
                return []
            
            docs = res.json().get('documents', [])
            items = []
            for d in docs:
                parsed = self._from_firestore_doc(d)
                if parsed:
                    items.append(parsed)

            if filters:
                for k, v in filters.items():
                    if v is not None:
                        if isinstance(v, str):
                            v_clean = v.lower().strip()
                            items = [it for it in items if str(it.get(k, '')).lower().strip() == v_clean]
                        else:
                            items = [it for it in items if it.get(k) == v]

            if order_by:
                items.sort(key=lambda x: str(x.get(order_by, '')), reverse=reverse)

            if limit:
                items = items[:limit]

            return items
        except Exception as e:
            print(f"[ERROR] Firestore query failed for {collection_name}: {e}", flush=True)
            return []


class LocalFirebaseSimulator:
    """
    Persistent Local Storage simulator fallback.
    """
    def __init__(self, data_dir=None):
        if not data_dir:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data_store')
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.upload_dir = os.path.join(self.data_dir, 'uploads')
        os.makedirs(self.upload_dir, exist_ok=True)

    def _get_coll_file(self, collection_name):
        return os.path.join(self.data_dir, f"{collection_name}.json")

    def _load_collection(self, collection_name):
        file_path = self._get_coll_file(collection_name)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_collection(self, collection_name, data):
        file_path = self._get_coll_file(collection_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def get_doc(self, collection_name, doc_id):
        coll = self._load_collection(collection_name)
        return coll.get(doc_id)

    def set_doc(self, collection_name, doc_id, data, merge=True):
        coll = self._load_collection(collection_name)
        if merge and doc_id in coll:
            coll[doc_id].update(data)
        else:
            coll[doc_id] = data
        self._save_collection(collection_name, coll)
        return coll[doc_id]

    def delete_doc(self, collection_name, doc_id):
        coll = self._load_collection(collection_name)
        if doc_id in coll:
            del coll[doc_id]
            self._save_collection(collection_name, coll)
            return True
        return False

    def query(self, collection_name, filters=None, order_by=None, reverse=False, limit=None):
        coll = self._load_collection(collection_name)
        items = list(coll.values())

        if filters:
            for key, val in filters.items():
                if val is not None:
                    items = [item for item in items if item.get(key) == val]

        if order_by:
            items.sort(key=lambda x: str(x.get(order_by, '')), reverse=reverse)

        if limit:
            items = items[:limit]

        return items

    def save_file(self, file_obj, subfolder='papers', filename=None):
        if not filename:
            filename = secure_filename(file_obj.filename)
        dest_dir = os.path.join(self.upload_dir, subfolder)
        os.makedirs(dest_dir, exist_ok=True)
        unique_name = f"{int(time.time())}_{uuid.uuid4().hex[:6]}_{filename}"
        dest_path = os.path.join(dest_dir, unique_name)
        file_obj.save(dest_path)
        
        web_url = f"/static/uploads/{subfolder}/{unique_name}"
        
        static_uploads = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app', 'static', 'uploads', subfolder)
        os.makedirs(static_uploads, exist_ok=True)
        shutil.copy2(dest_path, os.path.join(static_uploads, unique_name))

        return {
            'url': web_url,
            'local_path': dest_path,
            'filename': unique_name,
            'original_filename': filename
        }


class FirebaseService:
    def __init__(self, app=None):
        self.app = app
        self.is_live = False
        self.db = None
        self.bucket = None
        
        # Always connect directly to Live Google Cloud Firestore
        project_id = os.environ.get('FIREBASE_PROJECT_ID', 'gaposa-sst-conf-and-journal')
        api_key = os.environ.get('FIREBASE_API_KEY', 'AIzaSyBE_4r1CQUjTR1bvWSS1xYbMmt_cv7XjgY')
        self.rest_client = CloudFirestoreRESTClient(project_id, api_key)
        self.is_live = True

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        cred_path = app.config.get('FIREBASE_CREDENTIALS_PATH')
        project_id = app.config.get('FIREBASE_PROJECT_ID', 'gaposa-sst-conf-and-journal')
        api_key = app.config.get('FIREBASE_API_KEY', 'AIzaSyBE_4r1CQUjTR1bvWSS1xYbMmt_cv7XjgY')
        storage_bucket = app.config.get('FIREBASE_STORAGE_BUCKET')

        # 1. First, check if live Firebase Admin SDK credentials file exists
        if FIREBASE_AVAILABLE and cred_path and os.path.exists(cred_path):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id,
                        'storageBucket': storage_bucket
                    })
                self.db = firestore.client()
                try:
                    self.bucket = storage.bucket()
                except Exception:
                    pass
                self.is_live = True
                app.logger.info("Connected to live Firebase Admin SDK.")
                return
            except Exception as e:
                app.logger.warning(f"Admin SDK init failed: {e}")

        # 2. Initialize Live Cloud Firestore REST Client
        if project_id and api_key:
            self.rest_client = CloudFirestoreRESTClient(project_id, api_key)
            self.is_live = True
            app.logger.info(f"Connected directly to Live Google Cloud Firestore (Project: {project_id}).")

    # -------------------------------------------------------------
    # GENERIC FIRESTORE HELPERS
    # -------------------------------------------------------------
    def get_document(self, collection_name, doc_id):
        # 1. Cloud Firestore REST API (Reliable across all Python versions on Windows)
        if self.rest_client:
            try:
                res = self.rest_client.get_document(collection_name, doc_id)
                if res is not None:
                    return res
            except Exception as e:
                pass

        # 2. Admin SDK fallback
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(doc_id)
                doc = doc_ref.get()
                if doc.exists:
                    data = doc.to_dict()
                    data['id'] = doc.id
                    return data
            except Exception as e:
                pass

        return None

    def set_document(self, collection_name, doc_id, data, merge=True):
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        if 'created_at' not in data:
            data['created_at'] = datetime.now(timezone.utc).isoformat()
        data['id'] = doc_id

        # 1. Cloud Firestore REST API
        if self.rest_client:
            try:
                return self.rest_client.set_document(collection_name, doc_id, data, merge=merge)
            except Exception as e:
                pass

        # 2. Admin SDK fallback
        if self.db:
            try:
                doc_ref = self.db.collection(collection_name).document(doc_id)
                doc_ref.set(data, merge=merge)
                return data
            except Exception as e:
                pass

        return data

    def delete_document(self, collection_name, doc_id):
        if self.rest_client:
            try:
                return self.rest_client.delete_document(collection_name, doc_id)
            except Exception as e:
                pass

        if self.db:
            try:
                self.db.collection(collection_name).document(doc_id).delete()
                return True
            except Exception as e:
                pass

        return False

    def query_collection(self, collection_name, filters=None, order_by=None, reverse=False, limit=None):
        # 1. Cloud Firestore REST API (Fast, reliable, zero gRPC socket conflicts on Windows)
        if self.rest_client:
            try:
                return self.rest_client.query_collection(collection_name, filters=filters, order_by=order_by, reverse=reverse, limit=limit)
            except Exception as e:
                print(f"[WARN] REST query failed for {collection_name}: {e}", flush=True)

        # 2. Admin SDK fallback
        if self.db:
            try:
                ref = self.db.collection(collection_name)
                if filters:
                    for k, v in filters.items():
                        if v is not None:
                            ref = ref.where(k, '==', v)
                if order_by:
                    direction = firestore.Query.DESCENDING if reverse else firestore.Query.ASCENDING
                    ref = ref.order_by(order_by, direction=direction)
                if limit:
                    ref = ref.limit(limit)
                
                docs = ref.stream()
                results = []
                for doc in docs:
                    item = doc.to_dict()
                    item['id'] = doc.id
                    results.append(item)
                return results
            except Exception as e:
                print(f"[WARN] Admin SDK query failed for {collection_name}: {e}", flush=True)

        return []

    # -------------------------------------------------------------
    # AUTHENTICATION & USERS
    # -------------------------------------------------------------
    def create_user(self, email, password, full_name, role='participant', affiliation='', phone='', title=''):
        email = email.lower().strip()
        existing = self.get_user_by_email(email)
        if existing:
            raise ValueError("An account with this email address already exists.")

        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        password_hash = generate_password_hash(password)

        user_data = {
            'id': user_id,
            'email': email,
            'password_hash': password_hash,
            'full_name': full_name,
            'title': title,
            'role': role,
            'affiliation': affiliation,
            'phone': phone,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'is_active': True,
            'email_verified': False
        }

        self.set_document('users', user_id, user_data)
        return user_data

    def authenticate_user(self, email, password):
        email = email.lower().strip()
        users = self.query_collection('users', filters={'email': email}, limit=1)
        if not users:
            return None
        user = users[0]
        stored_hash = user.get('password_hash', '')
        if check_password_hash(stored_hash, password):
            return user
        return None

    def get_user_by_id(self, user_id):
        return self.get_document('users', user_id)

    def get_user_by_email(self, email):
        users = self.query_collection('users', filters={'email': email.lower().strip()}, limit=1)
        return users[0] if users else None

    def get_all_admins(self):
        return self.query_collection('users', filters={'role': 'admin'}, order_by='created_at', reverse=True)

    def update_user(self, user_id, update_data, new_password=None):
        if new_password and new_password.strip():
            update_data['password_hash'] = generate_password_hash(new_password.strip())
        update_data['updated_at'] = datetime.now(timezone.utc).isoformat()
        return self.set_document('users', user_id, update_data, merge=True)

    def delete_user(self, user_id):
        return self.delete_document('users', user_id)

    # -------------------------------------------------------------
    # REGISTRATIONS
    # -------------------------------------------------------------
    def generate_registration_id(self):
        random_code = uuid.uuid4().hex[:6].upper()
        return f"ICONFST26-REG-{random_code}"

    def create_registration(self, reg_data):
        reg_id = reg_data.get('id') or self.generate_registration_id()
        reg_data['id'] = reg_id
        reg_data['registration_id'] = reg_id
        reg_data['created_at'] = datetime.now(timezone.utc).isoformat()
        reg_data['payment_status'] = reg_data.get('payment_status', 'Pending')
        
        self.set_document('registrations', reg_id, reg_data)
        return reg_data

    def get_registration(self, reg_id):
        return self.get_document('registrations', reg_id)

    def update_registration_payment(self, reg_id, payment_proof_url=None, transaction_ref=None, payment_status='Confirmed', admin_notes=''):
        data = {
            'payment_status': payment_status,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        if payment_proof_url:
            data['payment_proof_url'] = payment_proof_url
        if transaction_ref:
            data['transaction_ref'] = transaction_ref
        if admin_notes:
            data['admin_notes'] = admin_notes
            
        return self.set_document('registrations', reg_id, data, merge=True)

    def get_user_registrations(self, user_email):
        return self.query_collection('registrations', filters={'email': user_email.lower().strip()}, order_by='created_at', reverse=True)

    def get_all_registrations(self, category=None, payment_status=None, mode=None):
        filters = {}
        if category:
            filters['category'] = category
        if payment_status:
            filters['payment_status'] = payment_status
        if mode:
            filters['mode'] = mode
        return self.query_collection('registrations', filters=filters if filters else None, order_by='created_at', reverse=True)

    # -------------------------------------------------------------
    # PAPER & ABSTRACT SUBMISSIONS
    # -------------------------------------------------------------
    def generate_paper_id(self):
        random_code = uuid.uuid4().hex[:5].upper()
        return f"ICONFST26-PAP-{random_code}"

    def create_submission(self, sub_data):
        paper_id = sub_data.get('id') or self.generate_paper_id()
        sub_data['id'] = paper_id
        sub_data['paper_id'] = paper_id
        sub_data['status'] = sub_data.get('status', 'Submitted')
        sub_data['created_at'] = datetime.now(timezone.utc).isoformat()
        sub_data['review_notes'] = sub_data.get('review_notes', '')
        sub_data['reviewer_score'] = sub_data.get('reviewer_score', None)
        
        self.set_document('submissions', paper_id, sub_data)
        return sub_data

    def get_submission(self, paper_id):
        return self.get_document('submissions', paper_id)

    def get_user_submissions(self, user_email):
        return self.query_collection('submissions', filters={'author_email': user_email.lower().strip()}, order_by='created_at', reverse=True)

    def get_all_submissions(self, status=None, subtheme=None):
        filters = {}
        if status:
            filters['status'] = status
        if subtheme:
            filters['subtheme'] = subtheme
        return self.query_collection('submissions', filters=filters if filters else None, order_by='created_at', reverse=True)

    def update_submission_status(self, paper_id, status, review_notes=None, reviewer_score=None):
        data = {
            'status': status,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        if review_notes is not None:
            data['review_notes'] = review_notes
        if reviewer_score is not None:
            data['reviewer_score'] = reviewer_score
        return self.set_document('submissions', paper_id, data, merge=True)

    def update_submission_file(self, paper_id, file_url, is_camera_ready=False):
        data = {
            'updated_at': datetime.now(timezone.utc).isoformat()
        }
        if is_camera_ready:
            data['camera_ready_file_url'] = file_url
            data['status'] = 'Camera-ready'
        else:
            data['paper_file_url'] = file_url
        return self.set_document('submissions', paper_id, data, merge=True)

    # -------------------------------------------------------------
    # FILE UPLOAD (FIREBASE STORAGE / LOCAL FALLBACK)
    # -------------------------------------------------------------
    def upload_file(self, file_obj, subfolder='papers', filename=None):
        if not file_obj or not file_obj.filename:
            return None

        clean_name = secure_filename(file_obj.filename)
        if not clean_name:
            clean_name = f"document_{int(time.time())}.pdf"

        # If live Firebase Storage is active, upload to bucket
        if self.bucket:
            try:
                unique_name = f"{subfolder}/{int(time.time())}_{uuid.uuid4().hex[:6]}_{clean_name}"
                blob = self.bucket.blob(unique_name)
                file_obj.seek(0)
                blob.upload_from_file(file_obj, content_type=file_obj.content_type)
                blob.make_public()
                return {
                    'url': blob.public_url,
                    'filename': clean_name,
                    'storage_path': unique_name,
                    'is_cloud': True
                }
            except Exception as e:
                self.app.logger.warning(f"Firebase Storage upload error: {e}. Falling back to local storage.")

        # Fallback to local storage simulator
        file_obj.seek(0)
        res = self.simulator.save_file(file_obj, subfolder=subfolder, filename=clean_name)
        res['is_cloud'] = False
        return res

    # -------------------------------------------------------------
    # SPEAKERS, SUBTHEMES, SCHEDULE & SETTINGS
    # -------------------------------------------------------------
    def get_speakers(self):
        speakers = self.query_collection('speakers', order_by='order')
        if not speakers:
            speakers = self.query_collection('speakers')
        return speakers

    def save_speaker(self, speaker_data, speaker_id=None):
        if not speaker_id:
            speaker_id = f"spk_{uuid.uuid4().hex[:8]}"
        speaker_data['id'] = speaker_id
        return self.set_document('speakers', speaker_id, speaker_data)

    def delete_speaker(self, speaker_id):
        return self.delete_document('speakers', speaker_id)

    def get_subthemes(self):
        subthemes = self.query_collection('subthemes', order_by='order')
        return subthemes

    def save_subtheme(self, subtheme_data, subtheme_id=None):
        if not subtheme_id:
            subtheme_id = f"sub_{uuid.uuid4().hex[:8]}"
        subtheme_data['id'] = subtheme_id
        return self.set_document('subthemes', subtheme_id, subtheme_data)

    def delete_subtheme(self, subtheme_id):
        return self.delete_document('subthemes', subtheme_id)

    def get_announcements(self):
        return self.query_collection('announcements', order_by='created_at', reverse=True)

    def save_announcement(self, ann_data, ann_id=None):
        if not ann_id:
            ann_id = f"ann_{uuid.uuid4().hex[:8]}"
        ann_data['id'] = ann_id
        return self.set_document('announcements', ann_id, ann_data)

    def delete_announcement(self, ann_id):
        return self.delete_document('announcements', ann_id)

    def get_schedule(self):
        return self.query_collection('schedule', order_by='day_number')

    def save_schedule_item(self, item_data, item_id=None):
        if not item_id:
            item_id = f"sch_{uuid.uuid4().hex[:8]}"
        item_data['id'] = item_id
        return self.set_document('schedule', item_id, item_data)

    def delete_schedule_item(self, item_id):
        return self.delete_document('schedule', item_id)

    # -------------------------------------------------------------
    # SYSTEM STATS & METRICS
    # -------------------------------------------------------------
    def get_analytics(self):
        registrations = self.query_collection('registrations')
        submissions = self.query_collection('submissions')
        users = self.query_collection('users')

        total_reg = len(registrations)
        total_sub = len(submissions)
        total_users = len(users)

        confirmed_reg = len([r for r in registrations if r.get('payment_status') == 'Confirmed'])
        pending_reg = len([r for r in registrations if r.get('payment_status') == 'Pending'])

        physical_count = len([r for r in registrations if r.get('mode') == 'Physical'])
        virtual_count = len([r for r in registrations if r.get('mode') == 'Virtual'])

        accepted_sub = len([s for s in submissions if s.get('status') == 'Accepted' or s.get('status') == 'Camera-ready'])
        under_review_sub = len([s for s in submissions if s.get('status') == 'Under Review'])
        rejected_sub = len([s for s in submissions if s.get('status') == 'Rejected'])
        submitted_sub = len([s for s in submissions if s.get('status') == 'Submitted'])

        subtheme_counts = {}
        for s in submissions:
            st = s.get('subtheme', 'General / Other')
            subtheme_counts[st] = subtheme_counts.get(st, 0) + 1

        total_revenue_ngn = 0
        total_revenue_usd = 0
        for r in registrations:
            if r.get('payment_status') == 'Confirmed':
                curr = r.get('currency', 'NGN')
                fee = r.get('fee_amount', 0)
                if curr == 'NGN':
                    total_revenue_ngn += fee
                elif curr == 'USD':
                    total_revenue_usd += fee

        return {
            'total_registrations': total_reg,
            'confirmed_registrations': confirmed_reg,
            'pending_registrations': pending_reg,
            'physical_count': physical_count,
            'virtual_count': virtual_count,
            'total_submissions': total_sub,
            'accepted_submissions': accepted_sub,
            'under_review_submissions': under_review_sub,
            'rejected_submissions': rejected_sub,
            'submitted_submissions': submitted_sub,
            'acceptance_rate': round((accepted_sub / total_sub * 100) if total_sub > 0 else 0, 1),
            'total_users': total_users,
            'total_revenue_ngn': total_revenue_ngn,
            'total_revenue_usd': total_revenue_usd,
            'subtheme_counts': subtheme_counts
        }


# Global singleton instance
firebase_service = FirebaseService()
