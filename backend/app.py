from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import hashlib
from datetime import datetime, timedelta
import uuid
import random

app = Flask(__name__)
CORS(app)

def load_data(filename):
    """Load data from JSON file"""
    try:
        with open(f'data/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    """Save data to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open(f'data/{filename}', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_member_status(member_id, date):
    """Generate dynamic status based on member ID and date"""
    hash_input = f"{member_id}_{date}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
    
    # 70% available, 20% busy, 10% away
    if hash_value % 100 < 70:
        return 'available'
    elif hash_value % 100 < 90:
        return 'busy'
    else:
        return 'away'

def generate_member_schedule(member_id, date):
    """Generate individual member schedule for a specific date"""
    times = ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM']
    schedule = []
    
    for time in times:
        hash_input = f"{member_id}_{date}_{time}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        
        # 75% chance of being available for time slots
        available = (hash_value % 100) < 75
        meeting = None if available else f"Budget Review #{hash_value % 99 + 100}"
        
        schedule.append({
            'time': time,
            'available': available,
            'meeting': meeting
        })
    
    return schedule

def generate_team_availability_with_details(date, team_members):
    """Generate detailed team availability for a specific date"""
    times = ['9:00 AM', '10:00 AM', '11:00 AM', '2:00 PM', '3:00 PM']
    availability = []
    
    for time in times:
        available_members = []
        unavailable_members = []
        
        for member in team_members:
            member_schedule = generate_member_schedule(member['id'], date)
            time_slot = next((slot for slot in member_schedule if slot['time'] == time), None)
            
            if time_slot and time_slot['available'] and member['status'] == 'available':
                available_members.append({
                    'id': member['id'],
                    'name': member['name'],
                    'role': member['role']
                })
            else:
                reason = 'Away' if member['status'] != 'available' else (time_slot['meeting'] if time_slot and time_slot['meeting'] else 'Busy')
                unavailable_members.append({
                    'id': member['id'],
                    'name': member['name'],
                    'role': member['role'],
                    'reason': reason
                })
        
        available_count = len(available_members)
        total_members = len(team_members)
        
        if available_count <= 5:
            status = 'poor'
        elif available_count <= 8:
            status = 'limited'
        else:
            status = 'excellent'
        
        availability.append({
            'time': time,
            'availableMembers': available_members,
            'unavailableMembers': unavailable_members,
            'status': status,
            'allAvailable': available_count == total_members,
            'availableCount': available_count,
            'canScheduleTeam': available_count >= 5,
            'canScheduleSmall': available_count >= 2
        })
    
    return availability

def generate_meeting_link(title, platform='google_meet'):
    """Generate realistic meeting links"""
    import re
    
    clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())
    clean_title = clean_title.replace(' ', '-')[:15]
    
    # Add timestamp for uniqueness
    timestamp = str(int(datetime.now().timestamp()))[-6:]
    
    if platform == 'zoom':
        meeting_id = f"123{abs(hash(title)) % 10000000:07d}"
        passcode = f"{abs(hash(title + timestamp)) % 1000000:06d}"
        return {
            'url': f"https://zoom.us/j/{meeting_id}?pwd={passcode}",
            'meeting_id': meeting_id,
            'passcode': passcode
        }
    else:
        meeting_code = f"{clean_title}-{timestamp}"
        return {
            'url': f"https://meet.google.com/{meeting_code}",
            'meeting_code': meeting_code
        }

def generate_professional_agenda(title, attendee_count):
    """Generate professional meeting agenda templates"""
    
    if attendee_count == 1:
        return f"""🤖 AI-Generated Agenda for: {title}
Meeting Type: One-on-One Meeting

📋 Finance One-on-One Meeting Agenda

1. Personal Check-in (5 minutes)
   - How are things going overall?
   - Work-life balance discussion

2. Current Finance Work Discussion (15 minutes)
   - Budget analysis progress and challenges
   - Support needed from manager/colleague
   - Recent financial accomplishments

3. Professional Development (10 minutes)
   - Finance skill building opportunities
   - Career goals and certifications (CPA, CFA)
   - Training or learning needs

4. Feedback Exchange (10 minutes)
   - Performance feedback
   - Process improvement suggestions
   - Open communication

5. Action Planning (10 minutes)
   - Next steps and priorities
   - Goal setting for upcoming period
   - Resource requirements

📝 Follow-up Actions:
- [ ] Financial analysis task - Due: [Date]
- [ ] Budget review completion - Due: [Date]

💡 Meeting Tips:
- Start and end on time
- Keep discussions focused
- Encourage open communication
- Document decisions and action items"""
    
    elif 'budget' in title.lower() or 'financial' in title.lower():
        return f"""🤖 AI-Generated Agenda for: {title}
Meeting Type: Financial Planning Meeting

📋 Financial Planning Meeting Agenda

1. Budget Overview (10 minutes)
   - Current budget status and variance analysis
   - Key financial metrics and KPIs
   - Timeline adherence

2. Financial Analysis Discussion (20 minutes)
   - Revenue and expense analysis
   - Cash flow projections
   - Risk assessment and mitigation

3. Resource & Budget Review (10 minutes)
   - Department budget allocation
   - Expense approvals and adjustments
   - Cost center performance

4. Compliance & Audit (10 minutes)
   - Regulatory compliance status
   - Internal audit findings
   - Documentation requirements

5. Next Period Planning (10 minutes)
   - Upcoming financial tasks and priorities
   - Role assignments
   - Deliverable timelines

📝 Action Items:
- [ ] Budget variance report - Assigned to: [Name] - Due: [Date]
- [ ] Financial statement review - Assigned to: [Name] - Due: [Date]

💡 Meeting Tips:
- Start and end on time
- Keep discussions focused
- Ensure compliance requirements are met
- Document all financial decisions"""
    
    else:
        return f"""🤖 AI-Generated Agenda for: {title}
Meeting Type: Finance Team Meeting

📋 Finance Team Meeting Agenda

1. Opening & Check-ins (5 minutes)
   - Welcome and attendance
   - Quick status updates from team members

2. Financial Updates (15 minutes)
   - Monthly/quarterly financial status review
   - Key milestones and deliverables
   - Budget variance and challenges discussion

3. Key Discussion Points (15 minutes)
   - Strategic financial initiatives
   - Process improvements
   - Compliance and audit updates

4. Action Items & Next Steps (10 minutes)
   - Task assignments
   - Deadlines and priorities
   - Follow-up meetings if needed

5. Closing (5 minutes)
   - Questions and clarifications
   - Next meeting scheduling

📝 Action Items Template:
- [ ] Financial report preparation - Assigned to: [Name] - Due: [Date]
- [ ] Budget analysis completion - Assigned to: [Name] - Due: [Date]

💡 Meeting Tips:
- Start and end on time
- Keep discussions focused
- Ensure regulatory compliance
- Document all financial decisions and action items"""

