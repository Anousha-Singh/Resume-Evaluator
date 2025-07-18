# Resume Evaluator

An AI-powered resume evaluation tool that analyzes resumes against job descriptions and provides comprehensive feedback to help job seekers improve their applications.

## 🚀 Features

- PDF Resume Processing: Extract text from PDF resumes using advanced parsing
- AI-Powered Analysis: Leverages OpenAI GPT-4 for intelligent evaluation
- Comprehensive Scoring: Overall match score, experience alignment, and education fit
- Detailed Feedback: Strengths, weaknesses, and actionable recommendations
- Skill Matching: Analyze technical and soft skills alignment with job requirements

## 🛠️ Tech Stack

### Backend
**FastAPI**, **PyPDF2**, **OpenAI API**

### Frontend
**Next.js**, **TypeScript**, **Tailwind CSS**

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/resume-evaluator.git
cd resume-evaluator
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

# Run the server by either running the main.py file or using:
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
# Open a new terminal window
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```