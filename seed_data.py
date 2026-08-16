"""
Database Seed Script for ICONFST'26 Conference
Populates initial Dignitaries/Speakers, Sub-themes, Schedule, and Admin User.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from app.firebase_service import firebase_service

def seed_database():
    app = Flask(__name__)
    app.config.from_object(Config)
    firebase_service.init_app(app)
    
    print("==================================================")
    print("[*] SEEDING ICONFST'26 CONFERENCE DATABASE...")
    print("==================================================")

    # 1. SEED ADMIN USER
    admin_email = "admin@gaposastconf.org"
    existing_admin = firebase_service.get_user_by_email(admin_email)
    if not existing_admin:
        admin_user = firebase_service.create_user(
            email=admin_email,
            password="AdminPassword2026!",
            full_name="Conference Administrator",
            role="admin",
            affiliation="The Gateway (ICT) Polytechnic, Saapade",
            phone="+2348062618986",
            title="Administrator"
        )
        print(f"[OK] Admin account created: {admin_email} / AdminPassword2026!")
    else:
        print(f"[INFO] Admin account already exists: {admin_email}")

    # Also seed a demo participant/author account
    author_email = "author@gaposastconf.org"
    if not firebase_service.get_user_by_email(author_email):
        firebase_service.create_user(
            email=author_email,
            password="AuthorPassword2026!",
            full_name="Dr. Adebayo Ogunlesi",
            role="author",
            affiliation="Department of Computer Science, Gateway Polytechnic",
            phone="+2348038499893",
            title="Dr."
        )
        print(f"[OK] Demo Author account created: {author_email} / AuthorPassword2026!")

    # 2. SEED SPEAKERS & DIGNITARIES
    speakers_data = [
        {
            "name": "Dr. Sanni Kehinde Oseni",
            "title": "Chief Host",
            "designation": "Rector, The Gateway (ICT) Polytechnic, Saapade",
            "institution": "The Gateway (ICT) Polytechnic, Saapade, Ogun State",
            "category": "leadership",
            "bio": "Distinguished academic leader, visionary rector steering The Gateway (ICT) Polytechnic Saapade toward cutting-edge technological innovation, research excellence, and sustainable industry partnerships.",
            "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80",
            "order": 1
        },
        {
            "name": "Mr. Eleyowo, I. O",
            "title": "Host",
            "designation": "Dean, School of Science and Technology",
            "institution": "The Gateway (ICT) Polytechnic, Saapade, Ogun State",
            "category": "leadership",
            "bio": "Seasoned administrator and scholar championing scientific inquiry, practical technology translation, and academic excellence within the School of Science and Technology.",
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80",
            "order": 2
        },
        {
            "name": "Prof. Sojinu Olatunbosun Samuel",
            "title": "Lead Paper Presenter",
            "designation": "Professor of Organic Geochemistry & Head, Department of Geology",
            "institution": "Federal University of Agriculture, Abeokuta (FUNAAB)",
            "category": "keynote",
            "bio": "Renowned authority in organic geochemistry, environmental analysis, and fossil resource research with extensive publications across premier international journals.",
            "image_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&auto=format&fit=crop&q=80",
            "order": 3
        },
        {
            "name": "Engr. Dr. Rilwan Olaolu Oliyide",
            "title": "Keynote Speaker",
            "designation": "B.Eng, MSc., Ph.D, Department of Electrical/Electronic Engineering",
            "institution": "Moshood Abiola Polytechnic (MAPOLY), Abeokuta",
            "category": "keynote",
            "bio": "Foremost expert in electrical engineering, smart systems, renewable power architectures, and technological bridge-building between Nigerian academia and industrial manufacturing.",
            "image_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=500&auto=format&fit=crop&q=80",
            "order": 4
        },
        {
            "name": "Mr. Olujimi O Oni",
            "title": "Chairman LoC",
            "designation": "Chairman, School of Science and Technology Conference Committee",
            "institution": "The Gateway (ICT) Polytechnic, Saapade",
            "category": "organizer",
            "bio": "Dedicated conference organizer leading the Local Organizing Committee to deliver a memorable, high-impact hybrid conference for local and international delegates.",
            "image_url": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=500&auto=format&fit=crop&q=80",
            "order": 5
        }
    ]

    for spk in speakers_data:
        firebase_service.save_speaker(spk)
    print(f"[OK] Seeded {len(speakers_data)} Dignitaries & Keynote Speakers.")

    # 3. SEED SUB-THEMES (Organized by Tracks)
    tracks_subthemes = [
        # Track 1
        ("Biological, Health & Environmental Sciences", "biology", [
            "Biotechnology for Sustainable Development",
            "Medical and Health Innovations from Biological Research",
            "Molecular Biology and Genetic Engineering Applications",
            "Biodiversity Conservation and Ecosystem",
            "Sustainability Bioinformatics and Computational Biology in Modern Research",
            "Biology Climate Change and Ecosystem Management",
            "Environmental Pollution Monitoring and Control",
            "Sustainable Natural Resource Management",
            "Urban Ecology and Environmental Health",
            "Conservation Biology and Wildlife Protection"
        ]),
        # Track 2
        ("Food, Agricultural & Nutritional Sciences", "agriculture", [
            "Food Security and Sustainable Agriculture",
            "Food Processing, Preservation, and Packaging Innovations",
            "Nutritional Science and Public Health",
            "Food Safety, Quality Control, and Regulation",
            "Functional Foods and Nutraceutical Development"
        ]),
        # Track 3
        ("Chemical, Materials & Pharmaceutical Sciences", "chemistry", [
            "Green Chemistry and Sustainable Chemical Processes",
            "Industrial Chemistry and Technology Transfer",
            "Materials Chemistry and Nanotechnology",
            "Environmental and Analytical Chemistry",
            "Pharmaceutical and Medicinal Chemistry"
        ]),
        # Track 4
        ("Physics, Energy & Space Technologies", "physics", [
            "Renewable Energy and Sustainable Power Systems",
            "Applied Physics in Industrial Technology",
            "Materials Science and Nanophysics",
            "Medical Physics and Imaging Technology",
            "Space Science and Emerging Physical Technologies"
        ]),
        # Track 5
        ("Mathematical & Computational Sciences", "math", [
            "Mathematical Modelling for Sustainable Development",
            "Applied Mathematics in Engineering and Industry",
            "Computational Mathematics and Scientific Computing",
            "Optimization Techniques for Industrial Applications",
            "Mathematics in Climate and Environmental Studies"
        ]),
        # Track 6
        ("Artificial Intelligence, Computing & Data Science", "computing", [
            "Artificial Intelligence and Machine Learning for Industry",
            "Cybersecurity and Data Protection in the Digital Age",
            "Internet of Things (IoT) and Smart Systems",
            "Software Engineering and Digital Innovation",
            "Big Data Analytics and Cloud Computing",
            "Data Science and Predictive Analytics"
        ]),
        # Track 7
        ("Statistical Modelling & Quality Analytics", "statistics", [
            "Statistical Modelling for Decision Making",
            "Biostatistics and Health Data Analysis",
            "Industrial Statistics and Quality Control",
            "Statistical Applications in Climate and Environmental Research"
        ]),
        # Track 8
        ("Academia-Industry Synergy, Policy & Commercialization", "policy", [
            "Academia–Industry Collaboration for Innovation",
            "Research Commercialization and Technology Transfer",
            "Entrepreneurship and Start-up Development from Research",
            "Science Policy, Education, and Sustainable Development",
            "Ethical Issues in Scientific Research and Innovation"
        ])
    ]

    order_idx = 1
    total_subthemes = 0
    for track_name, track_slug, topics in tracks_subthemes:
        for topic in topics:
            sub_doc = {
                "title": topic,
                "track": track_name,
                "track_slug": track_slug,
                "order": order_idx,
                "description": f"Exploring advancements, industrial applications, and sustainable research breakthroughs in {topic}."
            }
            firebase_service.save_subtheme(sub_doc)
            order_idx += 1
            total_subthemes += 1

    print(f"[OK] Seeded {total_subthemes} Sub-themes across 8 thematic tracks.")

    # 4. SEED CONFERENCE SCHEDULE
    schedule_data = [
        {
            "day_number": 1,
            "day_label": "Day 1: Arrival & Welcome",
            "date": "Sunday, 23rd August, 2026",
            "events": [
                {"time": "12:00 PM - 05:00 PM", "title": "Arrival & Accreditation of Delegates", "location": "Foyer, Prince Dapo Abiodun Hall", "type": "Registration"},
                {"time": "05:00 PM - 06:30 PM", "title": "Welcome Reception & Icebreaker", "location": "Polytechnic Guest House Lawn", "type": "Social"},
                {"time": "07:00 PM - 08:30 PM", "title": "LoC & Technical Reviewers Meeting", "location": "Conference Boardroom", "type": "Internal"}
            ]
        },
        {
            "day_number": 2,
            "day_label": "Day 2: Opening Ceremony & Plenary",
            "date": "Monday, 24th August, 2026",
            "events": [
                {"time": "08:00 AM - 09:30 AM", "title": "Registration & Kit Collection", "location": "Main Entrance Desk", "type": "Registration"},
                {"time": "09:30 AM - 10:30 AM", "title": "Grand Opening Ceremony & Welcome Address by Rector Dr. Sanni Kehinde Oseni", "location": "Main Auditorium", "type": "Ceremony"},
                {"time": "10:30 AM - 11:30 AM", "title": "Keynote Address: Engr. Dr. Rilwan Olaolu Oliyide", "location": "Main Auditorium", "type": "Keynote"},
                {"time": "11:30 AM - 12:30 PM", "title": "Lead Paper Presentation: Prof. Sojinu Olatunbosun Samuel", "location": "Main Auditorium", "type": "Keynote"},
                {"time": "12:30 PM - 01:30 PM", "title": "Group Photographs & Exhibition / Tea Break", "location": "Quadrangle", "type": "Break"},
                {"time": "01:30 PM - 04:30 PM", "title": "Parallel Technical Sessions (Tracks A, B, C, D)", "location": "Seminar Rooms 1 - 4 & Virtual Rooms", "type": "Parallel"}
            ]
        },
        {
            "day_number": 3,
            "day_label": "Day 3: Parallel Sessions & Exhibition",
            "date": "Tuesday, 25th August, 2026",
            "events": [
                {"time": "09:00 AM - 12:30 PM", "title": "Parallel Technical Sessions (Tracks E, F, G, H)", "location": "Seminar Rooms 1 - 4 & Virtual Rooms", "type": "Parallel"},
                {"time": "12:30 PM - 01:30 PM", "title": "Poster Presentations & Innovations Showcase", "location": "Exhibition Hall", "type": "Poster"},
                {"time": "01:30 PM - 02:30 PM", "title": "Networking Lunch", "location": "Banquet Hall", "type": "Break"},
                {"time": "02:30 PM - 04:00 PM", "title": "High-Level Panel: Academia-Industry Commercialization", "location": "Main Auditorium", "type": "Panel"},
                {"time": "06:30 PM - 09:30 PM", "title": "Conference Gala Dinner & Award Presentation", "location": "Grand Ballroom", "type": "Dinner"}
            ]
        },
        {
            "day_number": 4,
            "day_label": "Day 4: Communique & Departure",
            "date": "Wednesday, 26th August, 2026",
            "events": [
                {"time": "09:30 AM - 11:00 AM", "title": "Presentation of Conference Communique & Synthesis", "location": "Main Auditorium", "type": "Plenary"},
                {"time": "11:00 AM - 12:00 PM", "title": "Distribution of Certificates & Closing Remarks", "location": "Main Auditorium", "type": "Closing"},
                {"time": "12:00 PM - Departure", "title": "Delegates Departure & Excursion to Tourist Sites in Ogun State", "location": "Saapade", "type": "Social"}
            ]
        }
    ]

    for item in schedule_data:
        firebase_service.save_schedule_item(item)
    print(f"[OK] Seeded {len(schedule_data)} days Conference Schedule.")

    # 5. SEED ANNOUNCEMENTS
    announcements_data = [
        {
            "title": "Call for Papers Now Open!",
            "content": "Authors from academia and industry are invited to submit abstracts and full manuscripts across our 8 thematic tracks. Deadline for abstract submission is 31st July, 2026.",
            "is_pinned": True,
            "category": "Call for Papers",
            "date": "2026-06-01"
        },
        {
            "title": "Early Bird Registration Open",
            "content": "Take advantage of discounted Early Bird rates (₦20,000 for Local Scholars) valid until 31st July 2026. Student discounts (₦5,000) also available.",
            "is_pinned": True,
            "category": "Registration",
            "date": "2026-06-15"
        },
        {
            "title": "Hybrid Attendance Information",
            "content": "Both physical attendance at Prince Dapo Abiodun Hall and seamless virtual live-streaming options are available for local and international delegates.",
            "is_pinned": False,
            "category": "General",
            "date": "2026-07-01"
        }
    ]

    for ann in announcements_data:
        firebase_service.save_announcement(ann)
    print(f"[OK] Seeded {len(announcements_data)} Announcements.")

    print("==================================================")
    print("[SUCCESS] DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    seed_database()