def create_notification(type, title, message, recipient_ids=None, meeting_request_id=None):
    """Create a notification"""
    notification = {
        'id': int(datetime.now().timestamp() * 1000),
        'type': type,  # 'meeting_invite', 'meeting_update', 'meeting_reminder', 'system'
        'title': title,
        'message': message,
        'recipient_ids': recipient_ids or [],
        'meeting_request_id': meeting_request_id,
        'created_at': datetime.now().isoformat(),
        'read': False
    }
    
    # Save notification to data file
    notifications_data = load_data('notifications.json')
    if 'notifications' not in notifications_data:
        notifications_data['notifications'] = []
    
    notifications_data['notifications'].append(notification)
    save_data('notifications.json', notifications_data)
    
    return notification

def simulate_email_sending(meeting_data):
    """Enhanced email simulation with meeting links and detailed content"""
    attendees = meeting_data.get('attendees', [])
    attendee_count = len(attendees)
    meeting_link_data = meeting_data.get('meeting_link_data', {})
    
    print("\n" + "="*70)
    print("📧 BPI FINANCE DEPARTMENT MEETING INVITATION")
    print("="*70)
    print(f"📋 Meeting: {meeting_data.get('title', 'Finance Team Meeting')}")
    print(f"📅 Date: {meeting_data.get('date', 'TBD')}")
    print(f"⏰ Time: {meeting_data.get('time', 'TBD')}")
    print(f"⏱️ Duration: {meeting_data.get('duration', '30 minutes')}")
    print(f"🎥 Platform: {meeting_data.get('video_platform', 'Google Meet').title()}")
    
    # Enhanced meeting link display
    if meeting_link_data:
        print(f"🔗 Meeting Link: {meeting_link_data.get('url', 'N/A')}")
        if meeting_data.get('video_platform') == 'zoom':
            print(f"🆔 Meeting ID: {meeting_link_data.get('meeting_id', 'N/A')}")
            print(f"🔑 Passcode: {meeting_link_data.get('passcode', 'N/A')}")
        else:
            print(f"📱 Meeting Code: {meeting_link_data.get('meeting_code', 'N/A')}")
    
    print(f"👥 Finance Team Attendees ({attendee_count}): {', '.join(attendees)}")
    
    if meeting_data.get('agenda'):
        print(f"📋 Custom Agenda: {meeting_data['agenda']}")
    
    if meeting_data.get('ai_agenda'):
        print(f"\n🤖 AI-Generated Finance Agenda:\n{meeting_data['ai_agenda']}")
    
    print("="*70)
    return True

