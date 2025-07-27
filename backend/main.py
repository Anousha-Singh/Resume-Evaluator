from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import io
from typing import Optional
from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import pdfplumber


load_dotenv()

app = FastAPI(title="Resume Evaluator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


apikey = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=apikey)


class EvaluationResponse(BaseModel):
    overall_score: float
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]
    skill_match: dict
    experience_match: float
    education_match: float
    certification: list[str]
    detailed_analysis: str
    fit_assessment: dict 
    social_media_links: dict

# --- PDF Text Extraction ---
def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    try:
        pdf_content = pdf_file.file.read()
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        if not pdf_reader.pages:
            raise HTTPException(status_code=400, detail="The PDF file is empty or unreadable.")

        text = ""
        for page_number, page in enumerate(pdf_reader.pages, start=1):
            page_text = page.extract_text()
            if page_text is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unable to extract text from page {page_number}. This may be a scanned or image-based PDF. Please upload a text-based PDF."
                )
            text += page_text + "\n"
        
        return text.strip()

    except PyPDF2.errors.PdfReadError:
        raise HTTPException(status_code=400, detail="Failed to read the PDF. Make sure it's a valid, non-corrupted PDF file.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error extracting PDF text: {str(e)}")


def extract_hyperlinks(pdf_file: UploadFile) -> List[str]:
    urls = []

    # Use the file object from UploadFile directly
    with pdfplumber.open(pdf_file.file) as pdf:
        for page in pdf.pages:
            # Extract annotations from the page (where links reside)
            if hasattr(page, "annots") and page.annots:
                for annot in page.annots:
                    uri = annot.get("uri")
                    if uri:
                        urls.append(uri)

            # Fallback: check for annotations in the raw object structure
            if "annots" in page.objects:
                for obj in page.objects["annots"]:
                    if isinstance(obj, dict) and obj.get("uri"):
                        urls.append(obj["uri"])

    print(f"Extracted URLs: {urls}")
    return urls



# --- Prompt ---
def create_evaluation_prompt(resume_text: str, job_description: str, urls:List) -> str:
    prompt = f"""
    Evaluate the following resume based on the criteria listed below. Your assessment should be thorough, structured, and aligned with the job description.

    Please consider the following parameters:
    - Professional experience: relevance, depth, and alignment with the job description.
    - Skill set: both technical and soft skills, and their match with required skills.
    - Educational background: relevance and level of education.
    - Certifications: domain-specific and value-adding certifications.
    - Strengths: highlight strong points that support the candidate’s fit for the role.

    JOB DESCRIPTION:
    {job_description}

    RESUME CONTENT:
    {resume_text}

    social media links: {urls}
    Add all links related to the candidate's professional profile, such as mail address, LinkedIn, GitHub, or personal websites.

    --- OUTPUT FORMAT ---
    {{
        "overall_score": <precise_score_0_to_100>,
        "strengths": [...],
        "weaknesses": [...],
        "recommendations": [...],
        "skill_match": {{...}},
        "experience_match": <precise_score_0_to_100>,
        "education_match": <precise_score_0_to_100>,
        "certification": [...] ,
        "detailed_analysis": "...",
        "fit_assessment": {{
            "role_fit": "Excellent/Good/Fair/Poor",
            "experience_level_match": "Senior/Mid/Junior/Entry",
            "skill_level_assessment": "Above expectations/Meets requirements/Below requirements"
        }}
        "social_media_links": {{"platform_name": "link"}}
    }}
    """
    return prompt

