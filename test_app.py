import io
import unittest
from app import create_app
from config import Config
from app.firebase_service import firebase_service

class TestConferenceApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

    def test_public_routes(self):
        routes = ['/', '/about', '/speakers', '/subthemes', '/call-for-papers', '/schedule', '/venue', '/contact', '/privacy', '/terms']
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            self.assertIn(b"ICONFST", res.data)

    def test_api_fee_calculator(self):
        res = self.client.get('/api/calculate-fee?category=student')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['amount'], 5000)
        self.assertEqual(data['currency'], 'NGN')

        res_intl = self.client.get('/api/calculate-fee?category=international_scholar')
        self.assertEqual(res_intl.status_code, 200)
        data_intl = res_intl.get_json()
        self.assertEqual(data_intl['amount'], 20)
        self.assertEqual(data_intl['currency'], 'USD')

    def test_registration_flow(self):
        # 1. Submit Registration
        reg_payload = {
            'title': 'Dr.',
            'full_name': 'Prof. Test Participant',
            'email': 'testparticipant@gaposastconf.org',
            'phone': '+2348011223344',
            'affiliation': 'Gateway Polytechnic Saapade',
            'department': 'Science Laboratory Technology',
            'country': 'Nigeria',
            'mode': 'Physical',
            'category': 'local_scholar'
        }
        res = self.client.post('/registration/register', data=reg_payload, follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        redirect_url = res.headers['Location']
        self.assertIn('/registration/payment/', redirect_url)

        reg_id = redirect_url.split('/')[-1]
        
        # 2. View Payment page
        res_pay = self.client.get(f'/registration/payment/{reg_id}')
        self.assertEqual(res_pay.status_code, 200)
        self.assertIn(b"1226078857", res_pay.data)
        self.assertIn(b"Zenith Bank", res_pay.data)

        # 3. Submit Payment Proof
        res_pay_post = self.client.post(f'/registration/payment/{reg_id}', data={
            'transaction_ref': 'TEST-ZENITH-REF-9988'
        }, follow_redirects=True)
        self.assertEqual(res_pay_post.status_code, 200)
        self.assertIn(b"Registration Successful", res_pay_post.data)

        # 4. View Slip
        res_slip = self.client.get(f'/registration/slip/{reg_id}')
        self.assertEqual(res_slip.status_code, 200)
        self.assertIn(b"OFFICIAL REGISTRATION SLIP", res_slip.data)

    def test_submission_flow(self):
        # Submit Paper
        sub_payload = {
            'title': 'Automated IoT Sensor Networks for Sustainable Agriculture',
            'author_name': 'Dr. Adebayo Test Author',
            'author_email': 'testauthor@gaposastconf.org',
            'author_phone': '+2348099887766',
            'author_affiliation': 'Department of Computer Science, Gateway Poly',
            'co_authors': 'Engr. J. Doe (MAPOLY)',
            'subtheme': 'Artificial Intelligence and Machine Learning for Industry',
            'abstract_text': 'This paper presents a novel low-power IoT architecture designed to optimize agricultural irrigation in sub-Saharan climates.',
            'keywords': 'IoT, Smart Agriculture, Sensors, Sustainability',
            'paper_file': (io.BytesIO(b'%PDF-1.4 Mock Manuscript PDF Content'), 'test_paper.pdf')
        }
        res = self.client.post('/submissions/submit', data=sub_payload, content_type='multipart/form-data', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        redirect_url = res.headers['Location']
        self.assertIn('/submissions/track/', redirect_url)

        paper_id = redirect_url.split('/')[-1]

        # Track Paper
        res_track = self.client.get(f'/submissions/track/{paper_id}')
        self.assertEqual(res_track.status_code, 200)
        self.assertIn(b"Automated IoT Sensor Networks", res_track.data)

    def test_admin_flow(self):
        # 1. Login as Admin
        res_login = self.client.post('/auth/login', data={
            'email': 'admin@gaposastconf.org',
            'password': 'AdminPassword2026!'
        }, follow_redirects=True)
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Executive Dashboard", res_login.data)

        # 2. Access Admin Pages
        res_regs = self.client.get('/admin/registrations')
        self.assertEqual(res_regs.status_code, 200)

        res_subs = self.client.get('/admin/submissions')
        self.assertEqual(res_subs.status_code, 200)

        res_speakers = self.client.get('/admin/speakers')
        self.assertEqual(res_speakers.status_code, 200)

        res_schedule = self.client.get('/admin/schedule')
        self.assertEqual(res_schedule.status_code, 200)

        res_messages = self.client.get('/admin/messages')
        self.assertEqual(res_messages.status_code, 200)

        # 3. CSV Export
        res_csv = self.client.get('/admin/export/registrations')
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn(b"Registration ID", res_csv.data)

if __name__ == '__main__':
    unittest.main()