def initialize_default_data():
    """Initialize default unified employee data"""
    
    unified_employees = {
        "employees": [
            {"id": 1, "employee_id": "emp_001", "name": "Juan dela Cruz", "email": "juan.delacruz@bpi.com.ph", "position": "Finance Analyst", "role": "Finance Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-12", "status": "active", "employee_number": "BPI-2025-001", "completion": 45, "activity": "SAP Finance Module Training", "pending_items": 2, "risk_level": "medium", "last_checkin": "2025-08-22", "next_checkin": "2025-08-29", "days_since_checkin": 1, "onboarding_duration": 12, "icon": "../img/male.png"},
            {"id": 2, "employee_id": "emp_002", "name": "Maria Santos", "email": "maria.santos@bpi.com.ph", "position": "Finance Manager", "role": "Finance Manager", "department": "Finance", "manager_id": "", "start_date": "2020-01-15", "status": "active", "employee_number": "BPI-2020-001", "completion": 100, "activity": "Team Management", "pending_items": 0, "risk_level": "low", "last_checkin": "2025-08-23", "next_checkin": "2025-08-30", "days_since_checkin": 0, "onboarding_duration": 1825, "icon": "../img/female.png"},
            {"id": 3, "employee_id": "emp_003", "name": "Emma Watson", "email": "emma.watson@bpi.com.ph", "position": "Senior Financial Analyst", "role": "Senior Financial Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-01", "status": "active", "employee_number": "BPI-2025-003", "completion": 100, "activity": "Employee Handbook Review", "pending_items": 0, "risk_level": "low", "last_checkin": "2025-08-22", "next_checkin": "2025-08-29", "days_since_checkin": 1, "onboarding_duration": 23, "icon": "../img/female.png"},
            {"id": 4, "employee_id": "emp_004", "name": "Lisa Thompson", "email": "lisa.thompson@bpi.com.ph", "position": "Budget Analyst", "role": "Budget Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-05", "status": "active", "employee_number": "BPI-2025-004", "completion": 30, "activity": "SOP Review", "pending_items": 3, "risk_level": "high", "last_checkin": "2025-08-15", "next_checkin": "2025-08-22", "days_since_checkin": 8, "onboarding_duration": 19, "icon": "../img/female.png"},
            {"id": 5, "employee_id": "emp_005", "name": "James Wilson", "email": "james.wilson@bpi.com.ph", "position": "Financial Controller", "role": "Financial Controller", "department": "Finance", "manager_id": "mgr_001", "start_date": "2024-10-15", "status": "active", "employee_number": "BPI-2024-005", "completion": 100, "activity": "Monthly Financial Reporting", "pending_items": 0, "risk_level": "low", "last_checkin": "2025-08-23", "next_checkin": "2025-08-30", "days_since_checkin": 0, "onboarding_duration": 312, "icon": "../img/male.png"},
            {"id": 6, "employee_id": "emp_006", "name": "Arianna Leveau", "email": "arianna.leveau@bpi.com.ph", "position": "Accounts Payable Specialist", "role": "Accounts Payable Specialist", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-07-20", "status": "active", "employee_number": "BPI-2025-006", "completion": 85, "activity": "Vendor Management Training", "pending_items": 1, "risk_level": "low", "last_checkin": "2025-08-21", "next_checkin": "2025-08-28", "days_since_checkin": 2, "onboarding_duration": 35, "icon": "../img/female.png"},
            {"id": 7, "employee_id": "emp_007", "name": "Michael Rodriguez", "email": "michael.rodriguez@bpi.com.ph", "position": "Senior Accountant", "role": "Senior Accountant", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-08", "status": "active", "employee_number": "BPI-2025-007", "completion": 80, "activity": "Financial Reporting Training", "pending_items": 1, "risk_level": "low", "last_checkin": "2025-08-21", "next_checkin": "2025-08-28", "days_since_checkin": 2, "onboarding_duration": 16, "icon": "../img/male.png"},
            {"id": 8, "employee_id": "emp_008", "name": "Jennifer Kim", "email": "jennifer.kim@bpi.com.ph", "position": "Tax Analyst", "role": "Tax Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-03", "status": "active", "employee_number": "BPI-2025-008", "completion": 90, "activity": "Risk Assessment Training", "pending_items": 1, "risk_level": "low", "last_checkin": "2025-08-22", "next_checkin": "2025-08-29", "days_since_checkin": 1, "onboarding_duration": 21, "icon": "../img/female.png"},
            {"id": 9, "employee_id": "emp_009", "name": "David Brown", "email": "david.brown@bpi.com.ph", "position": "Payroll Specialist", "role": "Payroll Specialist", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-07-15", "status": "active", "employee_number": "BPI-2025-009", "completion": 95, "activity": "Payroll System Training", "pending_items": 0, "risk_level": "low", "last_checkin": "2025-08-22", "next_checkin": "2025-08-29", "days_since_checkin": 1, "onboarding_duration": 40, "icon": "../img/male.png"},
            {"id": 10, "employee_id": "emp_010", "name": "Sophie Turner", "email": "sophie.turner@bpi.com.ph", "position": "Accounts Receivable Specialist", "role": "Accounts Receivable Specialist", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-07-28", "status": "active", "employee_number": "BPI-2025-010", "completion": 75, "activity": "Customer Credit Analysis Training", "pending_items": 2, "risk_level": "medium", "last_checkin": "2025-08-20", "next_checkin": "2025-08-27", "days_since_checkin": 3, "onboarding_duration": 27, "icon": "../img/female.png"},
            {"id": 11, "employee_id": "emp_011", "name": "Alex Johnson", "email": "alex.johnson@bpi.com.ph", "position": "Treasury Analyst", "role": "Treasury Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-10", "status": "active", "employee_number": "BPI-2025-011", "completion": 60, "activity": "Cash Management Training", "pending_items": 2, "risk_level": "medium", "last_checkin": "2025-08-19", "next_checkin": "2025-08-26", "days_since_checkin": 4, "onboarding_duration": 14, "icon": "../img/male.png"},
            {"id": 12, "employee_id": "emp_012", "name": "Robert Kim", "email": "robert.kim@bpi.com.ph", "position": "Cost Analyst", "role": "Cost Analyst", "department": "Finance", "manager_id": "mgr_001", "start_date": "2025-08-06", "status": "active", "employee_number": "BPI-2025-012", "completion": 55, "activity": "Cost Accounting Fundamentals", "pending_items": 3, "risk_level": "medium", "last_checkin": "2025-08-18", "next_checkin": "2025-08-25", "days_since_checkin": 5, "onboarding_duration": 18, "icon": "../img/male.png"}
        ],
        "managers": {
            "mgr_001": {
                "id": "mgr_001",
                "employee_id": "emp_002",
                "name": "Maria Santos",
                "position": "Finance Manager",
                "department": "Finance",
                "employees": ["emp_001", "emp_003", "emp_004", "emp_005", "emp_006", "emp_007", "emp_008", "emp_009", "emp_010", "emp_011", "emp_012"],
                "status": "active",
                "email": "maria.santos@bpi.com.ph"
            }
        }
    }
    
    # Template meeting requests for demo
    template_meeting_requests = [
        {
            "id": "req_001",
            "from_user": "emp_001",
            "to_user": "mgr_001",
            "from_type": "employee",
            "to_type": "manager",
            "title": "SAP Training Discussion",
            "description": "Need guidance on upcoming SAP Finance module training and preparation steps",
            "proposed_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
            "priority": "MEDIUM",
            "meeting_type": "one_on_one",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "response_datetime": None,
            "response_reason": None
        },
        {
            "id": "req_002",
            "from_user": "mgr_001",
            "to_user": "emp_001",
            "from_type": "manager",
            "to_type": "employee",
            "title": "Progress Check-in",
            "description": "Weekly one-on-one to discuss onboarding progress and any support needed",
            "proposed_datetime": (datetime.now() + timedelta(days=2)).isoformat(),
            "priority": "HIGH",
            "meeting_type": "one_on_one",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "response_datetime": None,
            "response_reason": None
        },
        {
            "id": "req_003",
            "from_user": "emp_004",
            "to_user": "mgr_001",
            "from_type": "employee",
            "to_type": "manager",
            "title": "Budget Analysis Clarification",
            "description": "Questions about Q3 budget variance analysis methodology and reporting format",
            "proposed_datetime": (datetime.now() + timedelta(days=3)).isoformat(),
            "priority": "MEDIUM",
            "meeting_type": "one_on_one",
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "response_datetime": None,
            "response_reason": None
        }
    ]
    
    # Manager dashboard data
    manager_data = {
        "coaching_scripts": {
            "weekly_checkin": {
                "title": "Weekly Progress Check-in",
                "category": "Regular 1:1 Meeting",
                "description": "A structured weekly check-in to track progress and address challenges",
                "points": [
                    "Review completion rates and discuss progress since last meeting",
                    "Identify any blockers, challenges, or resource needs",
                    "Provide constructive feedback and recognition for achievements",
                    "Set clear, measurable goals for the upcoming week",
                    "Schedule follow-up meetings and define next steps"
                ],
                "suggested_questions": [
                    "How are you feeling about your current progress?",
                    "What challenges have you encountered this week?",
                    "What support do you need to complete your upcoming tasks?",
                    "Are there any training materials that would be helpful?"
                ]
            },
            "addressing_delays": {
                "title": "Addressing Delays & Blockers",
                "category": "Behind Schedule",
                "description": "Supportive approach to addressing delays without blame",
                "points": [
                    "Acknowledge delays without assigning blame - focus on solutions",
                    "Identify root causes and blocking factors preventing progress",
                    "Offer additional resources, training, or support as needed",
                    "Collaborate on realistic revised timelines and expectations",
                    "Implement more frequent check-ins and progress monitoring"
                ],
                "suggested_questions": [
                    "What specific obstacles are preventing you from completing tasks?",
                    "Would additional training or resources help you move forward?",
                    "How can we adjust the timeline to make it more manageable?",
                    "What would success look like for you this week?"
                ]
            }
        },
        "escalation_paths": [
            {
                "id": 1,
                "title": "Escalate to HR",
                "description": "Missing documents, policy clarification, or employment issues",
                "contact": "hr@bpi.com.ph",
                "response_time": "24 hours",
                "department": "Human Resources",
                "purpose": "Handle employment-related issues, missing documentation, policy questions, and personnel matters",
                "icon": "../img/Man-DB/Resume.png"
            },
            {
                "id": 2,
                "title": "IT Support",
                "description": "System access, technical issues, or software problems",
                "contact": "it.support@bpi.com.ph",
                "response_time": "2 hours",
                "department": "Information Technology",
                "purpose": "Resolve technical issues, system access problems, software installations, and IT equipment setup",
                "icon": "../img/Man-DB/Laptop.png"
            },
            {
                "id": 3,
                "title": "Compliance Review",
                "description": "Regulatory requirements, risk assessment, or audit issues",
                "contact": "compliance@bpi.com.ph",
                "response_time": "48 hours",
                "department": "Compliance & Risk",
                "purpose": "Address regulatory compliance issues, risk assessment concerns, audit requirements, and BSP-related matters",
                "icon": "../img/Man-DB/Error.png"
            },
            {
                "id": 4,
                "title": "Training Support",
                "description": "Learning materials, course access, or certification issues",
                "contact": "training@bpi.com.ph",
                "response_time": "4 hours",
                "department": "Learning & Development",
                "purpose": "Resolve training access issues, provide additional learning resources, schedule specialized training sessions",
                "icon": "../img/Man-DB/pm.png"
            }
        ],

        "escalation_history": [],
        "notifications": []
    }
    
    # Save all data
    save_data('employees.json', unified_employees)
    save_data('meeting_requests.json', {'meeting_requests': template_meeting_requests})
    save_data('meetings.json', {'meetings': [], 'requests': []})
    save_data('notifications.json', {'notifications': []})
    save_data('manager_data.json', manager_data)

# ===== UNIFIED API ROUTES =====

# Employee/Team routes
@app.route('/api/teams/members/<date>', methods=['GET'])
def get_team_members_for_date(date):
    """Get finance team members with dynamic status for a specific date"""
    data = load_data('employees.json')
    base_members = data.get('employees', [])
    
    # Generate dynamic status for each member based on the date
    members_with_status = []
    for member in base_members:
        member_copy = member.copy()
        member_copy['status'] = generate_member_status(member['id'], date)
        members_with_status.append(member_copy)
    
    return jsonify(members_with_status)

@app.route('/api/schedules/team/<date>', methods=['GET'])
def get_team_availability(date):
    """Get detailed finance team availability for a specific date"""
    data = load_data('employees.json')
    base_members = data.get('employees', [])
    
    # Generate dynamic status for each member
    team_members = []
    for member in base_members:
        member_copy = member.copy()
        member_copy['status'] = generate_member_status(member['id'], date)
        team_members.append(member_copy)
    
    # Generate detailed team availability
    availability = generate_team_availability_with_details(date, team_members)
    return jsonify(availability)

@app.route('/api/schedules/member/<int:member_id>/<date>', methods=['GET'])
def get_member_schedule(member_id, date):
    """Get individual finance member schedule for a specific date"""
    schedule = generate_member_schedule(member_id, date)
    return jsonify(schedule)

# Meeting routes
@app.route('/api/meetings', methods=['POST'])
def create_meeting():
    """Create a new finance meeting with enhanced AI and email features"""
    meeting_data = request.json
    
    # Validate required fields
    if not meeting_data.get('title'):
        return jsonify({'success': False, 'error': 'Meeting title is required'}), 400
    
    if not meeting_data.get('attendees'):
        return jsonify({'success': False, 'error': 'Attendees are required'}), 400
    
    # Generate AI agenda if requested
    if meeting_data.get('use_ai'):
        attendee_count = len(meeting_data.get('attendees', []))
        enhanced_agenda = generate_professional_agenda(
            meeting_data.get('title', ''),
            attendee_count
        )
        meeting_data['ai_agenda'] = enhanced_agenda
    
    # Generate meeting link with detailed info
    video_platform = meeting_data.get('video_platform', 'google_meet')
    meeting_link_data = generate_meeting_link(meeting_data.get('title', ''), video_platform)
    meeting_data['meeting_link_data'] = meeting_link_data
    meeting_data['meeting_link'] = meeting_link_data['url']
    meeting_data['video_platform'] = video_platform
    
    # Create notification for attendees
    attendee_ids = meeting_data.get('attendeeIds', [])
    notification = create_notification(
        'meeting_invite',
        f'Finance Meeting: {meeting_data.get("title")}',
        f'You have been invited to "{meeting_data.get("title")}" on {meeting_data.get("date")} at {meeting_data.get("time")}',
        attendee_ids
    )
    
    # Simulate email sending with enhanced content
    email_result = simulate_email_sending(meeting_data)
    
    # Save meeting
    meetings = load_data('meetings.json')
    meeting_data['id'] = len(meetings.get('meetings', [])) + 1
    meeting_data['created_at'] = datetime.now().isoformat()
    meeting_data['notification_id'] = notification['id']
    
    if 'meetings' not in meetings:
        meetings['meetings'] = []
    meetings['meetings'].append(meeting_data)
    save_data('meetings.json', meetings)
    
    return jsonify({
        'success': True,
        'meeting': meeting_data,
        'email_sent': email_result,
        'ai_agenda': meeting_data.get('ai_agenda'),
        'meeting_link_data': meeting_link_data,
        'notification': notification
    })

# Meeting request routes
@app.route('/api/meeting/request', methods=['POST'])
def create_meeting_request():
    """Create a meeting request (employee to manager or manager to employee)"""
    data = request.json
    
    # Generate unique ID
    request_id = str(uuid.uuid4())
    
    meeting_request = {
        'id': request_id,
        'from_user': data.get('from_user'),
        'to_user': data.get('to_user'),
        'from_type': data.get('from_type', 'employee'),
        'to_type': data.get('to_type', 'manager'),
        'title': data.get('title'),
        'description': data.get('description'),
        'proposed_datetime': data.get('proposed_datetime'),
        'priority': data.get('priority', 'MEDIUM'),
        'meeting_type': data.get('meeting_type', 'one_on_one'),
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'response_datetime': None,
        'response_reason': None
    }
    
    # Save meeting request
    meeting_requests_data = load_data('meeting_requests.json')
    if 'meeting_requests' not in meeting_requests_data:
        meeting_requests_data['meeting_requests'] = []
    
    meeting_requests_data['meeting_requests'].append(meeting_request)
    save_data('meeting_requests.json', meeting_requests_data)
    
    # Create notification for recipient
    create_notification(
        'meeting_request',
        f'New Meeting Request: {meeting_request["title"]}',
        f'Meeting request from {meeting_request["from_user"]}: {meeting_request["description"]}',
        [meeting_request['to_user']],
        request_id
    )
    
    print(f"\n📧 MEETING REQUEST SENT")
    print(f"From: {meeting_request['from_user']} ({meeting_request['from_type']})")
    print(f"To: {meeting_request['to_user']} ({meeting_request['to_type']})")
    print(f"Title: {meeting_request['title']}")
    print(f"Time: {meeting_request['proposed_datetime']}")
    print(f"Priority: {meeting_request['priority']}")
    
    return jsonify({'success': True, 'meeting_request': meeting_request})

@app.route('/api/meeting/request/<request_id>/respond', methods=['POST'])
def respond_to_meeting_request(request_id):
    """Respond to a meeting request (accept/decline)"""
    data = request.json
    response = data.get('response')
    reason = data.get('reason', '')
    
    # Load meeting requests
    meeting_requests_data = load_data('meeting_requests.json')
    meeting_requests = meeting_requests_data.get('meeting_requests', [])
    
    # Find and update the request
    request_found = False
    for req in meeting_requests:
        if req['id'] == request_id:
            req['status'] = response
            req['response_datetime'] = datetime.now().isoformat()
            req['response_reason'] = reason
            request_found = True
            
            # Create notification for requester
            create_notification(
                'meeting_response',
                f'Meeting Request {response.title()}',
                f'Your meeting request "{req["title"]}" has been {response}' + (f': {reason}' if reason else ''),
                [req['from_user']],
                request_id
            )
            
            print(f"\n📧 MEETING REQUEST RESPONSE")
            print(f"Request: {req['title']}")
            print(f"Response: {response.upper()}")
            print(f"Reason: {reason}")
            
            break
    
    if not request_found:
        return jsonify({'success': False, 'error': 'Meeting request not found'}), 404
    
    save_data('meeting_requests.json', meeting_requests_data)
    return jsonify({'success': True})

# Employee roadmap routes
@app.route('/api/employee/<employee_id>/roadmap', methods=['GET'])
def get_employee_roadmap(employee_id):
    """Get dynamic roadmap for employee"""
    
    # Enhanced roadmap data with proper task access logic
    roadmap_data = {
        'employee': {
            'id': employee_id,
            'name': 'Juan dela Cruz',
            'position': 'Finance Analyst',
            'department': 'Finance'
        },
        'overall_progress': 45,
        'stats': {
            'completed_tasks': 5,
            'in_progress_tasks': 3,
            'overdue_tasks': 1,
            'upcoming_tasks': 8
        },
        'phases': {
            'critical_documentation': {
                'title': 'Critical Documentation Phase',
                'status': 'in_progress',
                'completion_percentage': 60,
                'tasks': [
                    {
                        'task_id': 'task_001',
                        'title': 'Submit NBI Clearance',
                        'description': 'Obtain and submit valid NBI Clearance certificate',
                        'status': 'completed',
                        'priority': 'HIGH',
                        'deadline': (datetime.now() + timedelta(days=7)).isoformat(),
                        'estimated_time': 240,
                        'progress': 100,
                        'category': 'Documentation',
                        'blocking_tasks': []
                    },
                    {
                        'task_id': 'task_002',
                        'title': 'TIN Application',
                        'description': 'Apply for Tax Identification Number at BIR',
                        'status': 'in_progress',
                        'priority': 'HIGH',
                        'deadline': (datetime.now() + timedelta(days=10)).isoformat(),
                        'estimated_time': 180,
                        'progress': 70,
                        'category': 'Legal Requirements',
                        'blocking_tasks': [],
                        'ai_scheduling': {
                            'reasoning': 'BIR visits are most efficient on Tuesday-Thursday, 9-11 AM to avoid crowds'
                        }
                    }
                ]
            },
            'finance_training': {
                'title': 'Finance Training Phase',
                'status': 'available',
                'completion_percentage': 20,
                'tasks': [
                    {
                        'task_id': 'task_003',
                        'title': 'SAP Finance Module Training',
                        'description': '5-day comprehensive SAP training for finance operations',
                        'status': 'in_progress',
                        'priority': 'MEDIUM',
                        'deadline': (datetime.now() + timedelta(days=21)).isoformat(),
                        'estimated_time': 2400,
                        'progress': 20,
                        'category': 'Finance Training',
                        'blocking_tasks': []
                    },
                    {
                        'task_id': 'task_004',
                        'title': 'BSP Compliance Training',
                        'description': 'Banking regulations and compliance requirements training',
                        'status': 'pending',
                        'priority': 'MEDIUM',
                        'deadline': (datetime.now() + timedelta(days=28)).isoformat(),
                        'estimated_time': 480,
                        'progress': 0,
                        'category': 'Finance Training',
                        'blocking_tasks': []
                    }
                ]
            },
            'work_assignments': {
                'title': 'Work Assignments Phase',
                'status': 'available',
                'completion_percentage': 10,
                'tasks': [
                    {
                        'task_id': 'task_005',
                        'title': 'Q3 Budget Analysis Project',
                        'description': 'Mentored project analyzing Q3 budget variance and trends',
                        'status': 'pending',
                        'priority': 'MEDIUM',
                        'deadline': (datetime.now() + timedelta(days=35)).isoformat(),
                        'estimated_time': 1200,
                        'progress': 10,
                        'category': 'Work Assignment',
                        'blocking_tasks': []
                    }
                ]
            }
        },
        'ai_insights': [
            {
                'type': 'urgent',
                'title': 'Priority Task Alert',
                'message': 'TIN Application deadline approaching. Schedule BIR visit within 3 days.'
            },
            {
                'type': 'positive',
                'title': 'Great Progress!',
                'message': 'You\'re ahead of schedule on documentation requirements.'
            },
            {
                'type': 'info',
                'title': 'Training Available',
                'message': 'SAP training and work assignments are accessible even while completing documentation.'
            }
        ],
        'next_recommended_task': {
            'task_id': 'task_002',
            'title': 'TIN Application',
            'instructions': 'Visit BIR office Tuesday-Thursday morning for fastest service'
        }
    }
    
    return jsonify(roadmap_data)

@app.route('/api/employee/<employee_id>/task/<task_id>/update', methods=['POST'])
def update_task_status(employee_id, task_id):
    """Update task status for employee"""
    data = request.json
    status = data.get('status')
    progress = data.get('progress', 100 if status == 'completed' else 0)
    
    # Create notification for task completion
    if status == 'completed':
        create_notification(
            'task_completed',
            'Task Completed',
            f'Task {task_id} has been completed',
            [employee_id]
        )
    
    return jsonify({'success': True, 'task_id': task_id, 'status': status, 'progress': progress})

@app.route('/api/employee/<employee_id>/meeting-requests', methods=['GET'])
def get_employee_meeting_requests(employee_id):
    """Get meeting requests for an employee"""
    meeting_requests_data = load_data('meeting_requests.json')
    all_requests = meeting_requests_data.get('meeting_requests', [])
    
    # Filter requests for this employee (sent to them or sent by them)
    employee_requests = [
        req for req in all_requests 
        if req.get('from_user') == employee_id or req.get('to_user') == employee_id
    ]
    
    # Sort by created_at (most recent first)
    employee_requests.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({'meeting_requests': employee_requests})

# Notification routes
@app.route('/api/user/<user_id>/notifications', methods=['GET'])
def get_user_notifications(user_id):
    """Get notifications for a user"""
    notifications_data = load_data('notifications.json')
    all_notifications = notifications_data.get('notifications', [])
    
    # Filter notifications for this user
    user_notifications = [
        notif for notif in all_notifications 
        if user_id in notif.get('recipient_ids', []) or not notif.get('recipient_ids')
    ]
    
    # Sort by created_at (most recent first)
    user_notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    unread_count = len([n for n in user_notifications if not n.get('read', False)])
    
    return jsonify({
        'notifications': user_notifications[:20],
        'unread_count': unread_count
    })

@app.route('/api/user/<user_id>/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(user_id, notification_id):
    """Mark a notification as read"""
    notifications_data = load_data('notifications.json')
    notifications = notifications_data.get('notifications', [])
    
    for notification in notifications:
        if notification['id'] == notification_id:
            notification['read'] = True
            break
    
    save_data('notifications.json', notifications_data)
    return jsonify({'success': True})

# Manager dashboard routes
@app.route('/api/manager/dashboard/overview', methods=['GET'])
def get_dashboard_overview():
    """Get enhanced dashboard overview statistics"""
    try:
        employees_data = load_data('employees.json')
        team_members = employees_data.get('employees', [])
        
        # Filter out the manager herself
        team_members = [m for m in team_members if m.get('position') != 'Finance Manager']
        
        active_new_hires = len([m for m in team_members if m.get("status") == "active" and m.get("completion", 0) < 100])
        require_attention = len([m for m in team_members if m.get("risk_level") == "high"])
        completion_rate = round(sum(m.get("completion", 0) for m in team_members) / len(team_members)) if team_members else 0
        overdue_count = len([m for m in team_members if m.get("status") == "Overdue" or m.get("risk_level") == "high"])
        
        # Get recent escalations
        manager_data = load_data('manager_data.json')
        escalation_history = manager_data.get("escalation_history", [])
        recent_escalations = len([e for e in escalation_history 
                                if datetime.fromisoformat(e.get("created_at", "2025-08-01T00:00:00")) > datetime.now() - timedelta(days=7)])
        
        return jsonify({
            "active_new_hires": active_new_hires,
            "require_attention": require_attention,
            "completion_rate": completion_rate,
            "overdue_count": overdue_count,
            "recent_escalations": recent_escalations,
            "total_team_members": len(team_members)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to load overview: {str(e)}"}), 500

@app.route('/api/manager/analytics', methods=['GET'])
def get_analytics():
    """Get comprehensive analytics data"""
    try:
        employees_data = load_data('employees.json')
        team_members = employees_data.get('employees', [])
        
        # Filter out the manager
        team_members = [m for m in team_members if m.get('position') != 'Finance Manager']
        total_members = len(team_members)
        
        if total_members == 0:
            return jsonify({
                "completion_rates": {
                    "overall": 0,
                    "on_schedule": 0,
                    "at_risk": 0,
                    "overdue_tasks": 0
                },
                "team_metrics": {
                    "total_members": 0,
                    "completed": 0,
                    "in_progress": 0,
                    "overdue": 0
                }
            })
        
        # Calculate status counts
        completed_count = len([m for m in team_members if m.get("completion", 0) == 100])
        in_progress_count = len([m for m in team_members if 0 < m.get("completion", 0) < 100])
        overdue_count = len([m for m in team_members if m.get("risk_level") == "high"])
        
        # Calculate risk levels
        high_risk_count = len([m for m in team_members if m.get("risk_level") == "high"])
        medium_risk_count = len([m for m in team_members if m.get("risk_level") == "medium"])
        low_risk_count = len([m for m in team_members if m.get("risk_level") == "low"])
        
        # Calculate overall completion rate
        total_completion = sum(m.get("completion", 0) for m in team_members)
        overall_completion = round(total_completion / total_members)
        
        # Calculate percentages for dashboard metrics
        on_schedule = round((completed_count + low_risk_count) / total_members * 100)
        at_risk = round(medium_risk_count / total_members * 100)
        overdue_tasks = round(high_risk_count / total_members * 100)
        
        return jsonify({
            "completion_rates": {
                "overall": overall_completion,
                "on_schedule": on_schedule,
                "at_risk": at_risk,
                "overdue_tasks": overdue_tasks
            },
            "team_metrics": {
                "total_members": total_members,
                "completed": completed_count,
                "in_progress": in_progress_count,
                "overdue": overdue_count,
                "high_risk": high_risk_count,
                "medium_risk": medium_risk_count,
                "low_risk": low_risk_count
            }
        })
        
    except Exception as e:
        print(f"Analytics error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/manager/team/performance', methods=['GET'])
def get_team_performance():
    """Get team performance data with filtering"""
    try:
        search_query = request.args.get('search', '').lower()
        status_filter = request.args.get('status', '')
        
        employees_data = load_data('employees.json')
        team_members = employees_data.get('employees', [])
        
        # Filter out the manager
        team_members = [m for m in team_members if m.get('position') != 'Finance Manager']
        
        # Apply search filter
        if search_query:
            team_members = [
                member for member in team_members 
                if search_query in member.get("name", "").lower() or 
                   search_query in member.get("position", "").lower() or
                   search_query in member.get("activity", "").lower()
            ]
        
        # Apply status filter
        if status_filter:
            if status_filter == "Complete":
                team_members = [m for m in team_members if m.get("completion", 0) == 100]
            elif status_filter == "In Progress":
                team_members = [m for m in team_members if 0 < m.get("completion", 0) < 100]
            elif status_filter == "Overdue":
                team_members = [m for m in team_members if m.get("risk_level") == "high"]
        
        # Convert completion to status for display
        for member in team_members:
            if member.get("completion", 0) == 100:
                member["status"] = "Complete"
            elif member.get("risk_level") == "high":
                member["status"] = "Overdue"
            else:
                member["status"] = "In Progress"
        
        return jsonify(team_members)
    except Exception as e:
        return jsonify({"error": f"Failed to load team performance: {str(e)}"}), 500

@app.route('/api/manager/coaching/scripts', methods=['GET'])
def get_coaching_scripts():
    """Get all AI-generated coaching scripts"""
    try:
        manager_data = load_data('manager_data.json')
        return jsonify(manager_data.get("coaching_scripts", {}))
    except Exception as e:
        return jsonify({"error": f"Failed to load coaching scripts: {str(e)}"}), 500

@app.route('/api/manager/coaching/scripts/<script_type>', methods=['GET'])
def get_specific_coaching_script(script_type):
    """Get a specific coaching script by type with detailed guidance"""
    try:
        manager_data = load_data('manager_data.json')
        scripts = manager_data.get("coaching_scripts", {})
        script = scripts.get(script_type)
        if script:
            return jsonify(script)
        return jsonify({"error": "Script not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to load script: {str(e)}"}), 500

@app.route('/api/manager/escalations', methods=['GET'])
def get_escalation_paths():
    """Get available escalation paths"""
    try:
        manager_data = load_data('manager_data.json')
        return jsonify(manager_data.get("escalation_paths", []))
    except Exception as e:
        return jsonify({"error": f"Failed to load escalation paths: {str(e)}"}), 500

@app.route('/api/manager/escalations', methods=['POST'])
def create_escalation():
    """Create a new escalation"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        escalation_type = data.get('type')
        employee_id = data.get('employee_id')
        reason = data.get('reason', '')
        urgency = data.get('urgency', 'medium')
        
        if not escalation_type or not employee_id:
            return jsonify({"error": "Missing required fields"}), 400
        
        # Load manager data
        manager_data = load_data('manager_data.json')
        escalation_paths = manager_data.get("escalation_paths", [])
        
        # Find the escalation path
        escalation_path = next(
            (ep for ep in escalation_paths if ep["title"] == escalation_type), 
            None
        )
        
        if not escalation_path:
            return jsonify({"error": "Escalation type not found"}), 404
        
        # Find the employee
        employees_data = load_data('employees.json')
        employees = employees_data.get('employees', [])
        employee = next(
            (emp for emp in employees if emp["id"] == employee_id), 
            None
        )
        
        if not employee:
            return jsonify({"error": "Employee not found"}), 404
        
        # Generate escalation reference
        reference_id = f"ESC-{random.randint(10000, 99999)}"
        
        # Create escalation record
        escalation_record = {
            "id": str(uuid.uuid4()),
            "reference_id": reference_id,
            "type": escalation_type,
            "employee_id": employee_id,
            "employee_name": employee["name"],
            "reason": reason,
            "urgency": urgency,
            "created_at": datetime.now().isoformat(),
            "status": "Open",
            "assigned_to": escalation_path["department"],
            "contact": escalation_path["contact"],
            "response_time": escalation_path["response_time"]
        }
        
        # Add to escalation history
        if "escalation_history" not in manager_data:
            manager_data["escalation_history"] = []
        
        manager_data["escalation_history"].append(escalation_record)
        save_data('manager_data.json', manager_data)
        
        return jsonify({
            "success": True,
            "message": f"Escalation to {escalation_type} created successfully",
            "reference_id": reference_id,
            "escalation": escalation_record
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/manager/escalations/history', methods=['GET'])
def get_escalation_history():
    """Get escalation history"""
    try:
        manager_data = load_data('manager_data.json')
        history = manager_data.get("escalation_history", [])
        # Sort by creation date (most recent first)
        history.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jsonify(history[:20])  # Return last 20
    except Exception as e:
        return jsonify({"error": f"Failed to load escalation history: {str(e)}"}), 500

@app.route('/api/manager/notifications', methods=['GET'])
def get_manager_notifications():
    """Get recent notifications for manager"""
    try:
        employees_data = load_data('employees.json')
        team_members = employees_data.get('employees', [])
        
        # Filter out the manager
        team_members = [m for m in team_members if m.get('position') != 'Finance Manager']
        
        # Generate notifications based on team data
        notifications = []
        
        # High-risk employees
        high_risk_members = [m for m in team_members if m.get("risk_level") == "high"]
        for member in high_risk_members:
            notifications.append({
                "id": f"notif-{member['id']}-risk",
                "title": "High-Risk Employee Alert",
                "message": f"{member['name']} requires immediate attention - {member.get('pending_items', 0)} pending items",
                "time": "2 hours ago",
                "type": "warning",
                "read": False
            })
        
        # Completions
        completed_members = [m for m in team_members if m.get("completion", 0) >= 90 and m.get("completion", 0) < 100]
        for member in completed_members:
            notifications.append({
                "id": f"notif-{member['id']}-completion",
                "title": "Near Completion",
                "message": f"{member['name']} is at {member.get('completion', 0)}% completion",
                "time": "1 day ago",
                "type": "success",
                "read": False
            })
        
        return jsonify(notifications[:10])
    except Exception as e:
        return jsonify({"error": f"Failed to load notifications: {str(e)}"}), 500

# Statistics routes
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get finance dashboard statistics"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Get team members for today
    employees_data = load_data('employees.json')
    base_members = employees_data.get('employees', [])
    
    # Generate dynamic status
    available_count = 0
    busy_count = 0
    away_count = 0
    
    for member in base_members:
        status = generate_member_status(member['id'], today)
        if status == 'available':
            available_count += 1
        elif status == 'busy':
            busy_count += 1
        else:
            away_count += 1
    
    # Get meeting requests and notifications
    meeting_requests_data = load_data('meeting_requests.json')
    notifications_data = load_data('notifications.json')
    
    pending_requests = len([req for req in meeting_requests_data.get('meeting_requests', []) 
                           if req.get('status') == 'pending'])
    
    unread_notifications = len([notif for notif in notifications_data.get('notifications', [])
                               if not notif.get('read', False)])
    
    return jsonify({
        'total_members': len(base_members),
        'available_members': available_count,
        'busy_members': busy_count,
        'away_members': away_count,
        'pending_requests': pending_requests,
        'unread_notifications': unread_notifications
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    employees_data = load_data('employees.json')
    manager_data = load_data('manager_data.json')
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0 - Unified Backend",
        "employees": len(employees_data.get('employees', [])),
        "escalation_paths": len(manager_data.get('escalation_paths', []))
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure data directory exists and initialize default data
    os.makedirs('data', exist_ok=True)
    
    # Initialize default data files if they don't exist
    required_files = ['employees.json', 'meetings.json', 'notifications.json', 'meeting_requests.json', 'manager_data.json']
    if not all(os.path.exists(f'data/{file}') for file in required_files):
        print("🔧 Initializing BPI Finance Department unified data...")
        initialize_default_data()
    
    print("🚀 BPI SmartStart - Unified Backend System")
    print("=" * 60)
    print("🏦 Bank of the Philippine Islands")
    print("📄 Unified Backend Server: http://localhost:5000")
    print("💰 Finance Department Focus")
    print("🔄 All functions integrated into single backend")
    
    app.run(debug=True, port=5000, host='0.0.0.0')