# --- AI Evaluation ---
async def evaluate_with_ai(resume_text: str, job_description: str, urls: List) -> dict:
    try:
        prompt = create_evaluation_prompt(resume_text, job_description, urls)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert HR professional and resume evaluator. You must:
                    1. Always respond with valid JSON format
                    2. Be consistent in your evaluations - identical inputs should yield identical outputs
                    3. Use the full 0-100 scoring range appropriately
                    4. Provide specific, detailed, and actionable feedback
                    5. Include concrete examples and evidence"""
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.1,
            seed=42
        )

        evaluation_result = json.loads(response.choices[0].message.content)

        required_fields = ["overall_score", "strengths", "weaknesses", "recommendations",
                           "skill_match", "experience_match", "education_match","certification",
                           "detailed_analysis", "fit_assessment", "social_media_links"] 

        for field in required_fields:
            if field not in evaluation_result:
                raise ValueError(f"Missing required field: {field}")

        return evaluation_result

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON response from AI: {str(e)}")
    except Exception as e:
        return {
            "overall_score": 75.0,
            "strengths": [
                "Professional resume presentation and structure",
                "Relevant work experience demonstrated",
                "Clear communication of background and skills",
                "Appropriate career progression shown"
            ],
            "weaknesses": [
                "Limited quantifiable achievements provided",
                "Skills section could be more detailed",
                "Could benefit from more specific examples"
            ],
            "recommendations": [
                "Add specific metrics and quantifiable results to achievements",
                "Expand technical skills section with proficiency levels",
                "Include more project-specific details and outcomes",
                "Consider adding relevant certifications or training"
            ],
            "skill_match": {
                "General Skills": "70%",
                "Technical Skills": "65%",
                "Communication": "75%"
            },
            "experience_match": 75.0,
            "education_match": 80.0,
            "certification": ["None"],
            "detailed_analysis": f"Evaluation system encountered an error: {str(e)}. This is a fallback assessment. The candidate shows basic qualifications for the role with room for improvement in demonstrating specific achievements and technical expertise.",
            "fit_assessment": {
                "role_fit": "Good",
                "experience_level_match": "Mid",
                "skill_level_assessment": "Meets requirements"
            },
            "social_media_links": {
                "empty": "No social media links provided"
            }

        }

# --- Endpoint ---
@app.post("/evaluate-resume", response_model=EvaluationResponse)
async def evaluate_resume(
    job_description: str = Form(...),
    resume_file: UploadFile = File(...)
):
    if not resume_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    resume_text = extract_text_from_pdf(resume_file)
    urls = extract_hyperlinks(resume_file)

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF. Please ensure it is a text-based PDF.")

    evaluation_result = await evaluate_with_ai(resume_text, job_description, urls)
    return EvaluationResponse(**evaluation_result)


@app.get("/")
async def root():
    return {
        "message": "Enhanced Resume Evaluator API",
        "version": "2.0.0",
        "features": [
            "Consistent scoring across multiple evaluations",
            "Detailed technical skill assessment",
            "Comprehensive feedback with specific examples",
            "Full 0-100 scoring range utilization",
            "Enhanced prompting for better AI responses",
            "Structured fit assessment including role and skill match"
        ],
        "endpoints": {
            "evaluate": "/evaluate-resume",
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)


"""
Sample job description:

 We are looking for a Python Backend Developer with 1–3 years of experience to join our remote team. 
 The ideal candidate should have hands-on experience with Python, FastAPI or Flask, and working with relational databases like SQL. 
 Proficiency with version control systems such as Git is essential. 
 Familiarity with Docker and basic knowledge of cloud platforms like AWS is a plus. 
 The role involves developing and maintaining scalable APIs, collaborating with frontend developers, and writing clean, testable code. 
    
"""

"""
 --- DETAILED SCORING FRAMEWORK ---
    
    OVERALL SCORE CALCULATION (0-100):
    - 95-100: EXCEPTIONAL - Exceeds all requirements, demonstrates exceptional qualifications, leadership, and achievements that go beyond the job scope
    - 90-94: EXCELLENT - Meets all requirements excellently, strong relevant experience, impressive achievements, minimal gaps
    - 85-89: VERY GOOD - Meets most requirements well, good relevant experience, solid achievements, minor gaps in non-critical areas
    - 80-84: GOOD - Meets majority of requirements, adequate experience, some achievements, few gaps in secondary requirements
    - 75-79: ABOVE AVERAGE - Meets core requirements, relevant experience present, limited achievements, some gaps in important areas
    - 70-74: AVERAGE - Meets basic requirements, some relevant experience, few achievements, several gaps in key areas
    - 65-69: BELOW AVERAGE - Meets some requirements, limited relevant experience, minimal achievements, significant gaps
    - 60-64: POOR - Meets few requirements, little relevant experience, no notable achievements, major gaps
    - Below 60: VERY POOR - Fails to meet most requirements, irrelevant experience, substantial gaps

    --- EVALUATION FRAMEWORK ---

    1. KEYWORD MATCHING & ATS COMPATIBILITY (Weight: 25%):
    - Analyze hard skills match (technical skills, tools, software, certifications)
    - Evaluate soft skills match (leadership, communication, teamwork, problem-solving)
    - Check industry keywords and sector-specific terminology
    - Assess job title alignment with current/previous roles
    - Consider keyword density and natural integration

    2. EXPERIENCE RELEVANCE (Weight: 25%):
    - Evaluate role similarity and how closely previous roles match requirements
    - Assess industry experience and relevant background
    - Review responsibility alignment with job functions
    - Analyze career progression and growth trajectory
    - Consider years of experience in specific areas

    3. QUALIFICATIONS & REQUIREMENTS (Weight: 20%):
    - Compare education requirements (degree level, field of study, certifications)
    - Evaluate required experience levels in specific areas
    - Check must-have skills (non-negotiable technical or soft skills)
    - Assess preferred qualifications (nice-to-have items)
    - Review professional certifications and licenses

    4. RESUME QUALITY & PRESENTATION (Weight: 15%):
    - Evaluate formatting, structure, and professional layout
    - Assess content quality, clarity, and action-oriented descriptions
    - Check for quantified achievements (metrics, numbers, percentages)
    - Review grammar, spelling, and professional writing quality
    - Consider overall readability and organization

    5. ACHIEVEMENT & IMPACT DEMONSTRATION (Weight: 15%):
    - Look for quantified results (revenue growth, cost savings, efficiency improvements)
    - Evaluate leadership examples and team management experience
    - Assess problem-solving capabilities with specific examples
    - Review career achievements, awards, recognitions, and promotions
    - Consider scope and scale of accomplishments
"""
