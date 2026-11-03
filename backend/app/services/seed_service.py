import datetime
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import (
    DemoUser, Subject, Topic, Document, DocumentContent,
    Question, QuestionRevision, SourceEvidence, QuestionTopic,
    QuestionSet, QuestionSetItem, Paper, PaperSection, PaperItem,
    Attempt, AttemptItem, Response, Notification, DemoSeedVersion
)

ITS_DOCUMENT_TEXT = """
INTELLIGENT TRANSPORT SYSTEMS (ITS-401)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING

UNIT 1: INTRODUCTION TO INTELLIGENT TRANSPORT SYSTEMS
1.1 Fundamentals and Architecture of ITS
Intelligent Transport Systems (ITS) integrate advanced information, communication, electronics, and sensor technologies into transportation networks to enhance mobility, improve road safety, and minimize environmental impact. The national ITS architecture consists of physical, logical, and communication layers that interconnect traffic management centers, roadside field equipment, vehicles, and commuters.

1.2 Sensor Technologies and Traffic Surveillance
Traffic data collection utilizes both intrusive and non-intrusive sensors. Inductive loop detectors embedded beneath pavement detect magnetic field disruptions caused by metallic vehicle chassis, providing reliable vehicle counts, speed, and occupancy metrics. Non-intrusive sensors include pneumatic road tubes, microwave radars, infrared sensors, and computer vision closed-circuit television (CCTV) cameras. Video Image Processing Systems (VIPS) employ deep learning for automated incident detection and license plate recognition.

UNIT 2: ADVANCED TRAFFIC MANAGEMENT SYSTEMS (ATMS)
2.1 Real-Time Traffic Signal Optimization
Advanced Traffic Management Systems (ATMS) dynamically adjust traffic signal timings based on real-time saturation levels. SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets to minimize vehicular delay and stop frequencies across arterial corridors.

2.2 Incident Detection and Ramp Metering
Automated incident detection algorithms monitor flow fluctuations. Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways, preventing freeway breakdown and shockwave propagation during peak demand periods. Variable Message Signs (VMS) disseminate real-time advisory alerts and lane closure warnings.

UNIT 3: ADVANCED TRAVELER INFORMATION SYSTEMS (ATIS)
3.1 Architecture of ATIS and Commuter Guidance
Advanced Traveler Information Systems (ATIS) deliver pre-trip and en-route travel information to road users. By processing historical traffic baselines alongside live crowdsourced probe GPS feeds, ATIS platforms provide dynamic route guidance, estimated times of arrival (ETA), and multimodal transit alternatives.

3.2 Electronic Toll Collection (ETC) and RFID
Automated Electronic Toll Collection systems, such as FASTag, leverage Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz). As an RFID-tagged vehicle crosses an electronic toll plaza at speed, overhead transceivers read tag IDs and automatically debit linked prepaid bank wallets, eliminating manual cash delays and reducing emissions.

UNIT 4: CONNECTED AND AUTONOMOUS VEHICLES (CAV)
4.1 V2X Communication Frameworks
Vehicle-to-Everything (V2X) communication encompasses Vehicle-to-Vehicle (V2V), Vehicle-to-Infrastructure (V2I), and Vehicle-to-Pedestrian (V2P) exchanges. Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters). Cellular-V2X (C-V2X) utilizes 4G LTE and 5G sidelink PC5 direct communication, providing longer range and greater bandwidth for sensor sharing.

4.2 Cooperative Adaptive Cruise Control and Platooning
Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.
""".strip()

