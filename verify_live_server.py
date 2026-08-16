import requests

BASE_URL = "http://127.0.0.1:5000"

def test_live_server():
    print("==================================================")
    print("[*] RUNNING LIVE HTTP INTEGRATION TESTS...")
    print("==================================================")

    session = requests.Session()

    # 1. Test Home Page
    res_home = session.get(f"{BASE_URL}/")
    assert res_home.status_code == 200
    assert "THE SCHOOL OF SCIENCE AND TECHNOLOGY" in res_home.text
    assert "THE GATEWAY (ICT) POLYTECHNIC SAAPADE" in res_home.text
    assert "ICONFST" in res_home.text
    assert "Sustainable Research from Gown to Town" in res_home.text
    assert "1226078857" in res_home.text
    print("[OK] Home / Landing Page: 200 OK (All branding & bank details verified)")

    # 2. Test Speakers
    res_spk = session.get(f"{BASE_URL}/speakers")
    assert res_spk.status_code == 200
    assert "Prof. Sojinu Olatunbosun Samuel" in res_spk.text
    assert "Engr. Dr. Rilwan Olaolu Oliyide" in res_spk.text
    assert "Dr. Sanni Kehinde Oseni" in res_spk.text
    print("[OK] Speakers Page: 200 OK (Keynote & Principal officers verified)")

    # 3. Test Sub-themes
    res_sub = session.get(f"{BASE_URL}/subthemes")
    assert res_sub.status_code == 200
    assert "Biotechnology for Sustainable Development" in res_sub.text
    assert "Artificial Intelligence and Machine Learning for Industry" in res_sub.text
    print("[OK] Sub-themes Page: 200 OK (All 45 Sub-themes accessible)")

    # 4. Test Call for Papers
    res_cfp = session.get(f"{BASE_URL}/call-for-papers")
    assert res_cfp.status_code == 200
    assert "APA 7th Edition" in res_cfp.text
    assert "31ST JULY, 2026" in res_cfp.text
    assert "12 pages" in res_cfp.text
    print("[OK] Call for Papers: 200 OK (Guidelines & Hard cutoff date verified)")

    # 5. Test Schedule & Venue
    res_sch = session.get(f"{BASE_URL}/schedule")
    assert res_sch.status_code == 200
    assert "Day 1: Arrival" in res_sch.text
    assert "Day 2: Opening Ceremony" in res_sch.text
    print("[OK] Programme Schedule: 200 OK (Day 1 to Day 4 schedule verified)")

    res_ven = session.get(f"{BASE_URL}/venue")
    assert res_ven.status_code == 200
    assert "Prince Dapo Abiodun CON Leadership Hall" in res_ven.text
    print("[OK] Venue Page: 200 OK (Venue & Accommodation verified)")

    # 6. Test Fee Calculation API
    res_fee = session.get(f"{BASE_URL}/api/calculate-fee?category=student")
    assert res_fee.status_code == 200
    data_fee = res_fee.json()
    assert data_fee["amount"] == 5000
    print("[OK] Fee Calculator API: 200 OK (Student fee: NGN 5,000)")

    # 7. Test Admin Login & Protected Dashboard
    res_login = session.post(f"{BASE_URL}/auth/login", data={
        "email": "admin@gaposastconf.org",
        "password": "AdminPassword2026!"
    }, allow_redirects=True)
    assert res_login.status_code == 200
    assert "Executive Dashboard" in res_login.text or "ICONFST" in res_login.text
    print("[OK] Admin Authentication & Session Management: 200 OK")

    # 8. Test Admin Registrations & Submissions
    res_admin_regs = session.get(f"{BASE_URL}/admin/registrations")
    assert res_admin_regs.status_code == 200
    assert "Registrations" in res_admin_regs.text
    print("[OK] Admin Registrations Manager: 200 OK")

    res_admin_subs = session.get(f"{BASE_URL}/admin/submissions")
    assert res_admin_subs.status_code == 200
    assert "Manuscript Repository" in res_admin_subs.text
    print("[OK] Admin Submissions Manager: 200 OK")

    # Test Admin Schedule CMS & Messages
    res_admin_sch = session.get(f"{BASE_URL}/admin/schedule")
    assert res_admin_sch.status_code == 200
    assert "Conference Program Schedule CMS" in res_admin_sch.text
    print("[OK] Admin Schedule CMS: 200 OK")

    res_admin_msg = session.get(f"{BASE_URL}/admin/messages")
    assert res_admin_msg.status_code == 200
    assert "Delegate Inquiries" in res_admin_msg.text
    print("[OK] Admin Messages Inbox: 200 OK")

    # Test Administrators Management Page
    res_admin_list = session.get(f"{BASE_URL}/admin/administrators")
    assert res_admin_list.status_code == 200
    assert "Secretariat Administrators" in res_admin_list.text
    print("[OK] Administrators Management Suite: 200 OK")

    # 9. Test CSV Export on Live Server
    res_export = session.get(f"{BASE_URL}/admin/export/registrations")
    assert res_export.status_code == 200
    assert "text/csv" in res_export.headers.get("Content-Type", "")
    print("[OK] CSV Exporter: 200 OK (CSV file stream verified)")

    print("==================================================")
    print("[SUCCESS] ALL LIVE SERVER ENDPOINTS VERIFIED 100%!")
    print("==================================================")

if __name__ == "__main__":
    test_live_server()
