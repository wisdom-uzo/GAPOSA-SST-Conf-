# ICONFST’26 - International Conference on Science and Technology Web System
### The Gateway (ICT) Polytechnic Saapade, Ogun State, Nigeria

![ICONFST'26 Banner](https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&auto=format&fit=crop&q=80)

**Theme:** *“Sustainable Research from Gown to Town: Bridging the Academia and Industry Divide”*  
**Tagged:** `ICONFST’26`  
**Dates:** Sunday, 23rd August, 2026 – Thursday, 26th August, 2026  
**Venue:** Prince Dapo Abiodun CON Leadership Hall, The Gateway (ICT) Polytechnic, Saapade  
**Mode:** Hybrid (Physical & Virtual)  
**Official Email:** `gaposastconf@gmail.com`  
**Official Helplines:** `+23480-6261-8986`, `+23480-3849-9893`, `+23470-3888-9578`, `+23480-6918-1102`  

---

## 🌟 Overview

This is the production-ready web application and conference management system built specifically for the **International Conference on Science and Technology (ICONFST’26)** organized by **The School of Science and Technology, The Gateway (ICT) Polytechnic Saapade**.

The application features:
1. **Public Conference Website:** Modern landing page with interactive countdown timer, dynamic fee calculator, 45+ searchable sub-themes, keynote speaker profiles, program schedule, and venue logistics.
2. **Registration Engine:** Automatic tiered fee calculator for Nigerian scholars (Early bird ₦20,000 / Mid ₦25,000 / Late ₦30,000), students (₦5,000), international scholars ($20), and virtual delegates (₦20,000). Official registration badge and printable slip generation.
3. **Paper & Abstract Submission Portal:** Author submissions with real-time abstract word counter (max 200 words), keywords tags (3-5 keywords), sub-theme selection, and PDF manuscript uploads to Firebase Storage with status tracking.
4. **Author Dashboard:** Status pipeline tracking (`Submitted` &rarr; `Under Review` &rarr; `Accepted` / `Revision Required` / `Rejected` &rarr; `Camera-ready`), camera-ready file re-upload, official Acceptance Letter with stamp and signature generator, and Certificate of Participation.
5. **Admin & Secretariat Dashboard:** Review submitted manuscripts, assign reviewer scores, update acceptance decisions, verify bank payments, manage speakers and announcements, and export all data directly to CSV.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.10+ / Flask 3.1+ (Modular architecture using Flask Blueprints)
- **Frontend:** Tailwind CSS, Font Awesome 6.5, Google Fonts (*Outfit* & *Plus Jakarta Sans*), Vanilla JS
- **Database & Cloud Storage:** Google Cloud Firestore (NoSQL) & Google Firebase Storage
- **Authentication:** Firebase Auth / Session-based authentication with role differentiation (`admin`, `author`, `participant`)
- **WSGI & Server:** Gunicorn, Python WSGI

---

## 📁 Project Structure

```
CONFRANCE/
├── app/
│   ├── __init__.py                 # Flask App Factory, context processors & Jinja filters
│   ├── firebase_service.py         # Firebase Admin SDK & Local Firestore/Storage engine
│   ├── blueprints/
│   │   ├── main/routes.py          # Public conference routes (Home, About, Speakers, Subthemes, etc.)
│   │   ├── auth/routes.py          # Login, Register, Password Reset & Session Management
│   │   ├── registration/routes.py  # Fee calculation engine, registration & bank payment upload
│   │   ├── submissions/routes.py   # Paper & Abstract submission portal and tracking
│   │   ├── user/routes.py          # User Dashboard, camera-ready upload, Acceptance Letters
│   │   ├── admin/routes.py         # Executive Admin suite, reviews, CSV exporter, CMS
│   │   └── api/routes.py           # JSON API endpoints
│   ├── static/
│   │   ├── css/custom.css          # Theme styling, mesh gradients, glassmorphism & print rules
│   │   ├── js/main.js              # Live countdown timer, word counter, fee calculator
│   │   └── uploads/                # Local storage fallback directory for manuscripts & receipts
│   └── templates/
│       ├── base.html               # Master layout with Tailwind CDN and SEO tags
│       ├── components/             # Reusable UI components (Navbar, Footer, Flash Alerts)
│       ├── main/                   # Public page views (index, about, speakers, subthemes, etc.)
│       ├── auth/                   # Authentication forms (login, register, forgot password)
│       ├── registration/           # Registration forms, payment page, badge & slip
│       ├── submissions/            # Submission form and live tracker
│       ├── user/                   # Dashboard, submissions list, acceptance letters, certificate
│       ├── admin/                  # Admin dashboard, reviews, registrations table, CMS
│       └── errors/                 # 404, 500, and 403 error pages
├── config.py                       # App constants, deadlines, Zenith Bank info, and fee matrices
├── seed_data.py                    # Database seeder (Populates 45 sub-themes, 5 dignitaries, schedule)
├── firestore.rules                 # Production Firestore security rules
├── storage.rules                   # Production Cloud Storage security rules
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment variables template
├── run.py                          # Local development entrypoint
├── wsgi.py                         # Production WSGI entrypoint
└── README.md                       # Documentation
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Install Dependencies
```bash
# Navigate to project directory
cd CONFRANCE

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Seed Database
Run the automated seed script to populate all 45 conference sub-themes, keynote speakers, 4-day schedule, announcements, and default accounts:
```bash
python seed_data.py
```

### 4. Run the Development Server
```bash
python run.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

---

## 🔑 Default Accounts (For Testing)

| Role | Email | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@gaposastconf.org` | `AdminPassword2026!` | Full Secretariat & Review Suite (`/admin/dashboard`) |
| **Author / Scholar** | `author@gaposastconf.org` | `AuthorPassword2026!` | User Dashboard, Paper Submission & Letters (`/user/dashboard`) |

---

## ☁️ Firebase Production Configuration

To connect this application directly to your live Google Firebase project:

1. Go to the [Firebase Console](https://console.firebase.google.com/) and create a project (e.g. `iconfst26-conference`).
2. Enable **Cloud Firestore** in production mode.
3. Enable **Firebase Storage** for file storage.
4. Enable **Firebase Authentication** (Email/Password and optionally Google Sign-In).
5. Go to **Project Settings &rarr; Service Accounts**, click **Generate new private key**, and download the JSON file.
6. Rename the file to `firebase-service-account.json` and place it in the root directory of this project.
7. Update your `.env` file with your Firebase parameters:
   ```ini
   FIREBASE_CREDENTIALS_PATH=firebase-service-account.json
   FIREBASE_PROJECT_ID=your-project-id
   FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
   ```
8. Deploy Firestore & Storage rules using Firebase CLI:
   ```bash
   firebase deploy --only firestore:rules,storage:rules
   ```

*Note: If no service account JSON is detected, the app automatically runs on its built-in local persistence engine without breaking.*

---

## 💳 Conference Fee Structure & Official Bank Account

### Fee Matrix
- **Students (Undergraduate / Postgraduate):** ₦5,000
- **Nigerian Scholars (Early Bird, Ends 31 July 2026):** ₦20,000
- **Nigerian Scholars (Mid Registration, 1–15 Aug 2026):** ₦25,000
- **Nigerian Scholars (Late Registration, 16–27 Aug 2026):** ₦30,000
- **International Scholars:** $20 USD
- **Virtual Participation (Local):** ₦20,000 flat

### Bank Details for Direct Transfer
- **Bank Name:** Zenith Bank PLC
- **Account Name:** Gaposa SS&T Conference and Journal
- **Account Number:** `1226078857`

---

## 🚢 Production Deployment

### Running with Gunicorn (Production WSGI)
```bash
# Start with Gunicorn on production port (e.g. 5000 or 8080)
gunicorn --bind 0.0.0.0:5000 --workers 4 --threads 2 wsgi:app
```

### Running with Systemd or Nginx / VPS
You can configure Nginx as a reverse proxy pointing to `http://127.0.0.1:5000` with standard SSL certificate (Certbot / Let's Encrypt).

---

## 📄 License & Attribution
Organized and managed by **The School of Science and Technology, The Gateway (ICT) Polytechnic Saapade, Ogun State, Nigeria**.
Website portal developed for ICONFST’26.