def seed_database(db: Session, force: bool = False):
    """
    Deterministically seeds the database with initial ITS-401 course data.
    """
    # Check if already seeded
    seed_record = db.query(DemoSeedVersion).first()
    if seed_record and not force:
        return
        
    # Clear existing demo seed records if forcing
    if force:
        # Delete demo attempts, papers, questions, documents
        db.query(Response).delete()
        db.query(AttemptItem).delete()
        db.query(Attempt).delete()
        db.query(PaperItem).delete()
        db.query(PaperSection).delete()
        db.query(Paper).delete()
        db.query(QuestionSetItem).delete()
        db.query(QuestionSet).delete()
        db.query(SourceEvidence).delete()
        db.query(QuestionRevision).delete()
        db.query(Question).delete()
        db.query(DocumentContent).delete()
        db.query(Document).delete()
        db.query(Topic).delete()
        db.query(Subject).delete()
        db.query(DemoUser).delete()
        db.query(Notification).delete()
        db.query(DemoSeedVersion).delete()
        db.commit()

    # 1. Demo Users
    prof = DemoUser(
        id="prof_sharma",
        name="Dr. R. Sharma",
        role="faculty",
        email="r.sharma@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )
    student1 = DemoUser(
        id="student_aditi",
        name="Aditi Rao",
        role="student",
        email="aditi.cs21@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
    )
    student2 = DemoUser(
        id="student_karthik",
        name="Karthik Nair",
        role="student",
        email="karthik.cs21@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    )
    db.add_all([prof, student1, student2])
    db.flush()

    # 2. Subject & Topics
    its_sub = Subject(
        id="ITS-401",
        code="ITS-401",
        name="Intelligent Transport Systems",
        description="Comprehensive study of modern sensing, traffic optimization, V2X communications, and autonomous mobility architectures."
    )
    db.add(its_sub)
    db.flush()

    topics_data = [
        (1, "Unit 1: Introduction to ITS", "Fundamentals and Architecture of ITS", "Physical, logical, and communications subsystems in ITS architecture."),
        (1, "Unit 1: Introduction to ITS", "Sensor Technologies and Traffic Surveillance", "Intrusive inductive loop detectors and non-intrusive radar/video sensors."),
        (2, "Unit 2: ATMS", "Real-Time Traffic Signal Optimization", "SCATS and SCOOT coordinated adaptive split and offset algorithms."),
        (2, "Unit 2: ATMS", "Incident Detection and Ramp Metering", "Freeway queue breakdown prevention, VMS signage, automated incident algorithms."),
        (3, "Unit 3: ATIS", "Architecture of ATIS and Commuter Guidance", "Real-time trip planning, GPS probe ingestion, dynamic ETA computation."),
        (3, "Unit 3: ATIS", "Electronic Toll Collection and RFID", "FASTag passive UHF RFID operation, antenna arrays, transponder protocols."),
        (4, "Unit 4: CAV", "V2X Communication Frameworks", "DSRC IEEE 802.11p 5.9GHz vs Cellular-V2X direct sidelink PC5."),
        (4, "Unit 4: CAV", "Cooperative Adaptive Cruise Control and Platooning", "Radar plus V2V messaging for ultra-tight multi-truck platooning."),
    ]
    
    created_topics = []
    for u_num, u_name, t_name, desc in topics_data:
        t = Topic(
            subject_id=its_sub.id,
            unit_number=u_num,
            unit_name=u_name,
            topic_name=t_name,
            description=desc
        )
        db.add(t)
        created_topics.append(t)
    db.flush()

    # 3. Document
    doc = Document(
        id="doc_its_notes_01",
        title="ITS Comprehensive Lecture Notes (Units 1-4)",
        subject_id=its_sub.id,
        unit_number=1,
        original_filename="ITS_Lecture_Notes_2026.pdf",
        safe_filename="ITS_Lecture_Notes_2026_demo.pdf",
        file_type="pdf",
        file_size=245800,
        extraction_status="completed",
        detected_headings=[
            "UNIT 1: INTRODUCTION TO INTELLIGENT TRANSPORT SYSTEMS",
            "1.1 Fundamentals and Architecture of ITS",
            "1.2 Sensor Technologies and Traffic Surveillance",
            "UNIT 2: ADVANCED TRAFFIC MANAGEMENT SYSTEMS (ATMS)",
            "2.1 Real-Time Traffic Signal Optimization",
            "2.2 Incident Detection and Ramp Metering",
            "UNIT 3: ADVANCED TRAVELER INFORMATION SYSTEMS (ATIS)",
            "3.1 Architecture of ATIS and Commuter Guidance",
            "3.2 Electronic Toll Collection (ETC) and RFID",
            "UNIT 4: CONNECTED AND AUTONOMOUS VEHICLES (CAV)",
            "4.1 V2X Communication Frameworks",
            "4.2 Cooperative Adaptive Cruise Control and Platooning"
        ],
        is_demo_seed=True
    )
    db.add(doc)
    db.flush()

    doc_content = DocumentContent(
        document_id=doc.id,
        full_text=ITS_DOCUMENT_TEXT,
        page_count=6,
        cleaned_text=ITS_DOCUMENT_TEXT,
        topics_json=["ITS Architecture", "Inductive Loops", "SCATS", "SCOOT", "Ramp Metering", "RFID FASTag", "DSRC 802.11p", "Cellular-V2X", "CACC Platooning"]
    )
    db.add(doc_content)
    db.flush()

    # 4. Questions & Revisions (Approved & Draft Seed Questions)
    seed_questions = [
        # Q1: MCQ (Unit 1)
        {
            "text": "Which technology forms the basis of intrusive traffic surveillance by detecting magnetic disruptions caused by vehicle chassis?",
            "type": "mcq",
            "options": ["Inductive loop detectors", "Pneumatic road tubes", "Microwave radar sensors", "Video image processing cameras"],
            "correct": "Inductive loop detectors",
            "model_ans": None,
            "rubric": None,
            "explanation": "Inductive loop detectors are embedded beneath pavement and detect magnetic field disruptions caused by metallic vehicle chassis, providing vehicle count and occupancy.",
            "diff": "easy",
            "marks": 2.0,
            "topic": created_topics[1],
            "excerpt": "Inductive loop detectors embedded beneath pavement detect magnetic field disruptions caused by metallic vehicle chassis, providing reliable vehicle counts, speed, and occupancy metrics.",
            "status": "approved"
        },
        # Q2: MCQ (Unit 2)
        {
            "text": "What is the primary operational objective of freeway ramp metering in an ATMS framework?",
            "type": "mcq",
            "options": ["To eliminate speed limits on entry ramps", "To regulate vehicle entry rates and prevent mainline freeway breakdown", "To collect electronic tolls automatically", "To inspect vehicle emissions prior to highway entry"],
            "correct": "To regulate vehicle entry rates and prevent mainline freeway breakdown",
            "model_ans": None,
            "rubric": None,
            "explanation": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate of vehicle entry, mitigating shockwave propagation and mainline freeway breakdown.",
            "diff": "medium",
            "marks": 2.0,
            "topic": created_topics[3],
            "excerpt": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways, preventing freeway breakdown and shockwave propagation during peak demand periods.",
            "status": "approved"
        },
        # Q3: MCQ (Unit 4)
        {
            "text": "Which standard and frequency band does Dedicated Short-Range Communications (DSRC) utilize for V2X safety applications?",
            "type": "mcq",
            "options": ["IEEE 802.11b at 2.4 GHz", "IEEE 802.11p in the 5.9 GHz ITS band", "IEEE 802.15.4 at 868 MHz", "3GPP Release 16 at 28 GHz"],
            "correct": "IEEE 802.11p in the 5.9 GHz ITS band",
            "model_ans": None,
            "rubric": None,
            "explanation": "DSRC is based on IEEE 802.11p operating in the licensed 5.9 GHz ITS band, providing ultra-low latency communication for safety-critical vehicle exchanges.",
            "diff": "medium",
            "marks": 2.0,
            "topic": created_topics[6],
            "excerpt": "Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters).",
            "status": "approved"
        },
        # Q4: MCQ (Unit 3)
        {
            "text": "Electronic Toll Collection systems like FASTag operate primarily in which frequency spectrum?",
            "type": "mcq",
            "options": ["Low Frequency (125-134 kHz)", "High Frequency (13.56 MHz)", "Passive UHF band (865-868 MHz)", "Microwave band (2.4-5 GHz)"],
            "correct": "Passive UHF band (865-868 MHz)",
            "model_ans": None,
            "rubric": None,
            "explanation": "Automated Electronic Toll Collection systems utilize passive UHF RFID operating in the 865-868 MHz frequency band for automated wallet debiting at highway speeds.",
            "diff": "easy",
            "marks": 2.0,
            "topic": created_topics[5],
            "excerpt": "Automated Electronic Toll Collection systems, such as FASTag, leverage Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz).",
            "status": "approved"
        },
        # Q5: MCQ (Unit 2)
        {
            "text": "What does the SCATS adaptive traffic control system stand for?",
            "type": "mcq",
            "options": ["Sydney Coordinated Adaptive Traffic System", "System for Coordinated Arterial Traffic Scheduling", "Sequential Computerized Adaptive Timing Strategy", "Synchronized Corridor Automated Traffic System"],
            "correct": "Sydney Coordinated Adaptive Traffic System",
            "model_ans": None,
            "rubric": None,
            "explanation": "SCATS stands for Sydney Coordinated Adaptive Traffic System, which dynamically adjusts signal timings based on real-time traffic saturation levels.",
            "diff": "easy",
            "marks": 2.0,
            "topic": created_topics[2],
            "excerpt": "SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets.",
            "status": "approved"
        },
        # Q6: Short Answer (Unit 1)
        {
            "text": "Explain the architectural layers of an Intelligent Transport System and discuss how traffic surveillance data flows between them.",
            "type": "short_answer",
            "options": None,
            "correct": None,
            "model_ans": "The national ITS architecture comprises physical, logical, and communication layers. The physical layer encompasses roadside sensors (inductive loops, VIPS cameras) and onboard units. The communication layer transmits raw metrics over fiber or cellular links to the logical layer situated in Traffic Management Centers, which executes coordination algorithms (such as SCATS/SCOOT) and issues real-time advisories.",
            "rubric": [
                {"criterion": "Identification of physical, logical, and communication layers", "marks": 2.0},
                {"criterion": "Explanation of roadside sensor data collection", "marks": 1.5},
                {"criterion": "Description of Traffic Management Center processing and feedback loop", "marks": 1.5}
            ],
            "explanation": "A complete answer outlines the 3-tier ITS architecture and traces sensor telemetry from roadside equipment to central controllers and commuter guidance.",
            "diff": "medium",
            "marks": 5.0,
            "topic": created_topics[0],
            "excerpt": "The national ITS architecture consists of physical, logical, and communication layers that interconnect traffic management centers, roadside field equipment, vehicles, and commuters.",
            "status": "approved"
        },
        # Q7: Short Answer (Unit 4)
        {
            "text": "Distinguish between DSRC and Cellular-V2X (C-V2X) communication technologies in terms of architecture, range, and latency.",
            "type": "short_answer",
            "options": None,
            "correct": None,
            "model_ans": "DSRC is based on IEEE 802.11p operating in the licensed 5.9 GHz band, designed for direct short-range communications (<300m) with ultra-low latency (<5ms). Conversely, C-V2X utilizes 4G/5G cellular standards, supporting direct sidelink PC5 for localized communications and Uu cellular network links for wide-area dissemination, offering higher data bandwidth and longer transmission ranges at the cost of network dependency.",
            "rubric": [
                {"criterion": "DSRC standard (IEEE 802.11p) and performance specs", "marks": 2.0},
                {"criterion": "C-V2X architecture (PC5 sidelink and cellular Uu)", "marks": 2.0},
                {"criterion": "Comparison table/contrasting summary", "marks": 1.0}
            ],
            "explanation": "Compares vehicular wireless standards across bandwidth, range, and latency benchmarks.",
            "diff": "hard",
            "marks": 5.0,
            "topic": created_topics[6],
            "excerpt": "Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters). Cellular-V2X (C-V2X) utilizes 4G LTE and 5G sidelink PC5 direct communication, providing longer range and greater bandwidth.",
            "status": "approved"
        },
        # Q8: Long Answer (Unit 2 & 4)
        {
            "text": "Provide a detailed system analysis of Cooperative Adaptive Cruise Control (CACC) and vehicle platooning. Discuss how sensor fusion and V2V communication maintain stable sub-second time gaps without compromising highway safety.",
            "type": "long_answer",
            "options": None,
            "correct": None,
            "model_ans": "Cooperative Adaptive Cruise Control (CACC) enhances conventional radar-based Adaptive Cruise Control by integrating Vehicle-to-Vehicle (V2V) wireless telemetry. While standalone ACC is constrained by sensor perception delay (often requiring 1.2 to 2.0 second headway to guarantee string stability), CACC shares instantaneous acceleration, braking intention, and trajectory vectors between lead and following vehicles via DSRC or C-V2X.\n\nKey system components include:\n1. Onboard perception (radar, lidar, and wheel encoders) measuring relative distance and closing velocity.\n2. V2V transceiver exchanging emergency deceleration triggers with zero driver reaction delay.\n3. Longitudinal platoon controller executing string-stable decentralized control laws.\n\nThis architecture enables platooning vehicles to safely compress headways down to 0.5-0.8 seconds, eliminating string shockwaves, reducing aerodynamic drag by up to 25% for trailing commercial trucks, and dramatically maximizing arterial throughput.",
            "rubric": [
                {"criterion": "Distinction between standalone ACC and cooperative CACC", "marks": 3.0},
                {"criterion": "V2V communication integration and string stability explanation", "marks": 3.0},
                {"criterion": "Safety failure modes and fallback strategies", "marks": 2.0},
                {"criterion": "Aerodynamic and throughput benefits", "marks": 2.0}
            ],
            "explanation": "Evaluates advanced CAV coordination, string stability, and aerodynamic/traffic throughput enhancements.",
            "diff": "hard",
            "marks": 10.0,
            "topic": created_topics[7],
            "excerpt": "Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.",
            "status": "approved"
        },
        # Q9: Draft Question (Awaiting Faculty Review)
        {
            "text": "How do Variable Message Signs (VMS) assist ATMS operations during unexpected freeway incidents?",
            "type": "short_answer",
            "options": None,
            "correct": None,
            "model_ans": "Variable Message Signs provide dynamic alerts regarding incident locations, recommended detours, and reduced speed advisories.",
            "rubric": [{"criterion": "Mention of incident advisories", "marks": 2.0}],
            "explanation": "VMS updates commuters en-route to divert traffic away from bottleneck corridors.",
            "diff": "easy",
            "marks": 4.0,
            "topic": created_topics[3],
            "excerpt": "Variable Message Signs (VMS) disseminate real-time advisory alerts and lane closure warnings.",
            "status": "draft"
        }
    ]

    saved_revisions: List[QuestionRevision] = []
    
    for idx, q_info in enumerate(seed_questions):
        q_id = f"q_seed_{idx+1:02d}"
        q_obj = Question(
            id=q_id,
            subject_id=its_sub.id,
            status=q_info["status"],
            is_active=True,
            is_demo_seed=True
        )
        db.add(q_obj)
        db.flush()

        rev_id = f"{q_id}_v1"
        q_obj.current_revision_id = rev_id
        
        rev = QuestionRevision(
            id=rev_id,
            question_id=q_id,
            revision_number=1,
            question_text=q_info["text"],
            question_type=q_info["type"],
            options_json=q_info["options"],
            correct_answer=q_info["correct"],
            model_answer=q_info["model_ans"],
            rubric_json=q_info["rubric"],
            explanation=q_info["explanation"],
            difficulty=q_info["diff"],
            marks=q_info["marks"],
            topic_id=q_info["topic"].id,
            topic_name=q_info["topic"].topic_name,
            unit_number=q_info["topic"].unit_number,
            source_document_id=doc.id,
            source_document_title=doc.title,
            supporting_excerpt=q_info["excerpt"],
            verified_grounding=True,
            approved_by=prof.id if q_info["status"] == "approved" else None,
            approved_at=datetime.datetime.utcnow() if q_info["status"] == "approved" else None,
            is_current=True
        )
        db.add(rev)
        db.flush()

        # Evidence link
        ev = SourceEvidence(
            revision_id=rev.id,
            document_id=doc.id,
            document_title=doc.title,
            excerpt=q_info["excerpt"],
            match_confidence=1.0,
            verified_grounding=True
        )
        db.add(ev)
        
        if q_info["status"] == "approved":
            saved_revisions.append(rev)
            
    db.flush()

    # 5. Seeded Published Paper (Mid-Term Assessment)
    published_paper = Paper(
        id="paper_its_midterm_2026",
        title="ITS-401 Mid-Term Examination 2026",
        subject_id=its_sub.id,
        status="published",
        duration_minutes=60,
        total_marks=30.0,
        instructions="1. All questions are compulsory.\n2. Figures to the right indicate full marks.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        blueprint_json={
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        },
        warnings_acknowledged=True,
        is_demo_seed=True,
        published_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    db.add(published_paper)
    db.flush()

    # Paper Sections
    sec_a = PaperSection(
        id="p_sec_a_midterm",
        paper_id=published_paper.id,
        name="Section A: Multiple Choice Questions",
        description="Answer all questions. Each carries 2 marks.",
        section_order=1,
        total_marks=10.0,
        instructions="Select the single correct alternative."
    )
    sec_b = PaperSection(
        id="p_sec_b_midterm",
        paper_id=published_paper.id,
        name="Section B: Short Answer Questions",
        description="Answer both questions concisely.",
        section_order=2,
        total_marks=10.0,
        instructions="Provide structured, technical answers."
    )
    sec_c = PaperSection(
        id="p_sec_c_midterm",
        paper_id=published_paper.id,
        name="Section C: Long Answer / System Analysis",
        description="Detailed analytical and architectural evaluation.",
        section_order=3,
        total_marks=10.0,
        instructions="Answer in depth with system architecture block diagrams."
    )
    db.add_all([sec_a, sec_b, sec_c])
    db.flush()

    # Add items to paper
    # MCQs (Q1 to Q5)
    mcq_revs = [r for r in saved_revisions if r.question_type == "mcq"][:5]
    for i, r in enumerate(mcq_revs):
        db.add(PaperItem(
            id=f"pi_midterm_a_{i+1}",
            paper_id=published_paper.id,
            section_id=sec_a.id,
            question_revision_id=r.id,
            item_order=i+1,
            marks=2.0
        ))
        
    # Short answers (Q6, Q7)
    short_revs = [r for r in saved_revisions if r.question_type == "short_answer"][:2]
    for i, r in enumerate(short_revs):
        db.add(PaperItem(
            id=f"pi_midterm_b_{i+1}",
            paper_id=published_paper.id,
            section_id=sec_b.id,
            question_revision_id=r.id,
            item_order=len(mcq_revs) + i + 1,
            marks=5.0
        ))
        
    # Long answer (Q8)
    long_revs = [r for r in saved_revisions if r.question_type == "long_answer"][:1]
    if long_revs:
        db.add(PaperItem(
            id="pi_midterm_c_1",
            paper_id=published_paper.id,
            section_id=sec_c.id,
            question_revision_id=long_revs[0].id,
            item_order=len(mcq_revs) + len(short_revs) + 1,
            marks=10.0
        ))
    db.flush()

    # 6. Seeded Draft Paper
    draft_paper = Paper(
        id="paper_its_quiz2_draft",
        title="ITS-401 Surprise Quiz 2 (Draft)",
        subject_id=its_sub.id,
        status="draft",
        duration_minutes=30,
        total_marks=10.0,
        instructions="Quick assessment on sensor and ATMS algorithms.",
        is_demo_seed=True
    )
    db.add(draft_paper)
    db.flush()

    # 7. Seeded Student Attempts
    # Attempt 1: Fully Graded (Student: Aditi Rao)
    att1 = Attempt(
        id="att_seed_aditi_graded",
        student_id=student1.id,
        paper_id=published_paper.id,
        title="ITS-401 Mid-Term Examination 2026",
        subject_id=its_sub.id,
        mode="assessment",
        status="graded",
        started_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=3),
        deadline_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=2),
        submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=2, minutes=10),
        graded_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
        total_possible_marks=30.0,
        objective_score=8.0, # 4/5 MCQs correct
        provisional_score=26.0,
        final_score=26.0,
        is_demo_seed=True
    )
    db.add(att1)
    db.flush()

    # Attempt 1 Items & Responses
    all_paper_items = db.query(PaperItem).filter(PaperItem.paper_id == published_paper.id).order_by(PaperItem.item_order).all()
    for item in all_paper_items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        snapshot = {
            "question_text": rev.question_text,
            "question_type": rev.question_type,
            "options": rev.options_json,
            "marks": item.marks,
            "topic_name": rev.topic_name,
            "unit_number": rev.unit_number,
            "correct_answer": rev.correct_answer,
            "model_answer": rev.model_answer,
            "rubric_json": rev.rubric_json,
            "explanation": rev.explanation
        }
        db.add(AttemptItem(
            attempt_id=att1.id,
            question_revision_id=rev.id,
            order_index=item.item_order,
            marks_allocated=item.marks,
            question_snapshot_json=snapshot
        ))
        
        # Responses for Aditi
        if rev.question_type == "mcq":
            is_corr = (item.item_order != 2) # Q2 wrong, others right
            ans = rev.correct_answer if is_corr else "Microwave radar sensors"
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer=ans,
                is_correct=is_corr,
                marks_awarded=2.0 if is_corr else 0.0,
                grading_status="auto_graded",
                graded_at=att1.submitted_at
            ))
        elif rev.question_type == "short_answer":
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer=f"The national ITS architecture integrates physical sensors (loops, radars) communicating with TMCs via logical software pipelines. Telemetry allows algorithms to continuously adjust signals.",
                is_correct=True,
                marks_awarded=4.5,
                grading_status="manually_graded",
                faculty_feedback="Solid understanding of architecture layers and telemetry loops. Well explained.",
                grader_id=prof.id,
                graded_at=att1.graded_at
            ))
        elif rev.question_type == "long_answer":
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer="Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.",
                is_correct=True,
                marks_awarded=9.0,
                grading_status="manually_graded",
                faculty_feedback="Excellent depth on string stability and longitudinal control algorithms.",
                grader_id=prof.id,
                graded_at=att1.graded_at
            ))
            
    # Attempt 2: Submitted & Awaiting Faculty Grading (Student: Karthik Nair)
    att2 = Attempt(
        id="att_seed_karthik_pending",
        student_id=student2.id,
        paper_id=published_paper.id,
        title="ITS-401 Mid-Term Examination 2026",
        subject_id=its_sub.id,
        mode="assessment",
        status="awaiting_grading",
        started_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
        deadline_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3),
        submitted_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3, minutes=15),
        total_possible_marks=30.0,
        objective_score=10.0, # All 5 MCQs correct
        provisional_score=10.0,
        final_score=None, # UNGRADED descriptive answers
        is_demo_seed=True
    )
    db.add(att2)
    db.flush()

    for item in all_paper_items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        snapshot = {
            "question_text": rev.question_text,
            "question_type": rev.question_type,
            "options": rev.options_json,
            "marks": item.marks,
            "topic_name": rev.topic_name,
            "unit_number": rev.unit_number,
            "correct_answer": rev.correct_answer,
            "model_answer": rev.model_answer,
            "rubric_json": rev.rubric_json,
            "explanation": rev.explanation
        }
        db.add(AttemptItem(
            attempt_id=att2.id,
            question_revision_id=rev.id,
            order_index=item.item_order,
            marks_allocated=item.marks,
            question_snapshot_json=snapshot
        ))
        
        if rev.question_type == "mcq":
            db.add(Response(
                id=f"resp_att2_{item.item_order}",
                attempt_id=att2.id,
                question_revision_id=rev.id,
                submitted_answer=rev.correct_answer,
                is_correct=True,
                marks_awarded=2.0,
                grading_status="auto_graded",
                graded_at=att2.submitted_at
            ))
        else:
            db.add(Response(
                id=f"resp_att2_{item.item_order}",
                attempt_id=att2.id,
                question_revision_id=rev.id,
                submitted_answer="DSRC uses IEEE 802.11p at 5.9GHz while C-V2X uses 3GPP cellular standard with PC5 direct sidelink.",
                is_correct=None,
                marks_awarded=None, # CRITICAL: NULL
                grading_status="pending"
            ))

    # 8. Notifications
    db.add(Notification(
        role="faculty",
        title="Grading Queue: 1 Submission Pending",
        message="Karthik Nair has submitted 'ITS-401 Mid-Term Examination 2026' with 3 descriptive answers awaiting evaluation.",
        link=f"/faculty/grading/{att2.id}"
    ))
    db.add(Notification(
        user_id=student1.id,
        role="student",
        title="Mid-Term Results Published",
        message="Your submission for 'ITS-401 Mid-Term Examination 2026' has been graded. Total Score: 26 / 30.",
        link=f"/student/attempt/{att1.id}/results"
    ))

    # 9. Record demo seed version
    db.add(DemoSeedVersion(
        version="1.0.0",
        description="Initial deterministic seed with ITS-401 course, units 1-4, questions, mid-term paper, and sample attempts."
    ))

    db.commit()

def reset_demo_workspace(db: Session):
    """
    Resets the demo workspace to its initial seeded state while preserving configuration.
    """
    seed_database(db, force=True)
