# smartstart
# BPI Finance Onboarding System - SmartStart

A comprehensive onboarding and management system for BPI Finance Department with AI-powered features, dynamic roadmaps, and meeting orchestration.

## 🚀 Features

- **Employee Dynamic Roadmap**: AI-powered onboarding roadmap with real-time progress tracking
- **Manager Dashboard**: Team performance analytics, coaching scripts, and escalation management
- **Meeting Orchestration**: Smart scheduling with team availability visualization
- **AI Assistant**: Conversational interface for onboarding guidance
- **Real-time Notifications**: Meeting requests and system alerts

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## 🛠️ Installation & Setup
1. **Install Python dependencies**
   ```bash
   pip install flask flask-cors
   ```

## 🏃‍♂️ Running the Application

1. **Start the backend server**
   ```bash
   python app.py
   ```
   You should see output indicating the server is running on `http://localhost:5000`

2. **Open the frontend in your browser**
   - In the terminal, you can open the landing pages first. Or you can directly open it in your browser.

4. **Access the system health check**
   - Visit `http://localhost:5000/api/health` to verify the backend is working

## 💡 Usage Tips

1. The system uses simulated data that resets when the server restarts
2. Click the AI assistant button in the employee dashboard for guidance
3. Use the calendar view in Meeting Orchestration to see team availability
4. Managers can generate coaching scripts for team members from their dashboard
5. The system automatically creates meeting links for Google Meet and Zoom

## 🐛 Troubleshooting

- If images don't load, check that the `img/` folder exists with all required images
- If API calls fail, ensure the backend server is running on port 5000
- Clear your browser cache if you experience display issues
- Check the browser console (F12) for any error messages

---

**Powered by SmartStart — A BPI Innovation**
