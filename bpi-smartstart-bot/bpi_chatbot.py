from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

class BPIChatbot:
    def __init__(self):
        self.responses = {
            'greet': "Hello! I'm your BPI SmartStart assistant. How can I help you with your onboarding today?",
            'system_access': """To request system access at BPI:

1. Submit a request through the IT Service Portal
2. Get approval from your direct supervisor
3. Complete security clearance if required
4. Wait for IT to provision your accounts

Typical processing time is 2-3 business days. Need help with specific systems?""",
            'benefits_payroll': """For benefits and payroll questions, contact:

- HR Benefits Team: benefits@bpi.com.ph or ext. 1234
- Payroll Department: payroll@bpi.com.ph or ext. 1235
- Your HR Business Partner for complex inquiries

They can help with health insurance, retirement plans, leave credits, and salary concerns.""",
            'leave_request': """To submit a leave request at BPI:

1. Log into the HR Self-Service portal
2. Navigate to 'Leave Management'
3. Select leave type (vacation, sick, emergency, etc.)
4. Choose your dates and add justification
5. Submit for supervisor approval
6. You'll receive email confirmation once approved

Remember to submit requests at least 2 weeks in advance for vacation leave!""",
            'workflow_status': """You'll know a workflow is complete when:

1. All tasks are marked as done
2. Final approvals (if required) are submitted
3. You receive a confirmation message or email
4. The status changes to 'Complete' in your dashboard

Check your task list or contact your supervisor if unsure about a specific workflow.""",
            'training_compliance': """BPI Training Requirements:

- AMLA Training: Annual compliance requirement
- BSP Regulations: Banking compliance modules
- Data Privacy: Mandatory certification
- System Training: Role-specific modules

Which training do you need information about?""",
            'goodbye': "Thank you for using SmartStart! If you need more help with your onboarding, just ask. Have a great day at BPI!"
        }
        
        self.patterns = {
            'greet': r'hello|hi|hey|good morning|good afternoon|greetings',
            'system_access': r'system|access|login|account|password|CBS|VPN|IT|computer|software',
            'benefits_payroll': r'benefit|payroll|salary|insurance|health|HR|retirement|medical',
            'leave_request': r'leave|vacation|sick|time off|holiday|absence|day off',
            'workflow_status': r'workflow|complete|status|progress|done|finished|tracking',
            'training_compliance': r'training|AMLA|BSP|compliance|certification|regulation|course',
            'goodbye': r'bye|goodbye|thank|thanks|see you|farewell'
        }
    
    def get_response(self, message):
        message_lower = message.lower()
        
        for intent, pattern in self.patterns.items():
            if re.search(pattern, message_lower):
                return self.responses[intent]
        
        return "I'm here to help with BPI onboarding! You can ask me about system access, benefits, leave requests, training, or workflow status. What would you like to know?"

chatbot = BPIChatbot()

@app.route('/webhooks/rest/webhook', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    response = chatbot.get_response(user_message)
    
    return jsonify([{'text': response}])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'BPI SmartStart Chatbot is running!'})

if __name__ == '__main__':
    print("🤖 BPI SmartStart Chatbot is running on http://localhost:5005")
    print("📋 Ready to help with BPI onboarding questions!")
    app.run(host='0.0.0.0', port=5005, debug=True)